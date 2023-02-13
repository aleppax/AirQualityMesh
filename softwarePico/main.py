from libs import config, cron, leadacid, logger, picosngcja5, sps30, wlan,

# init logger
logger.info('booting')
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
#init pm sensor
#pm_sensor_p = picosngcja5.SNGCJA5(i2c) # Panasonic SNGCJA5
#pm_sensor_s = sps30.SPS30()
# init network
wlan.initialize()
# init RTC
cron.initialize()

