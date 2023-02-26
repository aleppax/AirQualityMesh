# system scheduler
import ntptime, os, mip, sys
from machine import RTC, lightsleep, mem32
from micropython import const
from math import fmod
from libs import logger, config
from time import sleep_ms
from random import randint
from machine import WDT
wdt_ms = config.board['WDT_seconds']*1000

debug = 1  #RR put it in config 
if debug == 1
    wdt = 'fake'
    def wdt.feed():
        wdt = 'fake'
else 
    wdt = WDT(timeout=wdt_ms)

rtc = RTC()
logger.use_NTP(rtc)
server_n = randint(0,config.cron['NTP_server_count']-1)
ntptime.host = str(server_n) + '.' + config.cron['NTP_server']
update_available = False
full_update = False
current_version = config.cron['current_version']
measurement_interval = round(86400 / config.cron['measuremens_per_day'])
minimum_sleep_s = config.cron['minimum_sleep_s']
sensor_preheating_s = config.cron['sensor_preheating_s']
do_measure = False
updated_NTP_at_boot = False
BASE = const(0x40058000)
_MASK = const(0x40000000)

#set
def enable_WdT():
    mem32[BASE + 0x2000] = _MASK

#clear
def disable_WdT():
    mem32[BASE + 0x3000] = _MASK

def sleep_ms_feeded(t):
    wdt.feed()
    mod = fmod(t,wdt_ms-500)
    times = int(t/wdt_ms-500)
    for i in range(times):
        sleep_ms(wdt_ms-500)
        wdt.feed()
    sleep_ms(int(mod))
    wdt.feed()
    
def updates():
    update_ntp() # every NTPsync_interval
    if not update_available:
        check_software_updates() # every update_interval
    software_update()
    
def update_ntp():
    global config, updated_NTP_at_boot
    wdt.feed()
    rtc_now = ntptime.time()
    if (updated_NTP_at_boot == False) or (config.cron['last_NTPsync'] == 0) or (rtc_now - config.cron['last_NTPsync'] > config.cron['NTPsync_interval']):
        logger.info('Using NTP server ' + ntptime.host)
        try:
            ntptime.settime()
            config = config.add('cron','last_NTPsync',ntptime.time())
            updated_NTP_at_boot = True
        except OverflowError as error:
            logger.error(error)
        except Exception as exception:
            logger.warning(exception)


def check_software_updates():
    global config, update_available, full_update
    # an extremely simple implementation:
    # it compares the current version number (int) with the online repo
    # and assuming that a network connection is up,
    # downloads version.py from the root of the repository/branch
    wdt.feed()
    rtc_now = ntptime.time()
    if rtc_now - config.cron['last_update'] > config.cron['update_interval']:
        if 'version.py' in os.listdir():
            os.remove('version.py')
        try:
            mip.install(config.cron['repository'] + 'version.py', target="/", version=config.cron['branch'])
        except:
            logger.warning("can't communicate with update server")
        wdt.feed()
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
                config = config.add('cron','last_update',rtc_now)
        else:
            logger.warning("can't check for new software versions")

def software_update():
    global config, update_available, full_update
    wdt.feed()
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
                filemodified = os.stat(directory + '/' + f)[7]
                mip.install(config.cron['repository'] + directory[1:] + '/' + f, target=directory + '/', version=config.cron['branch'])
                wdt.feed()
                if filemodified == os.stat(directory + '/' + f)[7]:
                    success = False
                    logger.warning("Problem updating file " + directory + '/' + f)
        # now update local version number
        if success:
            wdt.feed()
            config = config.add('cron','current_version',version.version)
            logger.info("Version upgrade done! Upgraded to version " + str(version.version))
            update_available = False
        else:
            logger.error("Version upgrade incomplete! This can lead to instability.")
            # TODO: maybe restoring the previus version could be a good idea...

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
        else:    
            do_measure = True
        return next_cycle_in_s

def lightsleep_wrapper(ms):
    logger.info('lightsleeping for ' + str(ms) + 'ms')
    disable_WdT()
    sleep_ms(100)
    lightsleep(ms - 200)
    enable_WdT()
    wdt.feed()
    sleep_ms(100)
    
    
def lightsleep_until_next_cycle():
    sleepSeconds = next_cycle_s() - sensor_preheating_s
    if sleepSeconds > minimum_sleep_s:
        lightsleep_wrapper(sleepSeconds*1000)
    
