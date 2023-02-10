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


# logger.info('start measurements')
# seconds = 120
# datafile = 'data.txt'
# import time
# while seconds > 0:
#     m = pm_sensor.measure()
#     time.sleep(1)
#     seconds -= 1
#     try:
#         with open(datafile, 'a') as f:
#             f.write(str(m["mass_density"]))
#     except:
#         print("Could not write file: ", datafile)
# logger.info('end measurements')
