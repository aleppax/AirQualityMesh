from machine import lightsleep, Pin
from time import sleep, sleep_ms
import network
from libs import config

ssid = config.wlan['SSID_0']
password = config.wlan['PASSW_0']

led = machine.Pin('LED', machine.Pin.OUT)

wlan = network.WLAN(network.STA_IF)

wlan.active(True)
wlan.connect(ssid, password)
while wlan.isconnected() == False:
    print('no wlan')
    sleep_ms(1000)
print('ok wlan')

#do the magic
wlan.disconnect()
wlan.active(False)
wlan.deinit()    #spegnere chip wifi
sleep_ms(100)
wlan=None
print('spento  wlan')

i = 0
while (i<30):
    led.on()
    sleep(.2)
    led.off()
    sleep(.2)
    i = i + 1
    
print('prima LS')
msecondi = 10000
lightsleep(msecondi)
sleep(.5)
print(f'fuori! dopo {msecondi} ms')

i = 0
while (i<20):
    led.on()
    sleep(.5)
    led.off()
    sleep(.5)
    i = i + 1

sleep(10)
machine.reset()
   
