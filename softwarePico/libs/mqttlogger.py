from libs import logger, config
from libs.cron import wdt
from libs.simple import MQTTClient
import ubinascii
import machine

client_ID = ubinascii.hexlify(machine.unique_id())
server = config.mqttlogger['server']
main_topic = config.mqttlogger['topic']
mqtt_user = config.mqttlogger['user']
mqtt_password = config.mqttlogger['pass']
mqtt_QOS = config.mqttlogger['QOS']

#c = MQTTClient(client_ID, server, user=mqtt_user, password=mqtt_password)
c = MQTTClient('2', server, user=mqtt_user, password=mqtt_password)

def send_data(d):
    if config.mqttlogger['enable']:
        wdt.feed()
        c.connect()
        for measure_key, measure_value in d.items():
            if measure_key not in ['station','datetime']:
                if measure_value != 0:
                    wdt.feed()
                    # topic levels: main_topic(opms) / station number / measured value
                    # topic = main_topic + str(config.station['station']) + '/' + measure_key
                    topic = main_topic + measure_key
                    c.publish(topic, str(measure_value), qos=mqtt_QOS)
                    #??c.publish(topic, str.encode(str(measure_value)), qos=mqtt_QOS)
                    # se invece si volesse usare il formato json
                    #  arrayt = ['{ "', str(measure_key) , '": ' , str(measure_value) , '}' ]
                    #  msg = ' '.join(arrayt)
                    #  print (msg)
                    #c.publish(topic, msg, qos=mqtt_QOS)
        c.disconnect()
        return True
    return False

def send_data_list(l):
    result = True
    for d in l:
        result &= send_data(d)
    return result
