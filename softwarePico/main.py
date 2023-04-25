from libs import cron, datalogger, filelogger, logger, mqttlogger, sensors, wlan
from machine import reset, freq, mem32

reset_cause = mem32[0x40058008]
# https://github.com/orgs/micropython/discussions/10858#discussioncomment-5504000
# You'll get 0 for normal power on. 1 for watchdog and 2 for machine.reset.
logger.info('booting. Reset cause ' + str(reset_cause))
clock = 65000000
freq(clock)
logger.info('Clock speed set to ' + str(freq()))
#this test works also before initializing i2c and sensors
sensors.check_low_power()
# init system
logger.check_fs_free_space()
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = cron.initialize_board()
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
                cron.check_software_updates() # every update_interval
                cron.software_update()
        wlan.turn_off()
        if cron.check_ntp_schedule():
            logger.info("Failed to update the clock. Rebooting.")
            cron.lightsleep_wrapper(180000)
            reset()

def send_values():
    done = False # current measures sent or saved somewhere
    if cron.check_data_schedule():
        # connect to wifi only if sending data is scheduled
        if wlan.initialize():
            # submission of stored data to servers
            attempts = datalogger.attempts()
            while attempts > 0:
                attempts -= 1
                file_lines = filelogger.read()
                if len(file_lines) == 0:
                    break
                sent = datalogger.send_data_list(file_lines)
                # success in submission of data, log also to mqtt and clead data
                # pass to mqtt logger lines that have been sent
                # sent_lines = [ln for ln in file_lines if sent[file_lines.index(ln)] is True]
                not_sent = [li for li in file_lines if sent[file_lines.index(li)] is False]
                # TODO: sent_mqtt could be used to keep records that can't be sent
                # sent_mqtt = mqttlogger.send_data_list(sent_lines)
                filelogger.keep_data(not_sent)
            #current data submission to servers
            done = datalogger.send_data(sensors.measures)
            if done:
                cron.update_last_data_sent()
                mqttlogger.send_data(sensors.measures)
        wlan.turn_off()
    attempts = 3
    while not done:
        attempts -= 1
        if attempts == 0:
            logger.error('current measurements cannot be saved. They will be lost.')
            return
        done = filelogger.write(sensors.measures)

while True:
    # before anything that could change the reading
    sensors.measure_battery()
    # check if it's time to look for NTP or software updates
    updates()
    # if a measurement is scheduled during this wake cycle, do the job
    if cron.do_measure:
        sensors.wakeup()
        # sleep while sensors preheat
        cron.lightsleep_wrapper(cron.preheat_time())
        sensors.measure(logger.now_DTF())
        send_values()
    # a way to exit the while cycle if power is low
    sensors.check_low_power()
    # otherwise work done, rest until next task
    cron.lightsleep_until_next_cycle()
