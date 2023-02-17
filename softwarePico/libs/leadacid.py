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
voltage_full_charged = battery_voltage * 1.1 # voltage can be higher than this when charging. Valid at least 15 minutes after end of charge
max_voltage = battery_voltage * 1.25 # above this value the battery will be damaged and the ADC too
charging_voltage = battery_voltage * 1.175 # this is typical when topping charge, current drops until full charged
final_discharge_voltage = battery_voltage * 0.975 # below this lower limit the battery will be irreversibly damaged
safe_min_discharge = 4.1 # below this limit the battery life will be reduced from 700 to 150-200 cycles
# 
t_m_callback = False
adc = ADC(config.leadacid['ADC_port'])
ADC_factor = config.leadacid['ADC_factor']
rp2040_temp = ADC(4)
rp2040_temp_factor = 3.3 / (65535)
voltage_filter = []
filter_length = config.leadacid['filter_length'] # how many previous measurements are used to calculate the moving average

def measure_RP2040_temp():
    reading = rp2040_temp.read_u16() * rp2040_temp_factor
    temperature = 27 - (reading - 0.706)/0.001721
    return temperature

def ADC_voltage():
    return int(adc.read_u16() * (ADC_factor))   
    
def average_n_measurements(n,callback):
    count = 0
    sum_measures = 0
    while count < n:
        count += 1
        sum_measures += callback()
    return sum_measures/n

def battery_percentage(voltage):
    global voltage_filter
    #detect if the battery is charging or discharging (moving average direction)
    voltage_filter.append(voltage)
    moving_voltage = round(sum(voltage_filter)/len(voltage_filter),3)
    if len(voltage_filter) == filter_length:
        voltage_filter.pop(0)
    is_charging = voltage > moving_voltage
    #convert voltage in percentage
    # we know if battery is charging if the previous value was lower.
    if is_charging:
        percentage = int((voltage - safe_min_discharge) / (charging_voltage - safe_min_discharge) * 100)
    else:
        percentage = int((voltage - safe_min_discharge) / (voltage_full_charged - safe_min_discharge) * 100)
    return percentage, is_charging

def levels():
    global previous_voltage
    #temp measure
    temperature = average_n_measurements(10,measure_RP2040_temp)
    #ADC measure
    voltage = average_n_measurements(100,ADC_voltage)
    percentage, is_charging = battery_percentage(voltage)
    return temperature, percentage, is_charging
