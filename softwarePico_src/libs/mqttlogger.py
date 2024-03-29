from libs import config
from libs.cron import feed_wdt
from libs.simple import MQTTClient
import ubinascii
import gc
import machine
from libs.sensors import measures
from time import sleep_ms

client_ID = ubinascii.hexlify(machine.unique_id())
server = config.mqttlogger['server']
main_topic = config.mqttlogger['topic']
mqtt_user = config.mqttlogger['user']
mqtt_password = config.mqttlogger['pass']
mqtt_QOS = config.mqttlogger['QOS']
mqtt_max_keepalive = config.board['WDT_seconds']-1
mqtt_gauges = measures.copy()

c = MQTTClient(client_ID, server, user=mqtt_user, password=mqtt_password, keepalive=mqtt_max_keepalive )

def fill_measures_dict(values):
    global mqtt_gauges
    keys = [k for k in mqtt_gauges.keys()]
    count = 0
    for v in values:
        mqtt_gauges[keys[count]] = v
        count += 1

def send_data(d):
    if config.mqttlogger['enable']:
        feed_wdt()
        try:
            c.connect()
        except Exception:
            return False
        for measure_key, measure_value in d.items():
            if measure_key not in ['station','datetime']:
                if measure_value != 0:
                    feed_wdt()
                    # topic levels: main_topic(opms) / key
                    topic = main_topic + measure_key
                    # publish relies on socket and expects bytes
                    c.publish(topic, bytes(str(measure_value),'utf-8'), qos=mqtt_QOS)
        c.disconnect()
        return True
    return False

def send_data_list(mqtt_measure_list):
    mqttl_results = []
    for d in mqtt_measure_list:
        gc.collect()
        fill_measures_dict(d)
        mqttl_results.append(send_data(mqtt_gauges))
        sleep_ms(10)
    return mqttl_results
