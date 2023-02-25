from libs import logger, config
from libs.sensors import empty_measures
from os import remove

def write(m):
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
    os.remove(config.filelogger['filename'])    

def fill_measures_dict(values):
    measures = empty_measures
    keys = [k for k in measures.keys()]
    count = 0
    for v in values:
        measures[keys[count]] = v
        count += 1
    return measures
