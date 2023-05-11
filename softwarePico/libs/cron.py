# system scheduler
import ntptime
import os
import mip
import sys
import urequests as requests
from machine import RTC, lightsleep, mem32, reset, WDT, deepsleep
from micropython import const
from math import fmod
from libs import logger, config
from time import sleep_ms, time, gmtime
from random import randint
wdt_ms = config.board['WDT_seconds']*1000
if config.cron['use_wdt']:
    wdt = WDT(timeout=wdt_ms)
    wdt_enabled = True
else:
    wdt_enabled = False
rtc = RTC()
logger.use_NTP(rtc)
server_n = randint(0,config.cron['NTP_server_count']-1)
ntptime.host = str(server_n) + '.' + config.cron['NTP_server']
update_available = False
full_update = False
current_version = config.cron['current_version']
measurement_interval = round(86400 / config.cron['measuremens_per_day'])
last_data_sent = 0
minimum_sleep_s = config.cron['minimum_sleep_s']
sensor_preheating_s = config.cron['sensor_preheating_s']
do_measure = False
last_NTPsync = 0
BASE = const(0x40058000)
_MASK = const(0x40000000)

#set
def enable_wdt():
    global wdt_enabled
    mem32[BASE + 0x2000] = _MASK
    wdt_enabled = True

#clear
def disable_wdt():
    global wdt_enabled
    mem32[BASE + 0x3000] = _MASK
    wdt_enabled = False

def feed_wdt():
    if wdt_enabled:
        wdt.feed()

def pause_wdt():
    if wdt_enabled:
        disable_WdT()

def restart_wdt():
    if config.cron['use_wdt']:
        enable_wdt()
    
def sleep_ms_feeded(t):
    feed_wdt()
    mod = fmod(t,wdt_ms-500)
    times = int(t/(wdt_ms-500))
    for i in range(times):
        sleep_ms(wdt_ms-500)
        feed_wdt()
    sleep_ms(int(mod))
    feed_wdt()

# derived from MicroPython package installer
# MIT license; Copyright (c) 2022 Jim Mussared
# added timeout
def download_file(url, dest, timeout):
    try:
        response = requests.get(url,timeout=timeout)
    except OSError:
        logger.warning('update connection timed out')
        return False
    try:
        if response.status_code != 200:
            response_error_msg = "Error " + str(response.status_code) + " requesting " + url
            logger.error(response_error_msg)
            return False

        copying_msg = "Copying:" + dest
        logger.info(copying_msg)
        mip._ensure_path_exists(dest)
        with open(dest, "wb") as f:
            mip._chunk(response.raw, f.write)

        return True
    finally:
        response.close()
    
def check_software_schedule():
    now = time()
    if now - config.cron['last_update_check'] > config.cron['update_interval']:
        return True
    else:
        return False

def check_data_schedule():
    now = rtc.datetime()
    if config.cron['data_submission_on_daylight'] and ((now[4] < config.cron['morning']) or (now[4] > config.cron['evening'])):
        return False
    if config.cron['data_submission_just_in_time']:
        return True
    now = time()
    if now - last_data_sent > config.cron['data_submission_interval']:
        return True
    else:
        return False

def check_ntp_schedule():
    feed_wdt()
    now = time()
    if now - last_NTPsync > config.cron['NTPsync_interval']:
        return True
    else:
        return False

def update_last_data_sent():
    global last_data_sent
    last_data_sent = time()

def update_ntp():
    global config, last_NTPsync
    feed_wdt()
    updated_NTP = False
    # this can lead to wdt intervention, a reboot is ok
    while not updated_NTP:
        feed_wdt()
        logger.info('Using NTP server ' + ntptime.host)
        try:
            ntptime.settime()
            last_NTPsync = time()
            updated_NTP = True
            break
        except OverflowError as error:
            logger.error(error)
        except Exception as exception:
            logger.warning(exception)
        logger.info('retrying NTP update in 4 seconds')
        sleep_ms_feeded(4000)


def check_software_updates():
    global config, update_available, full_update
    # an extremely simple implementation:
    # it compares the current version number (int) with the online repo
    # and assuming that a network connection is up,
    # downloads version.py from the root of the repository/branch
    feed_wdt()
    if not update_available:
        if 'version.py' in os.listdir():
            os.remove('version.py')
        try:
            download_file(config.cron['repository'] + '/version.py', dest="/version.py", timeout=config.board['WDT_seconds']-3)
        except Exception:
            logger.warning("can't communicate with update server")
            return
        feed_wdt()
        if 'version.py' in os.listdir():
            if 'version' in sys.modules:
                del sys.modules['version']
            import version
            if version.version > config.cron['current_version']:
                update_available = True
                # if updating more than one versioning step, fetch everything.
                if config.cron['current_version'] - version.version > 1:
                    full_update = True
                    logger.info('Updating from more than one versioning step, fetching everything.')
                logger.info('Going to update from version ' + str(config.cron['current_version']) + ' to version ' + str(version.version))
            elif version.version == config.cron['current_version']:
                update_available = False
            tt = time()
            config.set('cron','last_update_check',tt)
        else:
            logger.warning("can't check for new software versions")

def update_config():
    global config
    logger.info('updating config while preserving custom settings (hopefully...)')
    sleep_ms(1000)
    new_config = __import__('/libs/config')
    sgs = dict([(name, cls) for name, cls in new_config.__dict__.items() if isinstance(cls, dict)])
    for sg_name in sgs:
        for par in sgs[sg_name]:
            # if already exists, and is different, then restore the modified setting
            if par in config.__dict__[sg_name]:
                if sgs[sg_name][par] != config.__dict__[sg_name][par]:
                    # rewrite to file the pre-existing modified setting
                    feed_wdt()
                    msg = 'writing ' + str(sg_name) + ' ' + str(par) + ' ' + str(config.__dict__[sg_name][par])
                    logger.info(msg)
                    config.set(sg_name,par,config.__dict__[sg_name][par],do_reload=False)
            else:
                msg = 'writing ' + str(sg_name) + ' ' + str(par) + ' ' + str(sgs[sg_name][par])
                logger.info(msg)
                config.set(sg_name,par,sgs[sg_name][par],do_reload=False)

def software_update():
    global config, update_available, full_update
    feed_wdt()
    if update_available:
        success = True
        # bring version in this scope
        import version
        # this script does not delete old files or folders
        for folder in version.folders:
            if folder[1:] not in os.listdir() and folder != '/':
                os.mkdir(folder)
        if full_update:
            filedict = version.all_files
        else:
            filedict = version.updated_files
        for directory,files in filedict.items():
            for f in files:
                # if file didn't exixt, of course don't check for new timestamp
                existed = f in os.listdir()
                if existed:
                    filemodified = os.stat(directory + '/' + f)[7]
                else:
                    filemodified = -1
                if (f == 'config.py') and (directory == '/libs/'):
                    os.rename('/libs/config.py','/libs/configold.py')
                download_file(config.cron['repository'] + directory[1:] + f, dest=directory + f, timeout=config.board['WDT_seconds']-2)
                if (f == 'config.py') and (directory == '/libs/'):
                    update_config()
                feed_wdt()
                if filemodified == os.stat(directory + '/' + f)[7]:
                    success = False
                    logger.warning("Problem updating file " + directory + '/' + f)
        # now update local version number
        if success:
            feed_wdt()
            config.set('cron','current_version',version.version)
            logger.info("Version upgrade done! Upgraded to version " + str(version.version))
            update_available = False
            sleep_ms(1000)
            # rebooting
            reset()
        else:
            logger.error("Version upgrade incomplete! This can lead to instability.")
            # TODO: having space left, maybe restoring the previus version could be a good idea...

def next_cycle_s():
    # returns how long to lightsleep
    global do_measure
    now = rtc.datetime()
    time_since_midnight = now[4]*3600 + now[5]*60 + now[6] # there will be some misalignment every day at midnight
    next_cycle_in_s = int(measurement_interval - fmod(time_since_midnight,measurement_interval)) # seconds. calculates when should occur the first feasible measurement in the future
    # max RP2040 sleep time seems to be 2^32-1us or 4294966ms or 4294s or 71min33s
    # if next_measurement_in_s is higher than max sleep time go to sleep for max time without measuring anything
    if next_cycle_in_s > 4294:
        do_measure = False
        return 4294
    else:
        # if there is not enough time to turn on sensors before measurement, skipping this measurement
        if next_cycle_in_s < minimum_sleep_s + sensor_preheating_s:
            do_measure = False
            logger.warning('skipping measurement, not enough time to preheat sensors')
            sleep_ms_feeded(next_cycle_in_s*1000)
        else:    
            do_measure = True
        return next_cycle_in_s

def timetuple_to_rtctuple(t):
    return (t[0],t[1],t[2],t[6],t[3],t[4],t[5],0)

def restore_latest_timestamp():
    global config
    if config.cron['deepsleep_reset']:
        latest = gmtime(config.cron['latest_timestamp']+4294)
        rtc.datetime(timetuple_to_rtctuple(latest))
        config.set('cron','deepsleep_reset',False)

def store_latest_timestamp():
    global config
    now = time()
    config.set('cron','latest_timestamp',now)
    config.set('cron','deepsleep_reset',True)

def preheat_time():
    return config.cron['sensor_preheating_s']*1000

def initialize_board():
    return config.initialize_board()

def lightsleep_wrapper(ms):
    if config.cron['use_wdt']:
        logger.info('lightsleeping for ' + str(ms/1000) + ' s')
        disable_wdt()
        sleep_ms(500)
        lightsleep(ms - 1000)
        enable_wdt()
        feed_wdt()
        sleep_ms(500)
        print('') # realigning REPL communication, even if not used
    else:    
        logger.info('lightsleeping for ' + str(ms/1000) + ' s, WDT unused')
        sleep_ms(500)
        lightsleep(ms - 1000)
        sleep_ms(500)
        print('') #
    
def lightsleep_until_next_cycle():
    sleepSeconds = next_cycle_s() - sensor_preheating_s
    if sleepSeconds > minimum_sleep_s:
        lightsleep_wrapper(sleepSeconds*1000)
    
def deepsleep_as_long_as_you_can():
    restore_latest_timestamp()
    store_latest_timestamp()
    logger.info('deepsleeping for 71min33s')
    disable_wdt()
    sleep_ms(100)
    deepsleep(4294000)
