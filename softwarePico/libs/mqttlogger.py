from libs import wlan, logger , config
from libs.cron import wdt
from umqtt.simple import MQTTClient
from time import localtime

#RR TODO value from config
mqtt_server = '192.168.1.5'
client_id = 'PicoWeather'
user_t = 'pico'
password_t = 'picopassword'

ast_message = 0
message_interval = 5
counter = 0

# config?  per ora no
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

def init(client):
    wdt.feed()
    global client_mqtt
    client_mqtt = client
#    client_mqtt = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
#    client_mqtt.connect()
#    time.sleep(3)
    wdt.feed()
    logger.info('mqtt connected')

def mqtt_connect():
    client = MQTTClient(client_id, mqtt_server, user=user_t, password=password_t, keepalive=60)
    client.connect()
    print('Connected to %s MQTT Broker'%(mqtt_server))
    return client

def reconnect():
    print('Failed to connected to MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()
    
    
def mqttpub_test(client, txt):
    wdt.feed()
    yr, mo, md, h, m, s, wd = localtime()[:7]
    fst = '{} {:02d}:{:02d}:{:02d} on {:02d}/{:02d}/{:02d}'
    print(fst.format(txt, h, m, s, md, mo, yr))
    logger.info('dentro mqtt TEST' + txt)
    t, h = 11.1, 22.2 #measures['temperature'], measures['humidity']
    print(t)
    print(h)
    temp = str(t)
    arrayt = ['{', '"temperature": ' , temp , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    client_mqtt.publish('topic/temp', msg)
    print('published')
    return 0
   

def mqttpub_measures(measures,txt):
    wdt.feed()
    yr, mo, md, h, m, s, wd = localtime()[:7]
    fst = '{} {:02d}:{:02d}:{:02d} on {:02d}/{:02d}/{:02d}'
    print(fst.format(txt, h, m, s, md, mo, yr))
    logger.info(txt + fst.format(txt, h, m, s, md, mo, yr))

    t, h = measures['temperature'], measures['humidity']
    #t, h = 11.1, 22.2
    #print(t)
    #print(h)

    temp = str(t)
    # If WiFi is down the following will pause for the duration.
    arrayt = ['{', '"temperature": ' , temp , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    client_mqtt.publish('topic/temp', msg)
    
    humi = str(h)
    arrayt = ['{', '"humidity": ' , humi , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    client_mqtt.publish('topic/humi', msg)
    
    md_pm10,  md_pm2_5,  md_pm1_0 = measures['pm10'], measures['pm2.5'], measures['pm1.0']  # Panasonic SNGCJA5 PM sensor
    #md_pm1_0, md_pm2_5, md_pm10 = 111.1,128.9,222.2
    
    arrayt = ['{', '"mass_density_pm1_0": ' , str(md_pm1_0) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md1_0, text)
    
    arrayt = ['{', '"mass_density_pm2_5": ' , str(md_pm2_5) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md2_5, text)
    
    arrayt = ['{', '"mass_density_pm10": ' , str(md_pm10) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md10, text)

    md_pm10_ch2, md_pm2_5_ch2, md_pm4_0_ch2, md_pm1_0_ch2    = measures['pm10_ch2'], measures['pm2.5_ch2'], measures['pm4_ch2'], measures['pm1.0_ch2']  # Sensirion SPS30 PM sensor
    #md_pm1_0_ch2 = 555.567
    #md_pm2_5_ch2 = 777.567
    #md_pm4_0_ch2 = 234.567
    #md_pm10_ch2  = 999.567
    
    arrayt = ['{', '"mass_density_pm1_0_ch2": ' , str(md_pm1_0_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md1_0_ch2, text)
    
    arrayt = ['{', '"mass_density_pm2_5_ch2": ' , str(md_pm2_5_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md2_5_ch2, text)
    
    arrayt = ['{', '"mass_density_pm4_0_ch2": ' , str(md_pm4_0_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md4_0_ch2, text)
    
    arrayt = ['{', '"mass_density_pm10_ch2": ' , str(md_pm10_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    client_mqtt.publish(topic_pub_md10_ch2, text)
    
    logger.info('all published') 
    
    return 0