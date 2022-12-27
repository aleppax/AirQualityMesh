import machine
from ntp import Ntp
import os, io
import credentials_portal as cportal
import network, binascii


#load configuration files
conf_files = os.listdir('/conf')
if 'wifi.conf' not in conf_files:
    #no .conf file, acting as an access point, user input required.
    cportal.serve_credentials_portal()    
cportal.connect_accesspoint()


_rtc = machine.RTC()
Ntp.set_datetime_callback(_rtc.datetime)
Ntp.set_hosts(('pool.ntp.org','it.pool.ntp.org'))
print("Current time:" + str(_rtc.datetime()))