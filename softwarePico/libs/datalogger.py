from libs import logger, config
from libs.cron import feed_wdt
import urequests as requests
from machine import unique_id
import binascii

iam = unique_id()
UID = str(int(binascii.hexlify(iam).decode('utf-8')[-8:],16))

def send_data(d):
    feed_wdt()
    try:
        resp = requests.post(config.datalogger['URL'], json=d, timeout=config.board['WDT_seconds']-0.2)
        logger.info(resp.content)
    except OSError:
        feed_wdt()
        return False
    feed_wdt()
    isInt = True
    try:
        # converting to integer (we assume that the server replies
        # with the new record ID if the insert succeded. An error message otherwise.
        int(resp.content)
    except ValueError:
        isInt = False
    return isInt

def send_data_list(l):
    result = True
    for d in l:
        result &= send_data(d)
    if result == False:
        logger.warning("Couldn't reach datalogging URL")
    return result

def send_to_feinstaub_API(d_f):
    f_headers = {
    'Content-Type' : 'application/json',
    "X-Pin": "1",
    "X-Sensor": "raspicow-" + UID
    }
    f_body = {
    "software_version": config.cron['current_version'], 
    "sensordatavalues": [
    {"value_type":"P1","value":"66.04"},
    {"value_type":"P2","value":"53.32"}
        ]
    }  

def send_to_opensensemap_API(d_o):
    o_headers = {
    'Content-Type' : 'application/json',
                }
