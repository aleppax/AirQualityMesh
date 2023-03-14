from libs import  ahtx0, bmp280, config, leadacid, logger, picosngcja5, sps30
from libs.cron import feed_wdt, deepsleep_as_long_as_you_can, lightsleep_wrapper
from machine import Pin, reset
from math import log
from collections import OrderedDict
from time import ticks_ms, ticks_diff, sleep_ms, time

empty_measures = OrderedDict([
    ('station',''),
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
    ('O3',0), # not implemented yet
    ('NO2',0), # not implemented yet
    ('internal temperature',0),
    ('wind direction',0), # not implemented yet
    ('wind speed',0), # not implemented yet
    ('battery is charging',0),
    ('dew point',0)
])

def init(i2c, gpio):
    feed_wdt()
    global pm_p, pm_s, uln2003, th_s, bm_b, measures, latest_aux_pm_measure
    measures = empty_measures
    latest_aux_pm_measure = time()
    # bridge GPIO to output connector
    uln2003 = {int(k[8:]): v for k, v in config.board.items() if 'uln2003_' in k}
    #corresponding GPIO pin name is addressed with uln2003[1] where 1 is the uln2003 output
    if not config.sensors['disable_sensors']:
        p_pwr_pin = gpio[    uln2003[config.picosngcja5['sensor_power_pin']]  ]
        s_pwr_pin = gpio[    uln2003[config.sps30['sensor_power_pin']]   ] 
        pm_p = picosngcja5.SNGCJA5(i2c, p_pwr_pin) # Panasonic SNGCJA5 PM sensor
        pm_s = sps30.SPS30(i2c, s_pwr_pin) # Sensirion SPS30 PM sensor
        th_s = ahtx0.AHT10(i2c) # AHT20 temperature humidity sensor
        bm_b = bmp280.BMP280(i2c, addr=0x77, use_case = bmp280.BMP280_CASE_WEATHER) # Bosh BMP280 pressure temperature sensor
        bm_b.oversample(bmp280.BMP280_OS_HIGH)
        pm_p.off()
        pm_s.off()

def measure_aux_pm_sensor():
    if config.sensors['disable_sensors']:
        return
    global latest_aux_pm_measure, measures
    feed_wdt()
    # aux sensor should wake up when the other one is powered down,
    # to limit the current peak
    # auxiliary sensor (only wakes up once per sensors['aux_pm_measure_s'] seconds)
    # to limit battery usage
    rtc_now = time()
    if rtc_now - config.sensors['aux_pm_measure_s'] < latest_aux_pm_measure:
        measures['pm10'] = 0
        measures['pm2.5'] = 0
        measures['pm1.0'] = 0
        return
    latest_aux_pm_measure = rtc_now
    # wake up
    pm_p.on()
    # wait 30 seconds to heat the sensor
    lightsleep_wrapper(config.cron['sensor_preheating_s']*1000)
    # measure 
    # averaging n measures from sensors with 1Hz frequency
    count = config.sensors['average_particle_measurements']
    while count > 0:
        feed_wdt()
        start_iter_time = ticks_ms()
        count -= 1
        pm_s.on()
        sleep_ms(2)
        pm_0_data = pm_p.measure()['mass_density']
        pm_s.off()
        measures['pm10'] += pm_0_data['pm10'] # Panasonic SNGCJA5 PM sensor
        measures['pm2.5'] += pm_0_data['pm2.5']
        measures['pm1.0'] += pm_0_data['pm1.0']
        rem_iter_time_ms = config.sensors['average_measurement_interval_ms'] - ticks_diff(ticks_ms(),start_iter_time)
        if rem_iter_time_ms > 0:
            sleep_ms(rem_iter_time_ms)
    measures['pm10'] /= config.sensors['average_particle_measurements']
    measures['pm2.5'] /= config.sensors['average_particle_measurements']
    measures['pm1.0'] /= config.sensors['average_particle_measurements']
    #shutdown
    pm_p.off()

def wakeup():
    global config
    if not config.sensors['disable_sensors']:
        feed_wdt()
        pm_s.on()
        sleep_ms(200)
        pm_p.on()
        pm_s.start_measurement()
        sleep_ms(10)
        # check if sps30 requires to be cleaned, it can be done while preheating
        rtc_now = time()
        if rtc_now - config.sps30['last_cleaning'] > config.sps30['cleaning_interval']:
            feed_wdt()
            logger.info('Cleaning SPS30 sensor')
            pm_s.start_fan_cleaning()
            # this has to be written to file
            config = config.add('sps30','last_cleaning',rtc_now)
        pm_p.off()

def shutdown():
    if not config.sensors['disable_sensors']:
        feed_wdt()
        pm_s.off()

def measure(time_DTF):
    global measures
    feed_wdt()
    measures = empty_measures
    measures['station'] = config.station['station']
    measures['datetime'] = time_DTF
    measures['internal temperature'], measures['battery charge percentage'], measures['battery is charging'] = leadacid.levels()
    # averaging n measures from sensors with 1Hz frequency
    if not config.sensors['disable_sensors']:
        count = config.sensors['average_particle_measurements']
        while count > 0:
            feed_wdt()
            start_iter_time = ticks_ms()
            count -= 1
            pm_p.on()
            sleep_ms(10)
            measures['temperature'] += th_s.temperature
            measures['humidity'] += th_s.relative_humidity
            pressure = bm_b.pressure
            p_bar = pressure/100000
            measures['barometric pressure'] += p_bar
            pm_1_data = pm_s.measure()['mass_density']
            pm_p.off()
            measures['pm10_ch2'] += pm_1_data['pm10'] # Sensirion SPS30
            measures['pm2.5_ch2'] += pm_1_data['pm2.5']
            measures['pm4_ch2'] += pm_1_data['pm4.0']
            measures['pm1.0_ch2'] += pm_1_data['pm1.0']
            rem_iter_time_ms = config.sensors['average_measurement_interval_ms'] - ticks_diff(ticks_ms(),start_iter_time)
            if rem_iter_time_ms > 0:
                sleep_ms(rem_iter_time_ms)
        measures['temperature'] /= config.sensors['average_particle_measurements']
        measures['humidity'] /= config.sensors['average_particle_measurements']
        measures['barometric pressure'] /= config.sensors['average_particle_measurements']
        measures['pm10_ch2'] /= config.sensors['average_particle_measurements']
        measures['pm2.5_ch2'] /= config.sensors['average_particle_measurements']
        measures['pm4_ch2'] /= config.sensors['average_particle_measurements']
        measures['pm1.0_ch2'] /= config.sensors['average_particle_measurements']
        feed_wdt()
        k = log(measures['humidity'] / 100) + (17.62 * measures['temperature']) / (243.12 + measures['temperature'])
        measures['dew point'] =  243.12 * k / (17.62 - k)
    
def check_low_power():
    feed_wdt()
    # checking for low power mode (battery saving)
    if leadacid.config.leadacid['low_power_mode'] == True:
        leadacid.levels()
        if leadacid.config.leadacid['low_power_mode'] == True:
            deepsleep_as_long_as_you_can()
