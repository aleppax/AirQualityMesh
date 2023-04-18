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
    try:
        # if resp takes too long to arrive,
        resp = requests.post(config.datalogger['URL'], json=d, timeout=config.board['WDT_seconds']-0.5)
        msg = resp.text
        resp.close()
        feed_wdt()
        sleep_ms(30)
        logger.info(msg)
    except Exception as e:
        print(e)
    except OSError:
        return False
    isInt = True
    try:
        # converting to integer (we assume that the server replies
        # with the new record ID if the insert succeded. An error message otherwise.
        int(msg)
    except (ValueError, AttributeError) as e:
        isInt = False
    return isInt

def fill_measures_dict(values):
    global gauges
    keys = [k for k in gauges.keys()]
    count = 0
    for v in values:
        gauges[keys[count]] = v
        count += 1

def send_data_list(l):
    results = []
    for di in l:
        fill_measures_dict(di)
        result = send_data(gauges)
        results.append(result)
        sleep_ms(10)
    return results

def attempts():
    # twice the measurements per day takes account of failed sending attempts
    times = config.cron['measuremens_per_day'] * 2 / ( (10 * 3600 * 24) / config.cron['data_submission_interval'])
    # round up
    return int(times + 1)
