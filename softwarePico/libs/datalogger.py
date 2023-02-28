from libs import logger, config
from libs.cron import wdt
import urequests as requests

def send_data(d):
    resp = requests.post(config.datalogger['URL'], json=d)
    logger.info(resp.content)
    if type(resp.content) == int:
        return True
    else:
        return False

def send_data_list(l):
    for d in l:
        send_data(d)
    return True
