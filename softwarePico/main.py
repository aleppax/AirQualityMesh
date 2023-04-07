from libs import config, cron, filelogger, logger, mqttlogger, sensors, wlan, datalogger
from time import ticks_diff, ticks_ms
from machine import reset

logger.info('booting')
#this test works also before initializing i2c and sensors
# if power is low, revert to deepsleep
# still we do not have an idea of when we are, but better than nothing
cron.restore_latest_timestamp()
sensors.check_low_power()
# init system
logger.check_fs_free_space()
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
sensors.init(i2c, gpio)

def updates():
    # connect to wifi only if updates are required
    ntp_scheduled = cron.check_ntp_schedule()
    update_scheduled = cron.check_software_schedule()
    if (ntp_scheduled or update_scheduled):
        if wlan.initialize():
            if ntp_scheduled:
                cron.update_ntp() # every NTPsync_interval
            if update_scheduled:
                if not cron.update_available:
                    cron.check_software_updates() # every update_interval
                cron.software_update()
        else:
            logger.info("An update is required, but the sistem can't connect. Rebooting in 60s.")
            cron.lightsleep_wrapper(60000)
            reset()
        wlan.turn_off()

def send_values():
    #stored data submission to servers
    done = datalogger.send_data_list(filelogger.read())
    if done:
        # success in submission of data, log also to mqtt and clead data
        mqttlogger.send_data_list(filelogger.read())
        filelogger.clear_data()
    #current data submission to servers
    done = datalogger.send_data(sensors.measures)
    if done:
        # REST submission and mqtt are done together
        # but only REST delivery is guaranteed
        mqttlogger.send_data(sensors.measures)
    return done


###########
#rr prova rapida
sensors.wakeup()
sensors.measure(logger.now_DTF())
print(sensors.measures)
if wlan.initialize():
    mqttlogger.send_data(sensors.measures)
    wlan.turn_off()
    print('published')
###########

# while True:
#     # first thing, check if network is reachable
#     if wlan.initialize():
#         # check if it's time to look for NTP and software updates
#         cron.updates()
#         wlan.turn_off()
#     # if a measurement is scheduled during this wake cycle, do the job
#     if cron.do_measure:
#         sensors.wakeup()
#         # sleep while sensors preheat
#         cron.lightsleep_wrapper(config.cron['sensor_preheating_s']*1000)
#         #sensors measurements with timestamp, they have been pre-heated for 30s
#         sensors.measure(logger.now_DTF())
#         sensors.shutdown()
#         # check again if online, save data online, otherwise to file
#         sent = False
#         if wlan.initialize():
#             sent = send_values()
#             wlan.turn_off()
#         if not sent:
#             filelogger.write(sensors.measures)
#     # we need a way to exit the while cycle if power is low
#     sensors.check_low_power()
#     # otherwise work done, rest until next task
#     cron.lightsleep_until_next_cycle()
# 

