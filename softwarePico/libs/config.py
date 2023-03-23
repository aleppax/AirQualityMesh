board = {
    'GPIO_out' : [2,3,4,5,6,7], # Even if you could, Do NOT add "LED" because it sucks (current)
    'GPIO_in' : [0,1],
    'I2C_BUS' : 0,
    'I2C_SDA' : 8,
    'I2C_SCL' : 9,
    'I2C_freq' : 100000,
    'WDT_seconds' : 8,
    'uln2003_1' : 'GP7', # hardware connections between Pico GPIOs and ULN2003 channels
    'uln2003_2' : 'GP6',
    'uln2003_3' : 'GP5',
    'uln2003_4' : 'GP4',
    'uln2003_5' : 'GP3',
    'uln2003_6' : 'GP2',
}
cron = {
    'NTP_server' : 'it.pool.ntp.org',
    'NTP_server_count' : 4,
    'NTPsync_interval' : 3600 * 4,
    # 'NTPsync_interval' every x hours
    'update_interval' : 3600 * 24,
    # 'update_interval' every x hours
    'data_submission_interval' : 3600,
    # 'data_submission_interval' every hour
    'data_submission_just_in_time' : False,
    # if you need realtime data submission, it overrides 'data_submission_interval'
    'measuremens_per_day' : 144,
    # 'measuremens_per_day' interval starting at 0:00. do not set too high (1440 is already very battery expensive). better using divisors of 86400
    'minimum_sleep_s' : 4,
    # 'minimum_sleep_s' avoid too short sleep periods leading to malfunction
    'sensor_preheating_s' : 30,
    # 'sensor_preheating_s' do not change, suggested by the manufacturers' datasheets
    'last_update_check' : 0,
    'current_version' : 1,
    'repository' : 'github:aleppax/outdoorPMstation/softwarePico/',
    'branch' : 'mvpRemoteUpdate',
    #'repository' : 'http://192.168.0.88:8000/', # example of local update server (base directory should be softwarePico/)
    #'branch' : '',
    'latest_timestamp' : 1609459200,
    'deepsleep_reset' : False,
    'use_wdt' : True,
}
datalogger = {
    'URL' : 'https://example.org/opms/api.php/records/measurements/',
    # use your REST server, change this line
}
filelogger = {
    'filename' : '/logs/measures.txt',
}
logger = {
    'logfile' : 'system.log',
    'filesize_limit_byte' : 4000,
    'logfileCount' : 10,
    'lastlog' : 0,
    'print_log' : True,
}
leadacid = {
    'battery_voltage' : 4.0,
    'ADC_factor1' : 0.108, # there isn't a linear correlation, with two factors we achieve a better result at values where knowing the effective voltage is critical
    'ADC_factor2' : 0.085,
    # =adc*0,108+1/(adc*0,085)
    'ADC_port' : 2,
    'filter_length' : 5, # consider 'measuremens_per_day' (how frequently we take a measurement) if its span is too much reduce this number
    'low_power_mode' : False,
}
mqttlogger = {
    'enable' : False,
    'server' : '',
    'topic' : b'opms/',
    'user' : None,
    'pass' : None,
    'QOS' : 0, # default QOS is 0 and can be changed to 1
}
picosngcja5 = {
    'sensor_power_pin' : 2,
#    '30s_pre_heating' : True,
}
sensors = {
    'average_particle_measurements' : 20,
    'average_measurement_interval_ms' : 1000,
    'disable_sensors' : False,
    'aux_pm_measure_s' : 3600, # 1 hour
}
sps30 = {
    'sensor_power_pin' : 1,
#    '30s_pre_heating' : True,
    'last_cleaning' : 0,
    'cleaning_interval' : 604800/2, # twice a week
}

station = {
    'station' : 1, # this should be unique at least server wise.
    'latitude' : 0.0,
    'longitude' : 0.0,
}
wlan = {
    'SSID_0' : 'xxx',
    'PASSW_0' : 'xxx',
    'connection_timeout' : 15,
    # 'connection_timeout' better setting this at least 10s lower than cron.['sensor_preheating_s']
    'country_code' : 'IT',
}

mftsc = {
    'I' : 'exist',
}

#################################################
###  micropython far too simple config file   ###
###  do not write below this header           ###
###  do not store collections                 ### 
###  usage (add or overwrite config):         ###
### >>>import config                          ###
### >>>config = config.add('mftsc','I','exist')##
###  usage (access config):                   ###
### >>>config.mftsc['I']                      ###
### 'exist'                                   ###
#################################################
import gc
import sys
import machine
from time import sleep
from machine import Pin, I2C

def add(dictname, key, value, do_reload=True):
    newrow = _key_value_dict(key,value)
    me = _open_file_to_lines()
    dict_start = -1
    dict_end = -1
    new_dict = False
    linx = -1
    for rowx, linr in enumerate(me):
        if '#######################################' in linr:
            new_dict = True
            break
        if linr[:4] == '    ':
            linr = '    ' + ' '.join(linr.split()) + '\n'
        else:
            linr = ' '.join(linr.split()) + '\n'
        if linr[:len(dictname)+4] == dictname + ' = {':
            dict_start = rowx
        if dict_start != -1:
            if "    '" + str(key) + "' :" in linr:
                linx = rowx
                break
            if linr == '}\n':
                dict_end = rowx
                break
    result = 0
    if new_dict:
        #print('adding new dictionary')
        newfilerows = _new_dict(dictname,key,value) + me
        result = _write_lines_to_file(newfilerows)    
    elif linx != -1:
        #print('replacing row')
        me[linx] = newrow
        result = _write_lines_to_file(me)
    elif dict_end:
        #print('adding new row')
        me.insert(dict_end,newrow)
        result = _write_lines_to_file(me)
    if do_reload:
        if result:
            return _reload()
        else:
            return sys.modules[__name__]
    else:
        return result

def _reload():
    mod_name = __name__
    del sys.modules[mod_name]
    gc.collect()
    if mod_name == 'config':
        return __import__(mod_name)
    else:
        return __import__(mod_name).config

def _new_dict(dictname,key,value):
    return [dictname + ' = {\n',
    _key_value_dict(key,value),
    '}\n']

def _key_value_dict(key,value):
    if type(value) == type(''):
        return "    '" + str(key) + "' : '" + value + "',\n"
    else:
        return "    '" + str(key) + "' : " + str(value) + ",\n"
    
def _write_lines_to_file(lines):
    try:
        with open(__file__, 'w') as f:
            for l in lines:
                f.write(l)
            return 1
    except:
        print("Could not write file: ", __file__)
        return 0

def _open_file_to_lines():
    conf_lines = []
    try:
        with open(__file__, 'r') as f:
            conf_lines = f.readlines()
    except:
        print("Could not read file: ", __file__)
    return conf_lines

def initialize_board():
    i2c = I2C(board['I2C_BUS'], sda=Pin(board['I2C_SDA']), scl=Pin(board['I2C_SCL']), freq=board['I2C_freq'])
    sleep(0.1)
    gpio = {}
    for pin in board['GPIO_out']:
        gpio['GP'+str(pin)] = machine.Pin(pin, machine.Pin.OUT)
        gpio['GP'+str(pin)].off()
    for pin in board['GPIO_in']:
        gpio['GP'+str(pin)] = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN)
    
    return i2c, gpio

