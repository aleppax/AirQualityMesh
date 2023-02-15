# system scheduler
import ntptime, os, mip, sys
from machine import RTC, lightsleep
from libs import logger, config
from time import mktime, sleep_ms
import urequests as requests

rtc = RTC()
logger.use_NTP(rtc)
ntptime.host = config.cron['NTP_server']
update_available = False
current_version = config.cron['current_version']

def initialize():
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
        else:
            logger.warning("can't check for new software versions")

def software_update():
    global config
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
        else:
            logger.error("Version upgrade incomplete! This can lead to instability.")

def doLightSleep(sleepSeconds):
    sleep_ms(100)
    lightsleep(sleepSeconds * 1000)
    sleep_ms(100)
