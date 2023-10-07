from libs import logger, config, wlan
from libs.cron import feed_wdt, pause_wdt, restart_wdt
import urequests as requests
import json
import gc
from time import ticks_ms, ticks_diff
from libs.sensors import measures
gauges = measures.copy()
gc.enable()

def send_data(d):
    gc.collect()
    gc.mem_free()
    feed_wdt()
    if type(d) is type(gauges):
        d = '[' + json.dumps(d) + ']'
    msg = None
    attempts = 2
    while attempts > 0:
        attempts -= 1
        try:
            start_request_time = ticks_ms()
            # hope there will be a better way than disabling WDT
            pause_wdt()
            durl = config.datalogger['URL'] + 'measurements/'
            resp = requests.post(durl, headers={'X-API-Key':config.datalogger['apikey'],'content-type': 'application/json'}, data=d, timeout=config.board['WDT_seconds']-3)
            msg = resp.text
            resp.close()
            restart_wdt()
            feed_wdt()
            request_time = 'POST request time: ' + str(ticks_diff(ticks_ms(),start_request_time)) + ' ms'
            logger.info(request_time)
            try:
                # converting to integer (we assume that the server replies
                # with the new record IDs if ALL of the inserts succeded.
                # An error message otherwise.
                one_reply = msg[1:-1].split(',')[0]
                int(one_reply)
                logger.info(msg)
                return True
            except (ValueError, AttributeError):
                log_message = 'server response: ' + msg
                logger.warning(log_message)
        except (Exception,OSError) as exceptz:
            logger.warning(exceptz)
            logger.warning('post request failed.')
            # here we could try to restore network connection before proceding
            wlan.turn_off()
            wlan.connect()
        finally:
            try:
                resp.close()
            except NameError:
                pass
#            try:
#                del resp
#            except KeyError:
#                pass
    return False

def send_opensensemap_data(d):
    gc.collect()
    gc.mem_free()
    feed_wdt()
    if type(d) is type(gauges):
        d = '[\n' + format_json_opensensemap(d) + '\n]'
    msg = None
    attempts = 2
    while attempts > 0:
        attempts -= 1
        try:
            start_request_time = ticks_ms()
            # hope there will be a better way than disabling WDT
            pause_wdt()
            durl = config.datalogger['opensensemap_API_URL'] + config.datalogger['senseBox_ID'] + '/data'
            resp = requests.post(durl, headers={'Authorization': config.datalogger['opensensemap_token'],'content-type': 'application/json'}, data=d, timeout=config.board['WDT_seconds']-3)
            msg = resp.text
            resp.close()
            restart_wdt()
            feed_wdt()
            request_time = 'Opensensemap POST request time: ' + str(ticks_diff(ticks_ms(),start_request_time)) + ' ms'
            logger.info(request_time)
            if msg == '"Measurements saved in box"':
                logger.info(msg)
                return True
            else:
                log_message = 'server response: ' + msg
                logger.warning(log_message)
        except (Exception,OSError) as exceptz:
            logger.warning(exceptz)
            logger.warning('Opensensemap post request failed.')
            # here we could try to restore network connection before proceding
            wlan.turn_off()
            wlan.connect()
        finally:
            try:
                resp.close()
            except NameError:
                pass
#            try:
#                del resp
#            except KeyError:
#                pass
    return False

def fill_gauges_dict(values):
    global gauges
    keys = [k for k in gauges.keys()]
    count = 0
    for v in values:
        gauges[keys[count]] = v
        count += 1

def send_data_list(measures_list):
    if len(measures_list) == 0:
        return True
    json_payload = '['
    for di in measures_list:
        fill_gauges_dict(di)
        json_payload += json.dumps(gauges)
        json_payload += ','
    json_payload = json_payload[:-1] + ']'
    dl_results = send_data(json_payload)
    return dl_results

def format_json_opensensemap(data_dict):
    if config.station['rover']:
        jsdata = f'{{"sensor":"{config.datalogger["temperature_ID"]}", "value":"{data_dict["temperature"]}", "createdAt": "{data_dict["datetime"]}", "location": [{data_dict["longitude"]},{data_dict["latitude"]},{config.station["rover_sensor_height_above_ground"]}]}},\n'
        jsdata += f'{{"sensor":"{config.datalogger["humidity_ID"]}", "value":"{data_dict["humidity"]}", "createdAt": "{data_dict["datetime"]}", "location": [{data_dict["longitude"]},{data_dict["latitude"]},{config.station["rover_sensor_height_above_ground"]}]}},\n'
        jsdata += f'{{"sensor":"{config.datalogger["pm2.5_ID"]}", "value":"{data_dict["pm2.5"]}", "createdAt": "{data_dict["datetime"]}", "location": [{data_dict["longitude"]},{data_dict["latitude"]},{config.station["rover_sensor_height_above_ground"]}]}}'
    else:
        jsdata = f'{{"sensor":"{config.datalogger["temperature_ID"]}", "value":"{data_dict["temperature"]}", "createdAt": "{data_dict["datetime"]}"}},\n'
        jsdata += f'{{"sensor":"{config.datalogger["humidity_ID"]}", "value":"{data_dict["humidity"]}", "createdAt": "{data_dict["datetime"]}"}},\n'
        jsdata += f'{{"sensor":"{config.datalogger["pm2.5_ID"]}", "value":"{data_dict["pm2.5"]}", "createdAt": "{data_dict["datetime"]}"}}'
    return jsdata
    
def send_opensensemap_data_list(measures_list):
    if len(measures_list) == 0:
        return True
    json_payload = '[\n'
    for di in measures_list:
        fill_gauges_dict(di)
        json_payload += format_json_opensensemap(gauges)
        json_payload += ',\n'
    json_payload = json_payload[:-2] + '\n]'
    dl_results = send_opensensemap_data(json_payload)
    return dl_results

def attempts():
    # three times the measurements per day takes account of failed sending attempts and night break 
    times = config.cron['measurements_per_day'] * 3 / ( (10 * 3600 * 24) / config.cron['data_submission_interval'])
    # round up
    return int(times + 1)
