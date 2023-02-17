from libs import config, leadacid, sps30, picosngcja5
from machine import Pin

# ADC battery

def init(i2c, gpio):
    global pm_p, pm_s, uln2003
    # bridge GPIO to output connector
    uln2003 = {int(k[8:]): v for k, v in config.sensors.items() if 'uln2003_' in k}
    #corresponding GPIO pin name is addressed with uln2003[1] where 1 is the uln2003 output
    p_pwr_pin = gpio[    uln2003[config.picosngcja5['sensor_power_pin']]  ]
    s_pwr_pin = gpio[    uln2003[config.sps30['sensor_power_pin']]   ] 
    pm_p = picosngcja5.SNGCJA5(i2c, p_pwr_pin) # Panasonic SNGCJA5 PM sensor
    pm_s = sps30.SPS30(i2c, s_pwr_pin) # Sensirion SPS30 PM sensor

def wakeup():
    pm_p.on()
    pm_s.on()

def shutdown():
    pm_p.off()
    pm_s.off()

def measure():
    internal_temperature, battery_voltage = leadacid.level()
    pass


