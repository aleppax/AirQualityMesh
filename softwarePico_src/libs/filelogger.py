from libs import logger, config
from os import listdir
from libs.cron import feed_wdt

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
                for line in fr:
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

def write_remaining_data():
    global lines
    feed_wdt()
    # write the lines that could not be sent, if any.
    wrote_lines = 0
    try:
        with open(config.filelogger['filename'], 'w') as fw:
            # if lines is empty, it should write an empty file
            #unsent = [(';'.join(str(el) for el in linunsent) + '\n') for linunsent in unsent]
            #lines += unsent
            for lin in lines:
                fw.write(lin)
                wrote_lines += 1
            msg_wrote = 'wrote back ' + str(wrote_lines) + ' lines'
            logger.info(msg_wrote)
    except Exception as e:
        exc_msg = "Could not write file: " + config.filelogger['filename']
        logger.error(exc_msg)
        logger.error(e)
    return wrote_lines

def file_exists(fileURI):
    _splitted = config.filelogger['filename'].split('/')
    _log_path = '/'.join(_splitted[:-1])+'/'
    return _splitted[-1] in listdir(_log_path)
