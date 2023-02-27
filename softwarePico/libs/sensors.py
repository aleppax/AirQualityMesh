from libs import config, leadacid, sps30, picosngcja5, ahtx0, bmp280
from libs.cron import wdt
from machine import Pin
from math import log
from collections import OrderedDict

empty_measures = OrderedDict([
    ('station',''),
    ('datetime',''),
    ('humidity',''),
    ('temperature',''),
    ('pm1.0',''), # mass_densities
    ('pm2.5',''),
    ('pm4',''),
    ('pm10',''),
    ('pm1.0_ch2',''),
    ('pm2.5_ch2',''),
    ('pm4_ch2',''),
    ('pm10_ch2',''),
    ('sound pressure',''), # not implemented yet
    ('barometric pressure',''),
    ('battery charge percentage',''),
    ('O3',''), # not implemented yet
    ('NO2',''), # not implemented yet
    ('internal temperature',''),
    ('wind direction',''), # not implemented yet
    ('wind speed',''), # not implemented yet
    ('battery is charging',''),
    ('dew point','')
])

def init(i2c, gpio):
    wdt.feed()
    global pm_p, pm_s, uln2003, th_s, bm_b
    # bridge GPIO to output connector
    uln2003 = {int(k[8:]): v for k, v in config.sensors.items() if 'uln2003_' in k}
    #corresponding GPIO pin name is addressed with uln2003[1] where 1 is the uln2003 output
    p_pwr_pin = gpio[    uln2003[config.picosngcja5['sensor_power_pin']]  ]
    s_pwr_pin = gpio[    uln2003[config.sps30['sensor_power_pin']]   ] 
    pm_p = picosngcja5.SNGCJA5(i2c, p_pwr_pin) # Panasonic SNGCJA5 PM sensor
    pm_s = sps30.SPS30(i2c, s_pwr_pin) # Sensirion SPS30 PM sensor
    th_s = ahtx0.AHT10(i2c) # AHT20 temperature humidity sensor
    bm_b = bmp280.BMP280(i2c, addr=0x77, use_case = bmp280.BMP280_CASE_WEATHER) # Bosh BMP280 pressure temperature sensor
    bm_b.oversample(bmp280.BMP280_OS_HIGH)

def wakeup():
    pm_p.on()
    pm_s.on()

def shutdown():
    pm_p.off()
    pm_s.off()
    bm_b.sleep()

def measure(time_DTF):
    global measures
    wdt.feed()
    measures = empty_measures
    measures['station'] = config.station['station']
    measures['datetime'] = time_DTF
    measures['internal temperature'], measures['battery charge percentage'], measures['battery is charging'] = leadacid.levels()
    measures['temperature'], measures['humidity'], = th_s.temperature, th_s.relative_humidity
    pm_0_data = pm_p.measure()['mass_density']
    measures['pm10'], measures['pm2.5'], measures['pm1.0']  = pm_0_data['pm10'], pm_0_data['pm2.5'], pm_0_data['pm1.0'] # Panasonic SNGCJA5 PM sensor
    pm_1_data = pm_s.measure()['sensor_data']['mass_density']
    measures['pm10_ch2'], measures['pm2.5_ch2'], measures['pm4_ch2'], measures['pm1.0_ch2']  = pm_1_data['pm10'], pm_1_data['pm2.5'], pm_1_data['pm4.0'], pm_1_data['pm1.0']
    k = log(measures['humidity'] / 100) + (17.62 * measures['temperature']) / (243.12 + measures['temperature'])
    measures['dew point'] =  243.12 * k / (17.62 - k)
    pressure = bm_b.pressure
    p_bar = pressure/100000
    #p_mmHg = pressure/133.3224
    measures['barometric pressure'] = p_bar
