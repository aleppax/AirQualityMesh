from libs import config, cron, leadacid, logger, picosngcja5, sps30, wlan,
import gc
# init logger
logger.info('booting')
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
#init pm sensor
#pm_sensor_p = picosngcja5.SNGCJA5(i2c) # Panasonic SNGCJA5
#pm_sensor_s = sps30.SPS30()
while True:
    print('waking up')
    # init network
    online = wlan.initialize()
    # if online save data online, otherwise to file
    # init RTC
    print('free memory: ' + str(gc.mem_free()))
    if online:
        cron.initialize()

    wlan.turn_off()
    print('going to sleep')
    cron.doLightSleep(5)


