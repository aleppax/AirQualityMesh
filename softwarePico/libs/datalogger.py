from libs import logger, config
from libs.cron import feed_wdt
import urequests as requests

def send_data(d):
    feed_wdt()
    resp = requests.post(config.datalogger['URL'], json=d)
    logger.info(resp.content)
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
    return result
