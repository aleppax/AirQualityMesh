from libs import config, cron, filelogger, logger, sensors, wlan, output_mqtt, output_db
from libs import leadacid, sps30, picosngcja5, ahtx0, bmp280
from time import ticks_diff, ticks_ms, sleep_ms
from secrets import secrets
#from libs.mqtt_as import MQTTClient
#from libs.mqtt_local import config_mqtt
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import time


# Define blinking function for onboard LED to indicate error codes    
# def blink_onboard_led(num_blinks):
#     led = machine.Pin('LED', machine.Pin.OUT)
#     for i in range(num_blinks):
#         led.on()
#         time.sleep(.2)
#         led.off()
#         time.sleep(.2)


mqtt_server = '192.168.1.5'
client_id = 'PicoWeather'
user_t = 'pico'
password_t = 'picopassword'
topic_pub_temp = 'topic/temp'
topic_pub_humi = 'topic/humi'

ast_message = 0
message_interval = 5
counter = 0

# init logger
logger.info('booting')
logger.check_fs_free_space()
#init I2C and GPIO. access a port with gpio['GP2']
i2c, i2c_1, gpio = config.initialize_board2()
print('JMP00')
sensors.init2(i2c,i2c_1, gpio)
#th_s = ahtx0.AHT10(i2c) # AHT20 temperature humidity sensor
time.sleep(0.1)
print('JMP0')
#bm_b = bmp280.BMP280(i2c, addr=0x77, use_case = bmp280.BMP280_CASE_WEATHER) # Bosh BMP280 pressure temperature sensor
#bm_b.oversample(bmp280.BMP280_OS_HIGH)
time.sleep(0.1)
print("\nTemperature: %0.2f C" % sensor.temperature)
#print("Humidity: %0.2f %%" % sensor.relative_humidity)
print('JMP1')
logger.info('I2C active, now sensor init')
#sensors.init(i2c, gpio)
sensors.init2(i2c,i2c_1, gpio)
logger.info('JMP2, sensor init done')
sensor_preheating = config.cron['sensor_preheating_s']*1000
connection_max_time = config.wlan['connection_timeout']*1000
wlan.initialize()
print('IP: ', wlan.wlan)
#wlan_status = wlan.status()
#blink_onboard_led(wlan_status)
#if wlan_status != 3:
#    raise RuntimeError('Wi-Fi connection failed')
#else:
#    print('Connected')
#    status = wlan.ifconfig()
#    print('ip = ' + status[0])
client_mqtt = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
client_mqtt.connect()
logger.info('mqtt connected')
logger.info('activate output')
#prova su mqtt .. .. torno a mqtt.simple
# if (config.scheduler['mqtt'] == 1):
#     logger.info('mqtt enabled')
#     client_mqtt = output_mqtt.init(i2c)
#     logger.info('init mqtt done')
#     print(client_mqtt)
#     output_mqtt.mqttpub_test(client_mqtt,'proviamo') #rr fake write
#     logger.info('mqtt sending')
#prova su db, ora va
# if (config.scheduler['rest_lettori'] == 1):
#     output_db.db_measure(wlan,'proviamo db') #rr fake write
#     logger.info('db sending')
#break here
exit()
#break here
while True:
    if cron.do_measure:
        sensors.wakeup()
        short_sleep = sensor_preheating - connection_max_time
#        cron.lightsleep_wrapper(short_sleep)
        logger.info('waking up')
        # init network
        start_extra_time = ticks_ms()
        extra_time_ms = ticks_diff(ticks_ms(),start_extra_time)
        still_to_wait = connection_max_time - extra_time_ms
        if still_to_wait > 0:
            sleep_ms(still_to_wait)
        #sensors measurements, they have been pre-heated for 30s
        sensors.measure(logger.now_DTF())
        sensors.shutdown()
        # if online, save data online, otherwise to file
        if wlan.initialize():
            #data submission to servers
            # load from file
            # send data
            output_mqtt.mqttpub('proviamo') #rr fake write
            logger.info("sending")
            #if submission is successful, reset file, otherwise write to file
        else:
            #store data to file
            logger.info("saving")
    # if online check if it's time to look for NTP and software updates
    if wlan.online():
        # a software upgrade starts only if an update is available
        print('non controllo update')
#        cron.updates()
#    wlan.turn_off()
    print('disabilito lightsleep')
    #cron.lightsleep_until_next_cycle()
    sleep_ms(30000)
