import os
from time import localtime
from libs import config

# stores tuples of records: timestamp = <1609459286>, NTP_synced = 0 / 1, message;
# usage: import logger
#        logger.info('booting')

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
    config.set('logger','lastlog',n)
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

def debug(message):
    if config.logger['loglevel'] >= 1:
        log(message,1)

def info(message):
    if config.logger['loglevel'] >= 2:
        log(message,2)
    
def warning(message):
    if config.logger['loglevel'] >= 3:
        log(message,3)
    
def error(message):
    if config.logger['loglevel'] >= 4:
        log(message,4)

def critical(message):
    if config.logger['loglevel'] >= 5:
        log(message,5)
    
def log(message, level = 0):
    if rtc == '':
        NTP_synced = 0
    else:
        if rtc.datetime()[0] == 2021:
            NTP_synced = 0
        else:
            NTP_synced = 1
    now = now_DTF()
    # print debug information
    if __debug__ & print_log:
        print(now + ' ' + str(message))
    if config.logger['enable_log']:
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
        except Exception:
            print("Could not write file: /logs/" + logfile)

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
    now = localtime()
    return timetuple_to_DTF(now)
