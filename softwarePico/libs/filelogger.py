from libs import logger, config
from os import remove, listdir
from libs.cron import feed_wdt

lines = []

def write(m):
    logger.info("data can't be sent. Saving locally")
    feed_wdt()
    # convert single set of measures m to csv, doesn't check the order or number of items
    csv_m = ';'.join(str(el) for el in m.values()) + '\n'
    # write to file
    try:
        with open(config.filelogger['filename'], 'a+') as fa:
            fa.write(csv_m)
        return True
    except:
        logger.error("Could not write file: " + config.filelogger['filename'])
        return False
    
def read():
    global lines
    feed_wdt()
    # retrieve all sets of measures in a list of ordered dicts
    csvdata = []
    if file_exists(config.filelogger['filename']):
        lines = []
        try:
            with open(config.filelogger['filename'], 'r') as fr:
                count = 5
                for line in fr.readlines():
                    count -= 1
                    if count < 0:
                        lines.append(line)
                        continue
                    raw_line = line.rstrip('\n').split(';')
                    csvdata.append(raw_line)
        except Exception as e:
            logger.error("Could not read file: " + config.filelogger['filename'])
            print(e)
    return csvdata

def clear_data():
    global lines
    #delete lines
    feed_wdt()
    try:
        with open(config.filelogger['filename'], 'w') as fw:
            for lain in lines:
                fw.write(lain)
    except Exception as e:
        print("Could not write file: ", config.filelogger['filename'])
        print(e)

def file_exists(fileURI):
    _splitted = config.filelogger['filename'].split('/')
    _log_path = '/'.join(_splitted[:-1])+'/'
    return _splitted[-1] in listdir(_log_path)
