# system scheduler
import ntptime, os, mip, sys
from machine import RTC, lightsleep
from math import fmod, floor
from libs import logger, config
from time import mktime, sleep_ms, ticks_ms, ticks_diff
import urequests as requests

rtc = RTC()
logger.use_NTP(rtc)
ntptime.host = config.cron['NTP_server']
update_available = False
current_version = config.cron['current_version']
measurement_interval = round(86400 / config.cron['measuremens_per_day'])
logger.log('measurement_interval ' + str(measurement_interval))
minimum_sleep_s = config.cron['minimum_sleep_s']
sensor_preheating_s = config.cron['sensor_preheating_s']
do_measure = False

def updates():
    update_ntp() # every NTPsync_interval
    if not update_available:
        check_software_updates() # every update_interval
    
def update_ntp():
    global config
    rtc_now = mktime(rtc.datetime())
    if (config.cron['last_NTPsync'] == 0) or (rtc_now - config.cron['last_NTPsync'] > config.cron['NTPsync_interval']):
        ntptime.settime()
        ntp_nowness = rtc.datetime()
        config = config.add('cron','last_NTPsync',mktime(ntp_nowness))

def check_software_updates():
    global config
    # an extremely simple implementation:
    # it compares the current version number (int) with the online repo
    # and assuming that a network connection is up,
    # downloads version.py from the root of the repository/branch
    rtc_now = mktime(rtc.datetime())
    if rtc_now - config.cron['last_update'] > config.cron['update_interval']:
        global update_available
        if 'version.py' in os.listdir():
            os.remove('version.py')
        mip.install(config.cron['repository'] + 'version.py', target="/", version=config.cron['branch'])
        if 'version.py' in os.listdir():
            if 'version' in sys.modules:
                del sys.modules['version']
            import version
            if version.version > config.cron['current_version']:
                update_available = True
                logger.info('update found. Version ' + str(version.version))
            elif version.version == config.cron['current_version']:
                update_available = False
                config = config.add('cron','last_update',rtc_now)
        else:
            logger.warning("can't check for new software versions")

def software_update():
    global config, update_available
    if update_available:
        success = True
        # bring version in this scope
        import version
        # this script has many limitations: can't sync nested folders, does not delete old files or folders
        for folder in version.folders:
            if folder[1:] not in os.listdir() and folder != '/':
                os.mkdir(folder)
        for directory,files in version.updated_files.items():
            for f in files:
                filemodified = os.stat(directory + '/' + f)[7]
                mip.install(config.cron['repository'] + directory[1:] + '/' + f, target=directory + '/', version=config.cron['branch'])
                if filemodified == os.stat(directory + '/' + f)[7]:
                    success = False
                    logger.warning("Problem updating file " + directory + '/' + f)
        # now update local version number
        if success:
            config = config.add('cron','current_version',version.version)
            logger.info("Version upgrade done! Upgraded to version " + version.version)
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
    sleep_ms(100)
    lightsleep(ms - 200)
    sleep_ms(100)
    
def lightsleep_until_next_cycle():
    sleepSeconds = next_cycle_s() - sensor_preheating_s
    if sleepSeconds > minimum_sleep_s:
        lightsleep_wrapper(sleepSeconds*1000)
    

