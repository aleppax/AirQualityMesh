from libs import config, cron, filelogger, logger, leadacid, sensors, wlan, datalogger
from time import ticks_diff, ticks_ms
from umqtt.simple import MQTTClient

# init logger
logger.info('booting')
logger.check_fs_free_space()
# checking for low power mode (battery saving)
if leadacid.config.leadacid['low_power_mode'] == True:
    from machine import deepsleep
    leadacid.levels()
    # maximum allowed sleep time, 71 minutes 33 seconds
    cron.deepsleep_as_long_as_you_can()
    
#init I2C and GPIO. access a port with gpio['GP2']
i2c, gpio = config.initialize_board()
sensors.init(i2c, gpio)
sensor_preheating = config.cron['sensor_preheating_s']*1000


###########
print(i2c)
sensors.wakeup()
print('calling measure')
sensors.measure(logger.now_DTF())
print(sensors.measures)

#RR TODO value from config
mqtt_server = '192.168.1.5'
client_id = 'PicoWeather'
user_t = 'pico'
password_t = 'picopassword'

# TODO spostare sotto nel loop main, chiedere hint ale
#prova su mqtt, ok usando mqtt.simple (no async enabled)
if (config.scheduler['mqtt'] == 1):
    from libs import mqttlogger
    client_mqtt_ok = 0
    if wlan.initialize():
        client_mqtt = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
        client_mqtt.connect()
        mqttlogger.init(client_mqtt)
        logger.info('mqtt enabled')
        client_mqtt_ok = 1
    else:
        logger.error('mqtt server MISSING')
    if  client_mqtt_ok == 1:
        mqttlogger.mqttpub_measures(sensors.measures,'proviamo mqtt') 
        logger.info('mqtt sent')
#prova su db, ora va  importante usare http 1.1  ogni tanto non risponde al primo giro , sto provando a risvegliarlo con un fake get
if (config.scheduler['rest_lettori'] == 1):
    from libs import dblogger
    if wlan.initialize():
        logger.info('db insert enabled')
        dblogger.dbget_station(wlan,'read station , dummy to wake up')
        print('test read done)')
        dblogger.dbpub_measures(sensors.measures,'proviamo db')
        logger.info('db sent')
    else:
        logger.error('WLAN  MISSING')

###simply break here
cron.disable_WdT()
exit()
###simply break here
###########

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
            logger.warning('TODO send to mqtt e db')
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
#        cron.updates()
        rr=0
    wlan.turn_off()
    if leadacid.config.leadacid['low_power_mode'] == True:
        logger.warning("Warning: Low battery level. Switching to low power mode until recharged")
        cron.deepsleep_as_long_as_you_can()
    cron.lightsleep_until_next_cycle()

