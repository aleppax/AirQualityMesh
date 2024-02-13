from libs import logger, config
from os import listdir
from libs.cron import feed_wdt

lines_opms_queue = []
lines_opensensemap_queue = []

def write(m,filename):
    written = False
    logger.info("Saving locally to data queue.")
    feed_wdt()
    # write to file
    written = write_measures(m,filename)
    return written
    
def write_opms(m):
    return write(m,config.filelogger['filename'])
    
def write_opensensemap(m):
    return write(m,config.filelogger['opensensemap_filename'])
    
def write_measures(csv_measures,fname):
    # convert to csv, doesn't check the order or number of items
    csv_m = ';'.join(str(el) for el in csv_measures.values()) + '\n'
    try:
        with open(fname, 'a+') as fa:
            fa.write(csv_m)
        return True
    except Exception:
        logger.error("Could not write file: " + fname)
        return False

def read_opms():
    return read_measures(config.filelogger['filename'])

def read_opensensemap():
    return read_measures(config.filelogger['opensensemap_filename'])

def read_measures(fname):
    if file_exists(fname):
        csvdata = []
        lines = []
        try:
            with open(fname, 'r') as fr:
                count = config.filelogger['measurements_per_sending']
                for line in fr:
                    count -= 1
                    if count < 0:
                        lines.append(line)
                        continue
                    raw_line = line.rstrip('\n').split(';')
                    csvdata.append(raw_line)
                if fname == config.filelogger['filename']:
                    global lines_opms_queue
                    lines_opms_queue = lines
                if fname == config.filelogger['opensensemap_filename']:
                    global lines_opensensemap_queue
                    lines_opensensemap_queue = lines
                msg_count = 'retrieved ' + str(len(csvdata)) + ' lines from ' + fname + '. keeping aside ' + str(len(lines)) + ' lines.'
                if len(csvdata) > 0:
                    logger.info(msg_count)
        except Exception as e:
            logger.error("Could not read file: " + fname)
            logger.error(e)
        return csvdata
    else:
        logger.error("File doesn't exist: " + fname)
        return []

def write_remaining_opms_data():
    write_remaining_data(lines_opms_queue,config.filelogger['filename'])
    
def write_remaining_opensensemap_data():
    write_remaining_data(lines_opensensemap_queue,config.filelogger['opensensemap_filename'])

def write_remaining_data(lines_queue,fname):
    feed_wdt()
    # write the lines that could not be sent, if any.
    wrote_lines = 0
    try:
        with open(fname, 'w') as fw:
            # if lines is empty, it should write an empty file
            #unsent = [(';'.join(str(el) for el in linunsent) + '\n') for linunsent in unsent]
            #lines += unsent
            for lin in lines_queue:
                fw.write(lin)
                wrote_lines += 1
            msg_wrote = 'wrote back ' + str(wrote_lines) + ' lines'
            logger.info(msg_wrote)
    except Exception as e:
        exc_msg = "Could not write file: " + fname
        logger.error(exc_msg)
        logger.error(e)
    return wrote_lines

def file_exists(fileURI):
    _splitted = config.filelogger['filename'].split('/')
    _log_path = '/'.join(_splitted[:-1])+'/'
    return _splitted[-1] in listdir(_log_path)
