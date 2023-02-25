from libs.mqtt_as import MQTTClient
from libs.mqtt_local import config_mqtt
import uasyncio as asyncio
from libs import logger


def init(i2c, client_mqtt):
    print(i2c)  #RR ma qui non serve 
    global client
    client= client_mqtt


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
    print(client)
    client.publish('topic/temp', msg)
    
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
    await client.publish('topic/temp', msg)
    
    humi = str(h)
    arrayt = ['{', '"humidity": ' , humi , '}' ]
    msg = ' '.join(arrayt)
    print (msg)
    await client.publish('topic/humi', msg)
    
    #md_pm1_0, md_pm2_5, md_pm10 = measures['md_pm1_0'], measures['md_pm1_0'], measures['md_pm1_0'],  #RRR decidere i nomi
    md_pm1_0, md_pm2_5, md_pm10 = 111.1,128.9,222.2
    
    arrayt = ['{', '"mass_density_pm1_0": ' , str(md_pm1_0) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md1_0, text)
    
    arrayt = ['{', '"mass_density_pm2_5": ' , str(md_pm2_5) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md2_5, text)
    
    arrayt = ['{', '"mass_density_pm10": ' , str(md_pm10) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md10, text)

    #md_pm1_0_ch2, md_pm2_5_ch2, md_pm4_0_ch2, md_pm10_ch2 = measures['md_pm1_0'], measures['md_pm1_0'], measures['md_pm1_0'],  #RRR decidere i nomi
    
    pm1_0_ch2 = 555.567
    pm2_5_ch2 = 777.567
    pm4_0_ch2 = 234.567
    pm10_ch2  = 999.567
    
    arrayt = ['{', '"mass_density_pm1_0_ch2": ' , str(md_pm1_0_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md1_0_ch2, text)
    
    arrayt = ['{', '"mass_density_pm2_5_ch2": ' , str(md_pm2_5_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md2_5_ch2, text)
    
    arrayt = ['{', '"mass_density_pm4_0_ch2": ' , str(md_pm4_0_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md4_0_ch2, text)
    
    arrayt = ['{', '"mass_density_pm10_ch2": ' , str(md_pm10_ch2) , '}']
    text = ' '.join(arrayt)
    print (text)
    await client.publish(topic_pub_md10_ch2, text)
    
    return 0
