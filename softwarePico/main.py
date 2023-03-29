from libs import config, cron, datalogger, filelogger, logger, mqttlogger, sensors, wlan
from machine import reset

logger.info('booting')
#this test works also before initializing i2c and sensors
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
        wlan.turn_off()
        if cron.check_ntp_schedule():
            logger.info("An update of the clock is required, but the sistem can't do it now. Rebooting in 180s.")
            cron.lightsleep_wrapper(180000)
            reset()

def send_values():
    #stored data submission to servers
    while True:
        file_lines = filelogger.read()
        if file_lines == []:
            break
        done = datalogger.send_data_list(file_lines)
        if done:
            # success in submission of data, log also to mqtt and clead data
            mqttlogger.send_data_list(file_lines)
            filelogger.clear_data()
        else:
            break
    #current data submission to servers
    done = datalogger.send_data(sensors.measures)
    if done:
        # REST submission and mqtt are done together
        # but only REST delivery is guaranteed
        mqttlogger.send_data(sensors.measures)
    return done

while True:
     # check if it's time to look for NTP or software updates
    updates()  
    # if a measurement is scheduled during this wake cycle, do the job
    if cron.do_measure:
        sensors.wakeup()
        # sleep while sensors preheat
        cron.lightsleep_wrapper(config.cron['sensor_preheating_s']*1000)
        #sensors measurements with timestamp, they have been pre-heated for 30s
        sensors.measure(logger.now_DTF())
        sensors.shutdown()
        # check again if online, save data online, otherwise to file
        sent = False
        # connect to wifi only if sending data is cheduled
        submission_scheduled = cron.check_data_schedule()
        if submission_scheduled:
            if wlan.initialize():
                sent = send_values()
            wlan.turn_off()
        if sent:
            cron.update_last_data_sent()
        else:
            filelogger.write(sensors.measures)
    # we need a way to exit the while cycle if power is low
    sensors.check_low_power()
    # otherwise work done, rest until next task
    cron.lightsleep_until_next_cycle()


