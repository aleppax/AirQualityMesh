from libs import logger, config
from libs.sensors import empty_measures
from os import remove, listdir
from libs.cron import feed_wdt

def write(m):
    logger.info("data can't be sent. Saving locally")
    feed_wdt()
    # convert single set of measures m to csv, doesn't check the order or number of items
    csv_m = ';'.join(str(el) for el in m.values()) + '\n'
    # write to file
    try:
        with open(config.filelogger['filename'], 'a+') as f:
            f.write(csv_m)
        return True
    except:
        logger.error("Could not write file: " + config.filelogger['filename'])
        return False
    
def read():
    feed_wdt()
    # retrieve all sets of measures in a list of ordered dicts
    csvdata = []
    if file_exists(config.filelogger['filename']):
        try:
            with open(config.filelogger['filename'], 'r') as f:
                for line in f.readlines():
                    raw_line = line.rstrip('\n').split(';')
                    measures_dict = fill_measures_dict(raw_line)
                    csvdata.append(measures_dict)
            return csvdata
        except:
            logger.error("Could not read file: " + config.filelogger['filename'])
    return []

def clear_data():
    #delete file
    feed_wdt()
    if file_exists(config.filelogger['filename']):
        remove(config.filelogger['filename'])

def fill_measures_dict(values):
    measures = empty_measures
    keys = [k for k in measures.keys()]
    count = 0
    for v in values:
        measures[keys[count]] = v
        count += 1
    return measures

def file_exists(fileURI):
    _splitted = config.filelogger['filename'].split('/')
    _log_path = '/'.join(_splitted[:-1])+'/'
    return _splitted[-1] in listdir(_log_path)
