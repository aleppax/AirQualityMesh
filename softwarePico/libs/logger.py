import time
import os
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

logfile = config.logger['logfile']
filesize_limit_byte = config.logger['filesize_limit_byte']
rtc = ''
NTP_synced = 0
print_log = config.logger['print_log'] # False will disable printing log messages
# log levels: critical, error, warning, info, debug, notset

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
        timestamp = time.time()
        now = time.localtime()
        NTP_synced = 0
    else:
        timestamp = rtc.time_s()
        now = rtc.time()
        NTP_synced = 1
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
        print('logfile reached size of ' + os.stat(logfile)[6] + 'bytes. Limit is ' + filesize_limit_byte + ' bytes')
        return
        # TODO: purge older records
    # write to file
    try:
        with open(logfile, 'a') as f:
            f.write(logrecord)
    except:
        print("Could not write file: ", logfile) # there's no way to log this one!

def timetuple_to_DTF(timet,timezone='UTC'):
    # W3C-DTF, a subset of ISO8601 used also for HTTP headers
    # arguments:
    # timet = (year, month, day, weekday, hour, min, sec, unused)
    # timezone, except for UTC, must be expressed in the format: '+02:00'
    if timezone == 'UTC':
        timezone = 'Z'
    # if ms are missing, add an element to the tuple
    if len(timet) == 8:
        timet = timet + (0,)
    if len(timet) != 9:
        print('tuple length is not 9')
    Tyear, Tmonth, Tday, Tweekday, Thour, Tmin, Tsec, Tyearday, Tms = (timet)
    Tdateandtime = "{}/{}/{}T{}:{}:{}{}"
    return Tdateandtime.format(Tyear, Tmonth, Tday, Thour, Tmin, Tsec, timezone)

        
