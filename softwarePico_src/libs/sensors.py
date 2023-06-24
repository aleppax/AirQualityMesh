from libs import config, leadacid, logger
from libs.cron import feed_wdt, deepsleep_as_long_as_you_can
from math import log
from collections import OrderedDict
from time import ticks_ms, ticks_diff, sleep_ms, time
from machine import Pin

sensors = {}

measures = OrderedDict([
    ('station',0),
    ('datetime',0),
    ('humidity',0),
    ('temperature',0),
    ('pm1.0',0), # mass_densities
    ('pm2.5',0),
    ('pm4',0),
    ('pm10',0),
    ('pm1.0_ch2',0),
    ('pm2.5_ch2',0),
    ('pm4_ch2',0),
    ('pm10_ch2',0),
    ('sound pressure',0), # not implemented yet
    ('barometric pressure',0),
    ('battery charge percentage',0),
    ('vsys voltage',0),
    ('O3',0), # not implemented yet
    ('NO2',0), # not implemented yet
    ('internal temperature',0),
    ('wind direction',0), # not implemented yet
    ('wind speed',0), # not implemented yet
    ('battery is charging',0),
    ('dew point',0)
])
battery_values = ()

def init(i2c, gpio):
    feed_wdt()
    global sensors, latest_aux_measure, use_aux_sensors
    if config.sensors['enable_sensors']:
        latest_aux_measure = time()
        use_aux_sensors = False
        # build the list of sensors
        sensors = dict([(name, cls) for name, cls in config.__dict__.items() if isinstance(cls, dict)])
        for name, item in sensors.items():
            if 'is_sensor' not in item.keys():
                sensors.pop(name)
        for pin in gpio:
            gpio[pin].on()
        sleep_ms(200)
        startupTests(i2c, gpio)
        for s,t in sensors.items():
            if t['connected']:
                feed_wdt()
                logger.info('loading sensor ' + s)
                # import driver module
                if 'driver' in t.keys():
                    t['module'] = __import__('/libs/' + t['driver'])
                    # instantiate the class
                    sensor_class = t['module'].__dict__[t['cls']]
                    # if i2c
                    if 'i2c_address' in t.keys():
                        t['object'] = sensor_class(i2c, **t['init_arguments'])
                    # if serial (only pms5003 currently supported)
                    if t['driver'] == 'pms5003':
                        from machine import UART
                        uart = UART(0,baudrate=9600, tx=Pin(config.pms5003['serial_tx']), rx=Pin(config.pms5003['serial_rx']))
                        t['object'] = sensor_class(uart,None,None,**t['init_arguments'])
                if 'power_pin_name' in t.keys():
                    t['pwr_pin'] = gpio[t['power_pin_name']]
        ### custom initialization code
        if sensors['bmp280']['connected']: 
            sensors['bmp280']['object'].oversample(3)
        #
        for pin in gpio:
            gpio[pin].off()
        power_i2c_devices(False,'off')

def sensorlist():
    s_description = ''
    for s,t in sensors.items():
        feed_wdt()
        s_description +=  s + '§t' + str(t['connected']) + '§t' + t['name'] + '§t' + t['i2c_address'] + '§t' + str(t['is_auxiliary']) + '§n'
    return s_description
        
def power_i2c_devices(only_aux_devices=True, action='on'):
    for v in sensors.values():
        if 'pwr_pin' in v:
            if only_aux_devices:
                if v['is_auxiliary']:
                    getattr(v['pwr_pin'],action)()
            else:
                getattr(v['pwr_pin'],action)()
    sleep_ms(200)

def startupTests(i2c, gpio):
    global sensors
    #look for a PMS5003 connected to UART0
    pin_rx_uart =  Pin(config.pms5003['serial_rx'], Pin.IN, Pin.PULL_DOWN)
    if pin_rx_uart.value() == 1:
        sensors['pms5003']['connected'] = True
    else:
        sensors['pms5003']['connected'] = False
    # list i2c devices, some of them are powered by the ULN2003, 
    # but not yet initialized. turn everything on for this test.
    addresses = [hex(a) for a in i2c.scan()]
    # sometimes if a device is not powered, the bus floats and shows 
    # a lot of inexistent devices, check this
    if len(addresses) > len(sensors)-1:
        logger.error("the i2c bus is connected to zombie devices, it\
        has been compromised. Or maybe a new device has been added, \
        in that case please update the config file.")
    for name, s in sensors.items():
        if 'i2c_address' in s.keys():
            if s['i2c_address'] in addresses:
                s['connected'] = True
            else:
                s['connected'] = False

def wakeup():
    global config, use_aux_sensors
    if config.sensors['enable_sensors']:
        feed_wdt()
        rtc_now = time()
        use_aux_sensors = rtc_now - config.sensors['aux_measure_s'] > latest_aux_measure
        power_i2c_devices(False, 'on')
        ### sps30   custom wakeup code   ### TODO: still can't 
        # figure out where to place it, if not here
        if sensors['sps30']['connected']:
            clean = rtc_now - config.sps30['last_cleaning'] > config.sps30['cleaning_interval']
            sensors['sps30']['object'].wakeup(clean)
            if clean:
                feed_wdt()
                logger.info('Cleaning SPS30 sensor')
                # this has to be written to file
                config.set('sps30','last_cleaning',rtc_now)
        ### sps30 end custom wakeup code ###
        if not use_aux_sensors:
            power_i2c_devices(True,'off')

def reset_measures():
    global measures
    for m in measures:
        measures[m] = 0

def measure_battery():
    global battery_values
    battery_values = leadacid.levels()

def measure(time_DTF):
    global measures, latest_aux_measure
    feed_wdt()
    reset_measures()
    measures['station'] = config.station['station']
    measures['datetime'] = time_DTF
    measures['internal temperature'], measures['battery charge percentage'], measures['vsys voltage'], measures['battery is charging'] = battery_values
    # averaging n measures from sensors with 1Hz frequency
    if config.sensors['enable_sensors']:
        rtc_now = time()
        if use_aux_sensors:
            latest_aux_measure = rtc_now       
        count = config.sensors['average_particle_measurements']
        measuring_msg = 'Measuring. Collecting ' + str(count) + ' measures'
        logger.info(measuring_msg)
        while count > 0:
            feed_wdt()
            start_iter_time = ticks_ms()
            count -= 1
            if not use_aux_sensors: 
                power_i2c_devices(True,'on')
            for s in sensors.values():
                if s['connected']:
                    if not s['is_auxiliary'] or (s['is_auxiliary'] and use_aux_sensors):
                        feed_wdt()
                        s['object'].add_measure_to(measures) # a function which sums one or more measured values to one or more keys of the measure dict.
            if not use_aux_sensors: 
                power_i2c_devices(True,'off')
            rem_iter_time_ms = config.sensors['average_measurement_interval_ms'] - ticks_diff(ticks_ms(),start_iter_time)
            if rem_iter_time_ms > 0:
                sleep_ms(rem_iter_time_ms)
        feed_wdt()
        measuring_msg = 'Measuring. Averaging measures'
        logger.info(measuring_msg)
        for measurand in ['temperature','humidity','barometric pressure','pm2.5','pm1.0','pm10_ch2','pm2.5_ch2','pm1.0_ch2']:
            measures[measurand] /= config.sensors['average_particle_measurements']
        if (measures['temperature'] != 0) or (measures['humidity'] != 0):
            k = log(measures['humidity'] / 100) + (17.62 * measures['temperature']) / (243.12 + measures['temperature'])
            measures['dew point'] =  243.12 * k / (17.62 - k)
        else:
            measures['dew point'] = 0
        feed_wdt()
        logger.info('End of measurements. Turning off devices.')
        power_i2c_devices(False,'off')

def check_low_power():
    feed_wdt()
    # checking for low power mode (battery saving)
    if config.leadacid['low_power_mode'] is True:
        leadacid.levels()
        if config.leadacid['low_power_mode'] is True:
            deepsleep_as_long_as_you_can()
