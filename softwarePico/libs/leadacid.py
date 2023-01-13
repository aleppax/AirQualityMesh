from machine import ADC
import time
from libs import logger, config

# battery working interval
# designed for lead acid batteries with two cells, 4V nominal voltage, 
# because they can be recharged easily and can power the Pico directly
# measures are referred to a maximum load of 30 mA (during the measure), for a battery of 3000 mA
voltage_full_charged = 4.4 # voltage can be higher than this when charging. Valid at least 15 minutes after end of charge
max_voltage = 5.0 # above this value the battery will be damaged and the ADC too
charging_voltage = 4.7 # this is typical when topping charge, current drops until full charged
final_discharge_voltage = 3.9 # below this lower limit the battery will be irreversibly damaged
safe_min_discharge = 4.1 # below this limit the battery life will be reduced from 700 to 150-200 cycles
# 
t_m_callback = False
adc = ADC(config.leadacid['ADC_port'])
ADC_factor = config.leadacid['ADC_factor']

def set_temp_measurement_gauge(callback):
    if not callable(callback):
        logger.error('leadacid.py: Invalid parameter: callback must be a callable object')
    global t_m_callback
    t_m_callback = callback

def level():
    #temp measure
    temperature = average_n_measurements(10,bmp_temperature)
    #ADC measure
    voltage = average_n_measurements(100,ADC_voltage)
    print(temperature)
    print(voltage)

def bmp_temperature():
    t_m_callback.blocking_read()
    return t_m_callback.temperature

def ADC_voltage():
    return int(adc.read_u16() * (ADC_factor))   
    
def average_n_measurements(n,callback):
    count = 0
    sum_measures = 0
    while count < n:
        count += 1
        sum_measures += callback()
    return sum_measures/n
