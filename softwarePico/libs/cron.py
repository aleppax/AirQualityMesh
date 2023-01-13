# system scheduler

from machine import RTC
from libs.ntp import Ntp
from libs import logger, config

def initialize():
    _rtc = RTC()
    Ntp.set_datetime_callback(_rtc.datetime)
    Ntp.set_hosts((config.cron['NTP_server_1'],config.cron['NTP_server_2']))
    Ntp.rtc_sync(epoch = config.cron['epoch'])
    logger.use_NTP(Ntp)
    
