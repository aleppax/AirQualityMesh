from libs import logger, config
from libs.cron import wdt
import urequests as requests

def send_data(d):
    resp = requests.post(config.datalogger['URL'], json=d)
    logger.info(resp.content)
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
