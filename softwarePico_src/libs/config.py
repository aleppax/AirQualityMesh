aht20 = {
    'name' : 'Humidity and Temperature Sensor AHT20',
    'is_sensor' : True,
    'is_auxiliary' : False,
    'driver' : 'ahtx0',
    'cls' : 'AHT20',
    'init_arguments' : {},
    'i2c_address' : '0x38',
}
bmp280 = {
    'name' : 'Pressure sensor BMP280',
    'is_sensor' : True,
    'is_auxiliary' : False,
    'driver' : 'bmp280',
    'cls' : 'BMP280',
    'init_arguments' : {'addr' : 0x77, 'use_case' : 2},
    'i2c_address' : '0x77',
}
board = {
    'GPIO_out' : [2,3,4,5,6,7], # Even if you could, Do NOT use "LED"
    'GPIO_in' : [0,1],
    'I2C_BUS' : 0,
    'I2C_SDA' : 8,
    'I2C_SCL' : 9,
    'I2C_freq' : 100000,
    'WDT_seconds' : 8,
    'led_pin' : 22,
}
cron = {
    'NTP_server' : 'it.pool.ntp.org',
    'NTP_server_count' : 4,
    'NTPsync_interval' : 3600 * 24,
    # 'NTPsync_interval' every x seconds
    'update_interval' : 3600 * 24,
    # 'update_interval' every x seconds
    'data_submission_interval' : 3600,
    # 'data_submission_interval' every x seconds
    'data_submission_just_in_time' : False,
    # if you need realtime data submission, it overrides 'data_submission_interval' and 'data_submission_when_charging'
    'data_submission_when_charging' : True,
    # sends data only when the battery voltage is greater than leadacid.min_charging_voltage
    'measurements_per_day' : 144,                       ###  basic  ###
    # 'measurements_per_day' interval starting at 0:00. do not set too high
    'minimum_sleep_s' : 4,
    # 'minimum_sleep_s' avoid too short sleep periods leading to malfunction
    'sensor_preheating_s' : 30,
    # 'sensor_preheating_s' do not change, suggested by the manufacturers' datasheets
    'last_update_check' : 0,
    'current_version' : 64,
    'repository' : 'https://raw.githubusercontent.com/aleppax/outdoorPMstation/updates/concept/softwarePico_dist',
    #'repository' : 'http://192.168.0.88:8000', # example of local server
    'use_wdt' : True,
}
datalogger = {
    'URL' : 'http://example.org/opms/api.php/records/',
    'apikey' : '',
    # use your REST server. prefer unsecure http
    # to avoid crashes due to limitations of the implementation.
}
filelogger = {
    'filename' : '/logs/measures.txt',
}
logger = {
    'logfile' : 'system.log',
    'filesize_limit_byte' : 6000,                       
    'logfileCount' : 12,
    'lastlog' : 0,
    'print_log' : True,
    'enable_log' : True,
    'loglevel' : 4,
}
leadacid = {
    'battery_voltage' : 4.0,
    'ADC_factor1' : 0.108,
    'ADC_factor2' : 0.085,
    # =adc*0,108+1/(adc*0,085)
    'ADC_port' : 2,
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
    'name' : 'Laser Type PM Sensor SN-GCJA5',
    'is_sensor' : True,
    'is_auxiliary' : True,
    'driver' : 'picosngcja5',
    'cls' : 'SNGCJA5',
    'init_arguments' : {},
    'i2c_address' : '0x33',
    'power_pin_name' : 'GP6',
}
pms5003 = {
    'name' : 'PM Sensor PMS5003',
    'is_sensor' : True,
    'is_auxiliary' : False,
    'driver' : 'pms5003',
    'cls' : 'PMS5003',
    'init_arguments' : {'mode' : 'passive'},
    'serial_tx' : 'GP16',
    'serial_rx' : 'GP17',
    'power_pin_name' : 'GP3',
    'temp_and_humi' : True, # if the sensor is PMS5003T it provides also temperature and humidity
}
pms5003_ch2 = {
    'name' : 'PM Sensor PMS5003 (channel 2)',
    'is_sensor' : True,
    'is_auxiliary' : True,
    'driver' : 'pms5003',
    'cls' : 'PMS5003',
    'init_arguments' : {'mode' : 'passive'},
    'serial_tx' : 'GP4',
    'serial_rx' : 'GP5',
    'power_pin_name' : 'GP2',
    'temp_and_humi' : True, # if the sensor is PMS5003T it provides also temperature and humidity
}
qmc5883 = {
    'name' : 'Magnetic field sensor QMC5883',
    'is_sensor' : True,
    'is_auxiliary' : False,
    'driver' : 'qmc5883',
    'cls' : 'QMC5883',
    'init_arguments' : {},
    'i2c_address' : '0x13',
}
sensors = {
    'average_particle_measurements' : 20,
    'average_measurement_interval_ms' : 1000,
    'enable_sensors' : True,
    'aux_measure_s' : 3600, # 1 hour
}
sps30 = {
    'name' : 'PM Sensor SPS30',
    'is_sensor' : True,
    'is_auxiliary' : False,
    'driver' : 'sps30',
    'cls' : 'SPS30',
    'init_arguments' : {},
    'i2c_address' : '0x69',
    'power_pin_name' : 'GP7',
    'last_cleaning' : 0,
    'cleaning_interval' : 604800/2, # twice a week
}

station = {
    'UID' : None,
    'station' : None, # unique at least server wise.
    'latitude' : 0.0,
    'longitude' : 0.0,
}
wlan = {
    'SSID_0' : 'xxx',
    'PASSW_0' : 'xxx',
    'AP_SSID' : 'opms',
    'AP_PASSW' : 'opmsopms',
    'connection_timeout' : 15,
    # at least 10s lower than cron.['sensor_preheating_s']
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
### >>>config = config.set('mftsc','I','exist')##
###  usage (access config):                   ###
### >>>config.mftsc['I']                      ###
### 'exist'                                   ###
#################################################
import gc
import sys
import machine
from time import sleep
from machine import Pin, I2C

def set(dictname, key, value, do_reload=True):
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
        newfilerows = _new_dict(dictname,key,value) + me
        result = _write_lines_to_file(newfilerows)    
    elif linx != -1:
        me[linx] = newrow
        result = _write_lines_to_file(me)
    elif dict_end:
        me.insert(dict_end,newrow)
        result = _write_lines_to_file(me)
    if do_reload:
        if result:
            _reload()
        else:
            return
    else:
        return

def _reload():
    del sys.modules['libs.config']
    # if config is imported by other modules, delete it recursively
    for mo in sys.modules:
        if 'config' in dir(sys.modules[mo]):
            del sys.modules[mo].__dict__['config']
            sys.modules[mo].__dict__['config'] = __import__('libs.config').config
    gc.collect()
    sys.modules['libs.config'] = __import__('libs.config').config

def _new_dict(dictname,key,value):
    return [dictname + ' = {\n',
    _key_value_dict(key,value),
    '}\n']

def _key_value_dict(key,value):
    if isinstance(value,str):
        return "    '" + str(key) + "' : '" + value + "',\n"
    else:
        return "    '" + str(key) + "' : " + str(value) + ",\n"
    
def _write_lines_to_file(lines):
    try:
        with open(__file__, 'w') as f:
            for line in lines:
                f.write(line)
            return 1
    except Exception:
        print("Could not write file: ", __file__)
        return 0

def _open_file_to_lines():
    conf_lines = []
    try:
        with open(__file__, 'r') as f:
            conf_lines = f.readlines()
    except Exception:
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
    if board['led_pin'] in [1,22,26,27]:
        board['ledpin'] = machine.Pin(board['led_pin'], machine.Pin.OUT)
        flash_led('ok')
    else:
        board.ledpin = None
    return i2c, gpio

def flash_led(mode):
    if board['ledpin'] != None:
        modes = {
            'ok' : [1],
            'error' : [0.5,0.5,0.5],
        }
        for s in modes[mode]:
            board['ledpin'].on()
            sleep(s)
            board['ledpin'].off()
            sleep(0.2)
