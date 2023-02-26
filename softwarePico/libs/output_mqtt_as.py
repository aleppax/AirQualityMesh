from libs.mqtt_as import MQTTClient
from libs.mqtt_as import config_mqtt
import machine
import network
import urequests as requests
import ujson
import utime
from secrets import secrets 
from time import localtime
from libs import logger

# Local configuration
config_mqtt['ssid'] = secrets['ssid']
config_mqtt['wifi_pw'] = secrets['pw']
config_mqtt['user'] = 'pico'
config_mqtt['password'] = 'picopassword'
config_mqtt['server'] = '192.168.1.5'  # Change to suit e.g. 'iot.eclipse.org'
config_mqtt['client_id'] = 'PicoWeather'

topic_pub_temp = 'topic/temp'
topic_pub_humi = 'topic/humi'
topic_pub_md1_0 = 'topic/md_pm1_0'
topic_pub_md2_5 = 'topic/md_pm2_5'
topic_pub_md10  = 'topic/md_pm10'
topic_pub_md1_0_ch2 = 'topic/md_pm1_0_ch2'
topic_pub_md2_5_ch2 = 'topic/md_pm2_5_ch2'
topic_pub_md4_0_ch2 = 'topic/md_pm4_0_ch2'
topic_pub_md10_ch2  = 'topic/md_pm10_ch2'

TOPIC = 'topic/info'  # For demo publication and last will use same topic

# Define configuration
config_mqtt['will'] = (TOPIC, 'Goodbye cruel world!', False, 0)
config_mqtt['keepalive'] = 120
config_mqtt["queue_len"] = 1  # Use event interface


def init(i2c, client_mqtt):
    print(i2c)  #RR ma qui non serve 
    global client
    client= client_mqtt


def blink_onboard_led(txt):
    num_blinks=2
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)

def messages(client):  # Respond to incoming messages
    for topic, msg, retained in client.queue:
        print((topic, msg, retained))

def up(client):  # Respond to connectivity being (re)established
    while True:
        client.up.wait()  # Wait on an Event
        client.up.clear()
        client.subscribe('foo_topic', 1)  # renew subscriptions


#async def mqttpub(txt):
def mqttpub_test(client,txt):
    logger.info('dentro mqtt ' + txt)
    t, h = 11.1, 22.2 #measures['temperature'], measures['humidity']
    print(t)
    print(h)
    temp = str(t)
    arrayt = ['{', '"temperature": ' , temp , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    client.publish('topic/temp', msg)
    print('published')
    return 0
    
def mqttpub(client,txt):
    logger.info('dentro mqtt ' + txt)
    t, h = 11.1, 22.2 #measures['temperature'], measures['humidity']
    print(t)
    print(h)
#   await asyncio.sleep(5)
    temp = str(t)
    # If WiFi is down the following will pause for the duration.
    arrayt = ['{', '"temperature": ' , temp , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    client.publish('topic/temp', msg)
    
    humi = str(h)
    arrayt = ['{', '"humidity": ' , humi , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    client.publish('topic/humi', msg)
    
    #md_pm1_0, md_pm2_5, md_pm10 = measures['md_pm1_0'], measures['md_pm1_0'], measures['md_pm1_0'],  #RRR decidere i nomi
    md_pm1_0, md_pm2_5, md_pm10 = 111.1,128.9,222.2
    
    arrayt = ['{', '"mass_density_pm1_0": ' , str(md_pm1_0) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md1_0, text)
    
    arrayt = ['{', '"mass_density_pm2_5": ' , str(md_pm2_5) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md2_5, text)
    
    arrayt = ['{', '"mass_density_pm10": ' , str(md_pm10) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md10, text)

    #md_pm1_0_ch2, md_pm2_5_ch2, md_pm4_0_ch2, md_pm10_ch2 = measures['md_pm1_0'], measures['md_pm1_0'], measures['md_pm1_0'],  #RRR decidere i nomi
    
    pm1_0_ch2 = 555.567
    pm2_5_ch2 = 777.567
    pm4_0_ch2 = 234.567
    pm10_ch2  = 999.567
    
    arrayt = ['{', '"mass_density_pm1_0_ch2": ' , str(md_pm1_0_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md1_0_ch2, text)
    
    arrayt = ['{', '"mass_density_pm2_5_ch2": ' , str(md_pm2_5_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md2_5_ch2, text)
    
    arrayt = ['{', '"mass_density_pm4_0_ch2": ' , str(md_pm4_0_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md4_0_ch2, text)
    
    arrayt = ['{', '"mass_density_pm10_ch2": ' , str(md_pm10_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client.publish(topic_pub_md10_ch2, text)
    
    return 0


def mqtt_connect():
    client = MQTTClient(config_mqtt)
#    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(config_mqtt['server']))
    return client

def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
    
    
MQTTClient.DEBUG = True  
#client_mqtt = MQTTClient(config_mqtt)
#client_mqtt.connect()
try:
    client = mqtt_connect()
except OSError as e:
    reconnect()
#run test here
# rp2.country('IT')
# wlan = network.WLAN(network.STA_IF)
# wlan.active(True)
# ssid = secrets['ssid']
# pw = secrets['pw']
# wlan.connect(ssid, pw)
#print(wlan)
mqttpub_test(client,'prova')