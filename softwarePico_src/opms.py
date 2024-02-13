from libs import cron, datalogger, filelogger, logger, mqttlogger, sensors, wlan
from machine import reset, freq, mem32
import micropython

# cron could also be named 'core'
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

def updates_rover():
    # fetch datetime from GNSS, do not attempt any software update
    if sensors.update_gnss_time():
        return
    logger.info("Failed to update the clock via satellite. Trying via mobile hotspot and NTP.")
    if wlan.connect():
        cron.update_ntp()
    if cron.check_ntp_schedule():
        logger.info("Failed to update the clock. Rebooting.")
        cron.lightsleep_wrapper(20000)
        reset()

def send_values():
    opms_logged = filelogger.write_opms(sensors.measures) # current measures immediately saved to file
    # if using opensensemap, write current measures also to specific file queue
    if datalogger.opensensemap_enable:
        opensensemap_logged = filelogger.write_opensensemap(sensors.measures)
    if cron.check_data_schedule(sensors.battery_values[2],sensors.leadacid.min_charging_voltage):
        # connect to wifi only if sending data is scheduled
        if wlan.connect():
            # submission of stored data to servers
            attempts = datalogger.attempts()
            while attempts > 0:
                attempts -= 1
                opms_file_lines = filelogger.read_opms()
                if len(opms_file_lines) != 0:
                    if datalogger.send_data_list(opms_file_lines):
                        filelogger.write_remaining_opms_data()
                if datalogger.opensensemap_enable:
                    opensensemap_file_lines = filelogger.read_opensensemap()
                    if len(opensensemap_file_lines) != 0:
                        if datalogger.send_opensensemap_data_list(opensensemap_file_lines):
                            filelogger.write_remaining_opensensemap_data()
            #if errors occurred, try to submit current data to remote servers
            if not opms_logged:
                opms_logged = datalogger.send_data(sensors.measures)
            if datalogger.opensensemap_enable:
                if not opensensemap_logged:
                    opensensemap_logged = datalogger.send_opensensemap_data(sensors.measures)
            if opms_logged:
                cron.update_last_data_sent()
                mqttlogger.send_data(sensors.measures)
            else:
                opms_logged = filelogger.write_measures(sensors.measures,config.filelogger['filename'])
        wlan.turn_off()
    # retry writing to file
    if not opms_logged:
        opms_logged = filelogger.write_measures(sensors.measures,config.filelogger['filename'])
    if datalogger.opensensemap_enable:
        if not opensensemap_logged:
            opensensemap_logged = filelogger.write_measures(sensors.measures,config.filelogger['opensensemap_filename'])
    if not opms_logged:
        logger.error('current measures cannot be saved or sent to OPMS server.')
    if datalogger.opensensemap_enable:
        if not opensensemap_logged:
            logger.error('current measures cannot be saved or sent to OpenSenseMap API server.')


if cron.is_rover():
    sensors.measure_battery()
    sensors.wakeup()
    updates_rover()
    cron.lightsleep_wrapper(cron.preheat_time())
    while True:
        # uses GP1 as digital input. Bistable switch, enables moving and recording
        if not gpio['GP1'].value():
            cron.lightsleep_wrapper(10000)
            continue
        # set roving to True (either digital pin or communicate status, rover can start/continue his path)
        cron.enable_roving()
        # locate GNSS position and refine
            # if no fix: infer
            # if fix: store lat lon
        # compare position with latest record
            # if distance < interval distance: wait, goto locate GNSS
            # if distance > interval distance: continue
        # set roving to False (rover should stop in a safe spot)
        cron.disable_roving()
        # measure serie, average and store/send
        sensors.measure(logger.now_DTF())
        send_values()
        sensors.check_low_power()
else:
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
