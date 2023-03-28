from libs import logger, config
from libs.cron import feed_wdt
import urequests as requests
from machine import unique_id
import binascii, gc
from time import sleep_ms
from libs.sensors import measures
gauges = measures.copy()
iam = unique_id()
UID = str(int(binascii.hexlify(iam).decode('utf-8'),16))

def send_data(d):
    feed_wdt()
    gc.collect()
    try:
        # if resp takes too long to arrive,
        resp = requests.post(config.datalogger['URL'], json=d, timeout=config.board['WDT_seconds']-0.5)
        sleep_ms(30)
        logger.info(resp.text)
    except Exception as e:
        print(e)
    except OSError:
        feed_wdt()
        return False
    feed_wdt()
    isInt = True
    try:
        # converting to integer (we assume that the server replies
        # with the new record ID if the insert succeded. An error message otherwise.
        int(resp.text)
    except ValueError:
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
    result = True
    for di in l:
        gc.collect()
        fill_measures_dict(di)
        result &= send_data(gauges)
        sleep_ms(100)
    if result == False:
        logger.warning("Couldn't reach datalogging URL")
    del l
    return result
