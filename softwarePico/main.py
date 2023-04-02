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
    submission_scheduled = cron.check_data_schedule()
    if submission_scheduled:
        # connect to wifi only if sending data is scheduled
        if wlan.initialize():
            # submission of stored data to servers
            attempts = 3
            while attempts > 0:
                attempts -= 1
                file_lines = filelogger.read()
                if file_lines == []:
                    break
                sent = datalogger.send_data_list(file_lines)
                # pass to mqtt logger the lines that have been sent by datalogger
                sent_lines = [l for l in file_lines if sent[file_lines.index(l)] == True]
                sent_mqtt = mqttlogger.send_data_list(sent_lines)
                filelogger.clear_data(sent)
            #current data submission to servers
            done = datalogger.send_data(sensors.measures)
            if done:
                mqttlogger.send_data(sensors.measures)
                cron.update_last_data_sent()
            else:
                filelogger.write(sensors.measures)
        wlan.turn_off()
    else:
        filelogger.write(sensors.measures)

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
        send_values()
    # we need a way to exit the while cycle if power is low
    sensors.check_low_power()
    # otherwise work done, rest until next task
    cron.lightsleep_until_next_cycle()


