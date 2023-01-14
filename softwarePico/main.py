from machine import Pin, I2C
from libs import config, cron, leadacid, logger, picosngcja5, wlan


#init I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
#init pm sensor
pm_sensor = picosngcja5.SNGCJA5(i2c)
# TODO: wait at least 28 seconds before measuring pm
# init logger
logger.info('booting')
# init network
wlan.initialize()
# init RTC
cron.initialize()


