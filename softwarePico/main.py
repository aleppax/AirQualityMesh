import machine
from libs.ntp import Ntp
from libs import config, logger, wlan

# init logger
logger.info('booting')
# init network
wlan.initialize()

# init RTC
_rtc = machine.RTC()
Ntp.set_datetime_callback(_rtc.datetime)
Ntp.set_hosts(('pool.ntp.org','it.pool.ntp.org'))
Ntp.rtc_sync(epoch = 1)
logger.use_NTP(Ntp)
