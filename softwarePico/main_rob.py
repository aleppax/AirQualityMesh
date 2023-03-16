from libs import config, cron, filelogger, logger, mqttlogger, sensors, wlan, datalogger
from time import ticks_diff, ticks_ms, sleep
import machine
from machine import lightsleep, Pin

led = machine.Pin('LED', machine.Pin.OUT)
i = 0
while (i<5):
    led.on()
    sleep(.2)
    led.off()
    sleep(.2)
    i = i + 1
logger.info('booting')
#this test works also before initializing i2c and sensors
# if power is low, revert to deepsleep
# still we do not have an idea of when we are, but better than nothing
#cron.restore_latest_timestamp()
#sensors.check_low_power()
# init system
logger.check_fs_free_space()
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
sensors.init(i2c, gpio)

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
led = machine.Pin('LED', machine.Pin.OUT)
i = 0
while (i<5):
    led.on()
    sleep(.2)
    led.off()
    sleep(.2)
    i = i + 1
    
while True:
    sensors.wakeup()
    sensors.measure(logger.now_DTF())
    print(sensors.measures)
    if wlan.initialize():
        sleep(2)
        print('mqtt')
        mqttlogger.send_data(sensors.measures)
        print('published')
#         wlan.turn_off()
#         print('spento wifi')
        #do the magic
        wlan.wlan.disconnect()
        wlan.wlan.active(False)
        wlan.wlan.deinit()    #spegnere chip wifi
        sleep(.1)
        wlan.wlan=None
        print('spento  wlan')
        sleep(.1)
        i = 0
        while (i<10):
            led.on()
            sleep(.2)
            led.off()
            sleep(.2)
            i = i + 1
        ############
        lightsleep(300000)
        print('uscito lightsleep')
        ############
        i = 0
        while (i<10):
            led.on()
            sleep(.5)
            led.off()
            sleep(.5)
            i = i + 1
###########
# 
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
# 
