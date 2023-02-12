from libs import config, cron, leadacid, logger, picosngcja5, wlan

# init logger
logger.info('booting')
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
#init pm sensor
#pm_sensor = picosngcja5.SNGCJA5(i2c)
# init network
wlan.initialize()
# init RTC
cron.initialize()

