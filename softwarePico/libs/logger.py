import time
import os
from time import gmtime, mktime
from libs import config

# stores tuples of records: timestamp = <1609459286>, NTP_synced = 0 / 1, event_index;
# 1000 log records use 16 Kb, 2 KB. RP2040 has 2MB of memory
# indexes are deduced from this list, you can add other log events:
# usage: import logger
#        logger.info('booting')
events = [
    'booting',   #0
    'rebooting', #1
    'unknown',   #2
    'Connected to wifi with an IP address',
    'No way to connect. Trying again in 20 seconds',
    'Wrong wifi credentials',
]

logfile_name = config.logger['logfile']
filesize_limit_byte = config.logger['filesize_limit_byte']
logfileCount = config.logger['logfileCount']
lastlog = config.logger['lastlog']
logNvalues = list(range(logfileCount))
rtc = ''
NTP_synced = 0
print_log = config.logger['print_log'] # False will disable printing log messages
# log levels: critical, error, warning, info, debug, notset

def nextLogFile():
    if lastlog == logfileCount -1:
        n = 0
    else:
        n = logNvalues[lastlog+1]
    updateLastlogConfig(n)
    return value

def updateLastlogConfig(n):
    global config, lastlog, logfile
    config = config.add('logger','lastlog',n)
    logfile = logfile_name + '.' + str(n)
    lastlog = n

def use_NTP(ntp):
    global rtc
    rtc = ntp

def debug(message):
    log(message,1)

def info(message):
    log(message,2)
    
def warning(message):
    log(message,3)
    
def error(message):
    log(message,4)

def critical(message):
    log(message,5)
    
def log(message, level = 0):
    #timestamp
    if rtc == '':
        NTP_synced = 0
    else:
        NTP_synced = 1
    timestamp = time.time()
    now = time.localtime()
    # parse message
    if message in events:
        index = events.index(message)
    else:
        index = 2 #unknown
    # print debug information
    if __debug__ & print_log:
        print(timetuple_to_DTF(now) + ' ' + message)
    # format log
    logformat = "{},{},{},{}\n"
    logrecord = logformat.format(str(timestamp),str(level),str(NTP_synced),str(index))
    # check file size
    if os.stat(logfile)[6] > filesize_limit_byte:
        nextLogFile()
    # write to file
    try:
        with open(logfile, 'a') as f:
            f.write(logrecord)
    except:
        print("Could not write file: ", logfile) # there's no way to log this one!

def timetuple_to_DTF(timet,timezone='UTC'):
    # W3C-DTF, a subset of ISO8601 used also for HTTP headers
    # arguments:
    # timet = time.localtime() (year, month, day, hour, min, sec, weekday, yearday)
    # timezone, except for UTC, must be expressed in the format: '+02:00'
    if timezone == 'UTC':
        timezone = 'Z'
    # if ms are missing, add an element to the tuple
    if len(timet) == 8:
        timet = timet + (0,)
    if len(timet) != 9:
        print('tuple length is not 9')
    Tyear, Tmonth, Tday, Thour, Tmin, Tsec, Tweekday, Tyearday, Tms = (timet)
    Tdateandtime = "{:02d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}{}"
    return Tdateandtime.format(Tyear, Tmonth, Tday, Thour, Tmin, Tsec, timezone)

def now_DTF():
    now = time.localtime()
    return timetuple_to_DTF(now)
