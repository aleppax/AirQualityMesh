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


c = (
"\033[0m",       # reset#
"\033[30m",      # Black #
"\033[31m",      # Red #
"\033[32m",      # Green #
"\033[33m",      # Yellow #
"\033[34m",      # Blue #
"\033[35m",      # Magenta #
"\033[36m",      # Cyan #
"\033[37m",      # White #
)

logfile_name = config.logger['logfile']
filesize_limit_byte = config.logger['filesize_limit_byte']
logfileCount = config.logger['logfileCount']
lastlog = config.logger['lastlog']
logfile = logfile_name + '.' + str(lastlog)
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

def updateLastlogConfig(n):
    global config, lastlog, logfile
    config = config.add('logger','lastlog',n)
    logfile = logfile_name + '.' + str(n)
    lastlog = n
    if logfile in os.listdir('/logs'):
        os.remove('/logs/' + logfile)

def check_fs_free_space():
    fs_stat = os.statvfs('/')
    fs_size = fs_stat[0] * fs_stat[2]/1024
    fs_free = fs_stat[0] * fs_stat[3]/1024
    info("File System Size {:,}KB - Free Space {:,}KB".format(fs_size, fs_free))

def use_NTP(ntp):
    global rtc
    rtc = ntp

    
c = (
"\033[0m",       # reset#
"\033[30m",      # Black #
"\033[31m",      # Red #
"\033[32m",      # Green #
"\033[33m",      # Yellow #
"\033[34m",      # Blue #
"\033[35m",      # Magenta #
"\033[36m",      # Cyan #
"\033[37m",      # White #
)

def debug(message):
    log(c[0]+message+c[0],1)

def info(message):
    log(c[3]+message+c[0],2)
    
def warning(message):
    log(c[4]+message+c[0],3)
    
def error(message):
    log(c[2]+message+c[0],4)

def critical(message):
    log(c[5]+message+c[0],5)
    
def log(message, level = 0):
    #timestamp
    if rtc == '':
        NTP_synced = 0
    else:
        NTP_synced = 1

    now = now_DTF()
    # parse message
    if str(message) in events:
        index = events.index(str(message))
    else:
        index = 2 #unknown
    # print debug information
    if __debug__ & print_log:
        print(now + ' ' + str(message))
    # format log TODO: replace timestamp with more readable DTF
    logformat = "{},{},{},{}\n"
    logrecord = logformat.format(now,str(level),str(NTP_synced),str(message))
    # check file size
    if logfile in os.listdir('/logs'):
        if os.stat('/logs/' + logfile)[6] > filesize_limit_byte:
            nextLogFile()
    # write to file
    try:
        with open('/logs/' + logfile, 'a+') as f:
            f.write(logrecord)
    except:
        print("Could not write file: /logs/" + logfile) # there's no way to log this one!

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
