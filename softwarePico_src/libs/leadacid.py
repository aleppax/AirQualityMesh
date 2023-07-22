from machine import ADC
import time
from libs import logger, config

# battery working interval
# designed for AGM lead acid batteries, use 4, 6 or 12 V batteries.
# (4V batteries can be recharged easily and can power the Pico W directly) 
# thanks to the buck-boost SMPS RT6154 on the Raspberry pico W board
# measures are referred to a typical load of 0,01% of battery capacity
# charging voltage is fixed, it doesn't adapt to temperature.
battery_voltage = config.leadacid['battery_voltage'] # 4.0, 6.0 or 12.0
voltage_full_charged = battery_voltage * 1.15 # voltage can be higher than this when charging. Valid at least 15 minutes after end of charge
max_voltage = battery_voltage * 1.25 # above this value the battery will be damaged and the ADC too
charging_voltage = battery_voltage * 1.2375 # this is typical when topping charge, current drops until full charged
#final_discharge_voltage = battery_voltage * 0.8 # below this lower limit the battery will be irreversibly damaged
safe_min_discharge = battery_voltage * 0.9 # below this limit the battery life will be reduced from 700 to 150-200 cycles
min_charging_voltage = battery_voltage * 1.05 # if cron['data_submission_when_charging'] is True, data can be sent when voltage > min_charging_voltage.
# this value indicates that the battery is charging or enough charged to send data.
t_m_callback = False
adc = ADC(config.leadacid['ADC_port'])
ADC_factor1 = config.leadacid['ADC_factor1']
ADC_factor2 = config.leadacid['ADC_factor2']
rp2040_temp = ADC(4)
rp2040_temp_factor = 3.3 / (65535)

def measure_RP2040_temp():
    reading = rp2040_temp.read_u16() * rp2040_temp_factor
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

def ADC_voltage():
    reading = adc.read_u16()
    result = (reading * (ADC_factor1)) + 1 / (reading * (ADC_factor2))
    return int(result)   
    
def average_n_measurements(n,callback, interval=0):
    count = 0
    sum_measures = 0
            # init network
    while count < n:
        start_cycle_time = time.ticks_ms()
        count += 1
        sum_measures += callback()
        rem_iteration_time_ms = interval - time.ticks_diff(time.ticks_ms(),start_cycle_time)
        if rem_iteration_time_ms > 0:
            time.sleep_ms(rem_iteration_time_ms)
    return sum_measures/n

def battery_percentage(voltage):
    if voltage > max_voltage:
        logger.error('voltage is greater than max_voltage: ' + str(voltage))
    is_charging = voltage > min_charging_voltage
    #convert voltage in percentage, uses different max values if charging or not
    if is_charging:
        percentage = int((voltage - safe_min_discharge) / (charging_voltage - safe_min_discharge) * 100)
    else:
        percentage = int((voltage - safe_min_discharge) / (voltage_full_charged - safe_min_discharge) * 100)
    return percentage, is_charging

def levels():
    global config
    #temp measure
    temperature = average_n_measurements(10,measure_RP2040_temp)
    #ADC measure
    vvvoltage = average_n_measurements(100,ADC_voltage)/1000
    percentage, is_charging = battery_percentage(vvvoltage)
    # if battery is too low, switch to low power mode. 
    # Restore normal power if battery is charging and level is greater than minimum safe lvl.
    if vvvoltage < safe_min_discharge:
        if config.leadacid['low_power_mode'] is False:
            logger.warning('Switching to low power mode')
            config.set('leadacid','low_power_mode',True)
    if (vvvoltage > safe_min_discharge + 0.1):
        if config.leadacid['low_power_mode'] is True:
            logger.warning('Switching back from low power')
            config.set('leadacid','low_power_mode',False)
    return temperature, percentage, vvvoltage, is_charging
