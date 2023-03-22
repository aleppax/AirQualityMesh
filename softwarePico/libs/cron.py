# system scheduler
import ntptime, os, mip, sys
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
def enable_WdT():
    global wdt_enabled
    mem32[BASE + 0x2000] = _MASK
    wdt_enabled = True

#clear
def disable_WdT():
    global wdt_enabled
    mem32[BASE + 0x3000] = _MASK
    wdt_enabled = False

def feed_wdt():
    if wdt_enabled:
        wdt.feed()

def sleep_ms_feeded(t):
    feed_wdt()
    mod = fmod(t,wdt_ms-500)
    times = int(t/(wdt_ms-500))
    for i in range(times):
        sleep_ms(wdt_ms-500)
        feed_wdt()
    sleep_ms(int(mod))
    feed_wdt()
    
def check_software_schedule():
    if time() - config.cron['last_update_check'] > config.cron['update_interval']:
        return True
    else:
        return False

def check_data_schedule():
    if config.cron['data_submission_just_in_time']:
        return True
    if time() - last_data_sent > config.cron['data_submission_interval']:
        return True
    else:
        return False

def check_ntp_schedule():
    if time() - last_NTPsync > config.cron['NTPsync_interval']:
        return True
    else:
        return False

def update_last_data_sent():
    global last_data_sent
    last_data_sent = time()

def update_ntp():
    global config, last_NTPsync
    feed_wdt()
    rtc_now = time()
    updated_NTP = False
    # this can lead to wdt intervention, a reboot is better than not knowing for sure the actual time 
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
    if 'version.py' in os.listdir():
        os.remove('version.py')
    try:
        mip.install(config.cron['repository'] + 'version.py', target="/", version=config.cron['branch'])
    except:
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
            logger.info('Going to update from version ' + str(config.cron['current_version']) + 'to version ' + str(version.version))
        elif version.version == config.cron['current_version']:
            update_available = False
        config = config.add('cron','last_update_check',time())
    else:
        logger.warning("can't check for new software versions")

def update_config():
    from libs import config as new_config
    # now dir of new_config content
    s = dir(new_config)
    for El in s:
        if El[:2] != '__':
            if type(El) == type({}):
                print(El)

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
                mip.install(config.cron['repository'] + directory[1:] + '/' + f, target=directory + '/', version=config.cron['branch'])
                if (f == 'config.py') and (directory == '/libs'):
                    update_config()
                feed_wdt()
                if filemodified == os.stat(directory + '/' + f)[7]:
                    success = False
                    logger.warning("Problem updating file " + directory + '/' + f)
        # now update local version number
        if success:
            feed_wdt()
            config = config.add('cron','current_version',version.version)
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
    logger.log('next_cycle_in_s ' + str(next_cycle_in_s))
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
        config = config.add('cron','deepsleep_reset',False)

def store_latest_timestamp():
    global config
    config = config.add('cron','latest_timestamp',time())
    config = config.add('cron','deepsleep_reset',True)

def lightsleep_wrapper(ms):
    if config.cron['use_wdt']:
        logger.info('lightsleeping for ' + str(ms) + 'ms')
        disable_WdT()
        sleep_ms(100)
        lightsleep(ms - 200)
        enable_WdT()
        feed_wdt()
        sleep_ms(100)
    else:    
        logger.info('lightsleeping for ' + str(ms) + 'ms, WDT unused')
        sleep_ms(100)
        lightsleep(ms - 200)
        sleep_ms(100)
    
def lightsleep_until_next_cycle():
    sleepSeconds = next_cycle_s() - sensor_preheating_s
    if sleepSeconds > minimum_sleep_s:
        lightsleep_wrapper(sleepSeconds*1000)
    
def deepsleep_as_long_as_you_can():
    restore_latest_timestamp()
    store_latest_timestamp()
    logger.info('deepsleeping for 71min33s')
    disable_WdT()
    sleep_ms(100)
    deepsleep(4294000)
