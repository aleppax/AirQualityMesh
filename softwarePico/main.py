from libs import config, cron, filelogger, logger, sensors, wlan, datalogger
from time import ticks_diff, ticks_ms

# init logger
logger.info('booting')
logger.check_fs_free_space()
# checking for low power mode (battery saving)
if config.leadacid['low_power_mode'] == True:
    from libs import leadacid
    from machine import deepsleep
    leadacid.levels()
    # maximum allowed sleep time, 71 minutes 33 seconds
    cron.deepsleep_as_long_as_you_can()
    
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
sensors.init(i2c, gpio)
sensor_preheating = config.cron['sensor_preheating_s']*1000

print(i2c)
sensors.wakeup()
print('ok wakeup')
sensors.measure(logger.now_DTF())
print(sensors.measures)

exit()

while True:
    if cron.do_measure:
        sensors.wakeup()
        cron.lightsleep_wrapper(sensor_preheating)
        #sensors measurements, they have been pre-heated for 30s
        sensors.measure(logger.now_DTF())
        sensors.shutdown()
        # if online, save data online, otherwise to file
        sent = False
        if wlan.initialize():
            sent = datalogger.send_data_list(filelogger.read())
            if sent:
                filelogger.clear_data()
            #data submission to servers
            # load from file
            datalogger.send_data(sensors.measures)
        if not sent:
            #store data to file
            logger.info("data can't be sent. Saving locally")
            filelogger.write(sensors.measures)
    # if online check if it's time to look for NTP and software updates
    if wlan.online():
        # a software upgrade starts only if an update is available
        cron.updates()
        rr=0
    wlan.turn_off()
    if config.leadacid['low_power_mode'] == True:
        logger.warning("Warning: Low battery level. Switching to low power mode until recharged")
        cron.deepsleep_as_long_as_you_can()
    cron.lightsleep_until_next_cycle()


