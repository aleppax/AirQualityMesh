# system scheduler
import ntptime
from machine import RTC
from libs import logger, config
from time import mktime
rtc = RTC()
logger.use_NTP(rtc)

def initialize():
    global config
    rtc_now = mktime(rtc.datetime())
    if (config.cron['last_NTPsync'] == 0) or (rtc_now - config.cron['last_NTPsync'] > config.cron['NTPsync_interval']):
        ntptime.settime()
        ntp_nowness = rtc.datetime()
        config = config.add('cron','last_NTPsync',mktime(ntp_nowness))

