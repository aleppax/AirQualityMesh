from libs import logger, config
from os import listdir
from libs.cron import feed_wdt
from time import sleep_ms

lines = []

def write(m):
    logger.info("Saving locally to data queue.")
    feed_wdt()
    # convert to csv, doesn't check the order or number of items
    csv_m = ';'.join(str(el) for el in m.values()) + '\n'
    # write to file
    try:
        with open(config.filelogger['filename'], 'a+') as fa:
            fa.write(csv_m)
        return True
    except Exception:
        logger.error("Could not write file: " + config.filelogger['filename'])
        return False
    
def read():
    global lines
    feed_wdt()
    # retrieve all sets of measures in a list
    csvdata = []
    if file_exists(config.filelogger['filename']):
        lines = []
        try:
            with open(config.filelogger['filename'], 'r') as fr:
                count = 10
                for line in fr.readlines():
                    count -= 1
                    if count < 0:
                        lines.append(line)
                        continue
                    raw_line = line.rstrip('\n').split(';')
                    csvdata.append(raw_line)
        except Exception as e:
            logger.error("Could not read file: " + config.filelogger['filename'])
            logger.error(e)
    msg_count = 'retrieved ' + str(len(csvdata)) + ' lines from ' + config.filelogger['filename'] + '. keeping aside ' + str(len(lines)) + ' lines.'
    if len(csvdata) > 0:
        logger.info(msg_count)
    else:
        logger.info('No more lines to be sent.')
    return csvdata

def keep_data(unsent):
    global lines
    feed_wdt()
    # write the lines that could not be sent, if any.
    try:
        with open(config.filelogger['filename'], 'w') as fw:
            # if lines is empty, it should write an empty file
            lines += unsent
            for lin in lines:
                fw.write(lin)
    except Exception as e:
        logger.error("Could not write file: ", config.filelogger['filename'])
        logger.error(e)
    sleep_ms(100)

def file_exists(fileURI):
    _splitted = config.filelogger['filename'].split('/')
    _log_path = '/'.join(_splitted[:-1])+'/'
    return _splitted[-1] in listdir(_log_path)
