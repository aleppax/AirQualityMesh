from libs import logger, config
from libs.cron import feed_wdt
import urequests as requests
from machine import unique_id
import binascii
from time import sleep_ms
from libs.sensors import measures
gauges = measures.copy()
iam = unique_id()
UID = str(int(binascii.hexlify(iam).decode('utf-8'),16))

def send_data(d):
    feed_wdt()
    msg = None
    attempts = 2
    while attempts > 0:
        attempts -= 1
        try:
            resp = requests.post(config.datalogger['URL'], json=d, timeout=config.board['WDT_seconds']-4)
            msg = resp.text
            resp.close()
            feed_wdt()
            try:
                # converting to integer (we assume that the server replies
                # with the new record ID if the insert succeded. An error message otherwise.
                int(msg)
                logger.info(msg)
                return True
            except (ValueError, AttributeError):
                log_message = 'server response: ' + msg
                logger.warning(log_message)
        except (Exception,OSError):
            logger.warning('post request failed.')
    return False


def fill_gauges_dict(values):
    global gauges
    keys = [k for k in gauges.keys()]
    count = 0
    for v in values:
        gauges[keys[count]] = v
        count += 1

def send_data_list(measures_list):
    results = []
    for di in measures_list:
        fill_gauges_dict(di)
        result = send_data(gauges)
        results.append(result)
        sleep_ms(10)
    return results

def attempts():
    # twice the measurements per day takes account of failed sending attempts
    times = config.cron['measuremens_per_day'] * 2 / ( (10 * 3600 * 24) / config.cron['data_submission_interval'])
    # round up
    return int(times + 1)
