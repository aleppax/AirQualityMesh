from libs import cron, datalogger, filelogger, logger, mqttlogger, sensors, wlan
from machine import reset, freq, mem32
import micropython

micropython.alloc_emergency_exception_buf(100)
reset_cause = mem32[0x40058008]
# https://github.com/orgs/micropython/discussions/10858#discussioncomment-5504000
# You'll get 0 for normal power on. 1 for watchdog and 2 for machine.reset.
logger.info('booting. Reset cause ' + str(reset_cause))
freq(65000000)
logger.info('Clock speed set to ' + str(freq()))
#this test works also before initializing i2c and sensors
sensors.check_low_power()
# init system
logger.check_fs_free_space()
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = cron.initialize_board()
sensors.init(i2c, gpio)

#button SW1 pressed at startup: entering configuration mode
if gpio['GP0'].value() is 1:
    wlan.serve_captive_portal()

def updates():
    # connect to wifi only if updates are required
    ntp_scheduled = cron.check_ntp_schedule()
    update_scheduled = cron.check_software_schedule()
    if (ntp_scheduled or update_scheduled):
        if wlan.connect():
            if ntp_scheduled:
                cron.update_ntp() # every NTPsync_interval
            if update_scheduled:
                cron.check_software_updates() # every update_interval
                cron.update_software()
        wlan.turn_off()
        if cron.check_ntp_schedule():
            logger.info("Failed to update the clock. Rebooting.")
            cron.lightsleep_wrapper(180000)
            reset()

def send_values():
    done = filelogger.write(sensors.measures) # current measures sent or saved somewhere
    if cron.check_data_schedule(sensors.battery_values[2],sensors.leadacid.min_charging_voltage):
        # connect to wifi only if sending data is scheduled
        if wlan.connect():
            # submission of stored data to servers
            attempts = datalogger.attempts()
            while attempts > 0:
                attempts -= 1
                file_lines = filelogger.read()
                if len(file_lines) == 0:
                    break
                if datalogger.send_data_list(file_lines):
                    filelogger.write_remaining_data()
            #current data submission to servers
            if not done:
                done = datalogger.send_data(sensors.measures)
            if done:
                cron.update_last_data_sent()
                mqttlogger.send_data(sensors.measures)
            else:
                done = filelogger.write(sensors.measures)  
        wlan.turn_off()
    if not done:
        done = filelogger.write(sensors.measures)
    if not done:
        logger.error('current measures cannot be saved.')


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
