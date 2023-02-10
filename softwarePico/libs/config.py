board = {
    'GPIO_out' : ["LED",2,3,4,5,6,7],
    'GPIO_in' : [0,1],
    'I2C_BUS' : 0,
    'I2C_SDA' : 8,
    'I2C_SCL' : 9,
}

cron = {
    'NTP_server_1' : '192.168.0.88', #local NTP server otherwise use something like 'it.pool.ntp.org',
    'NTP_server_2' : '192.168.0.210',
    'epoch' : 1970,
    'NTPsync_interval' : 14400, # every 12 hours
    'last_NTPsync' : 0,
}
logger = {
    'logfile' : 'system.log',
    'filesize_limit_byte' : 4000,
    'print_log' : True,
}
leadacid = {
    'battery_voltage' : 4.0,
    'ADC_factor' : 0.1122,
    'ADC_port' : 2,
}
picosngcja5 = {
    'sensor_power_on_pin' : 15,
}
station = {
    'latitude' : 0.0,
    'longitude' : 0.0,
}
wlan = {
    'SSID_0' : 'xxx',
    'PASSW_0' : 'xxx',
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
from machine import Pin, I2C

def add(dictname, key, value):
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
    if result:
        return _reload()
    else:
        return sys.modules[__name__]

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
    i2c = I2C(board['I2C_BUS'], sda=Pin(board['I2C_SDA']), scl=Pin(board['I2C_SCL']))
    gpio = {}
    for pin in board['GPIO_out']:
        gpio['GP'+str(pin)] = machine.Pin(pin, machine.Pin.OUT)
        gpio['GP'+str(pin)].off()
    for pin in board['GPIO_in']:
        gpio['GP'+str(pin)] = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_DOWN)
    
    return i2c, gpio
