import network
from secrets import secrets
import ubinascii
import time
from umqtt.simple import MQTTClient
from machine import Pin, I2C
import ujson
import utime
from time import localtime
from libs import logger

mqtt_server = '192.168.1.5'
client_id = 'PicoWeather'
user_t = 'pico'
password_t = 'picopassword'

# Load login data from different file for safety reasons
ssid = secrets['ssid']
pw = secrets['pw']

ast_message = 0
message_interval = 5
counter = 0

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


def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
    
    
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
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
    

#run test here
rp2.country('IT')
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
ssid = secrets['ssid']
pw = secrets['pw']
wlan.connect(ssid, pw)
print(wlan)
try:
    client = mqtt_connect()
except OSError as e:
    reconnect()
mqttpub_test(client,'prova')