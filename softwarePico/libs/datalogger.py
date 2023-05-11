from libs import logger, config
from libs.cron import feed_wdt, disable_WdT, enable_WdT
import urequests as requests
from machine import unique_id
import binascii
import json
from time import ticks_ms, ticks_diff, sleep_ms
from libs.sensors import measures
gauges = measures.copy()

def send_data(d):
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
            resp = requests.post(config.datalogger['URL'], data=d, timeout=config.board['WDT_seconds']-3)
            msg = resp.text
            resp.close()
            enable_wdt()
            feed_wdt()
            request_time = 'POST request time: ' + str(ticks_diff(ticks_ms(),start_request_time)) + ' ms'
            feed_wdt()
            logger.info(request_time)
            try:
                # converting to integer (we assume that the server replies
                # with the new record IDs if ALL of the inserts succeded.
                # An error message otherwise.
                one_reply = msg[1:].split(',')[0]
                if ']' in one_reply:
                    one_reply = one_reply[:-1]
                int(one_reply)
                logger.info(msg)
                return True
            except (ValueError, AttributeError):
                log_message = 'server response: ' + msg
                logger.warning(log_message)
        except (Exception,OSError):
            logger.warning('post request failed.')
            # here we could try to restore network connection before proceding
    return False

def fill_gauges_dict(values):
    global gauges
    keys = [k for k in gauges.keys()]
    count = 0
    for v in values:
        gauges[keys[count]] = v
        count += 1

def send_data_list(measures_list):
    json_payload = '['
    for di in measures_list:
        fill_gauges_dict(di)
        json_payload += json.dumps(gauges)
        json_payload += ','
    json_payload = json_payload[:-1] + ']'
    dl_results = send_data(json_payload)
    return dl_results

def attempts():
    # three times the measurements per day takes account of failed sending attempts and night break 
    times = config.cron['measuremens_per_day'] * 3 / ( (10 * 3600 * 24) / config.cron['data_submission_interval'])
    # round up
    return int(times + 1)
