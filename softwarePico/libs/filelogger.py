from libs import logger, config
from libs.sensors import empty_measures
from os import remove, listdir
from libs.cron import wdt

def write(m):
    logger.info("data can't be sent. Saving locally")
    wdt.feed()
    # convert single set of measures m to csv, doesn't check the order or number of items
    csv_m = ';'.join(str(el) for el in m.values()) + '\n'
    # write to file TODO: fix wrong file opening
    try:
        with open(config.filelogger['filename'], 'a+') as f:
            f.write(csv_m)
        return True
    except:
        logger.error("Could not write file: " + config.filelogger['filename'])
        return False
    
def read():
    wdt.feed()
    # retrieve all sets of measures in a list of ordered dicts
    csvdata = []
    try:
        with open(config.filelogger['filename'], 'r') as f:
            for line in f:
                raw_line = line.rstrip('\n').split(';')
                measures_dict = fill_measures_dict(values)
                csvdata.append(measures_dict)
        return csvdata
    except:
        logger.error("Could not read file: " + config.filelogger['filename'])
        return []

def clear_data():
    #delete file
    splitted = config.filelogger['filename'].split('/')
    log_path = '/'.join(splitted[:-1])+'/'
    if splitted[-1] in listdir(log_path):
        remove(config.filelogger['filename'])

def fill_measures_dict(values):
    measures = empty_measures
    keys = [k for k in measures.keys()]
    count = 0
    for v in values:
        measures[keys[count]] = v
        count += 1
    return measures
