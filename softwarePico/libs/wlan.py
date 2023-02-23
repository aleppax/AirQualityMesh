import machine
import network
import socket
import binascii
import time
from libs import logger, config
from libs.cron import wdt

wlan = ''
trying = False
wlanSw = machine.Pin(23, machine.Pin.OUT)
statuses = {
    -3 : 'authentication failure',
    -2 : 'No matching SSID found (could be out of range, or down)',
    -1 : 'Connection failed',
    0  : 'Link is down',
    1  : 'link established',
    2  : 'Connected to wifi, but no IP address',
    3  : 'Connected. Got an IP address',
}

def initialize():
    global wlanSw
    wlanSw.high()
    time.sleep_ms(80)
    wdt.feed()
    if not hasattr(config,'wlan'):
        serve_captive_portal()
    return connect(0)

def turn_off():
    global wlan, wlanSw
    wlanSw.low()
    time.sleep_ms(100)
    wlan.disconnect()
    wlan.active(False)
    wlan.deinit()
    wlan = None
    time.sleep_ms(100)

def connect_from_list():
    global trying
    trying = True
    wifiNumber = 0
    connected = False
    while trying:
        connected = connect(wifiNumber)
        wifiNumber += 1
        if connected:
            return True
    return False

def online():
    if wlan == '':
        return initialize()
    if wlan.status() == 3:
        return True
    else:
        return False

def connect(wifiNumber):
    wdt.feed()
    global wlan, trying
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    ssid = "SSID_" + str(wifiNumber)
    password = "PASSW_" + str(wifiNumber)
    if ssid in config.wlan:
        ssid, password = config.wlan[ssid], config.wlan[password]
        try:
            wlan.connect(ssid, password)
        except:
            logger.error('Wrong wifi credentials')
        timeout = config.wlan['connection_timeout']
        prev_status = -4
        while timeout > 0:
            wdt.feed()
            status = wlan.status()
            if prev_status != status:
                logger.info(statuses[status])
                prev_status = status
            if status == 3:
                return True
            if status in [-3,-2,-1,0]:
                return False 
            timeout -= 1
            time.sleep(1)
    else:
        logger.warning('connection failed.')
        trying = False
        return False

def serve_captive_portal():
    global wlan
    iam = machine.unique_id()
    passwd = binascii.hexlify(iam).decode('utf-8')[-8:]
    global ap
    wlan = network.WLAN(network.AP_IF)
    wlan.config(essid=ssid, password=passwd)
    wlan.active(True)
    while ap.active() == False:
        pass
    ipaddress = ap.ifconfig()[0]
    # now wait for a connection
    while ap.isconnected() == False:
        pass
    html_portal = open('./html/portal.html')
    html_form = html_portal.read()
    html_portal.close()
    addrinfo = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = socket.socket()
    s.bind(addrinfo)
    s.listen(1)
    # Listen for connections
    waiting_credentials = True
    while waiting_credentials:
        wdt.feed()
        try:
            cl, addr = s.accept()
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(html_form)
            logger.debug('client connected from', addr)
            request = cl.recv(1024)
            request = str(request.decode('utf-8'))
            reqstrings = request.split("\r\n")
            for part in reqstrings:
                if 'GET /?' in part:
                    subparts = part.split("&")
                    if 'text-password=' in subparts[1]:
                        newpassword = subparts[1].split('=')[1]
                        newssid = subparts[0].split('=')[1]
                    if 'text-latitude' in subparts[2]:
                        latitude = subparts[2].split('=')[1]
                    if 'text-longitude' in subparts[3]:
                        longitude = subparts[3].split('=')[1]
                        # validate field input
                        #TODO
                        exist_wifi = True
                        wifiNumber = 0
                        while exist_wifi:
                            wifiNumber += 1
                            ssid = "SSID_" + str(wifiNumber)
                            exist_wifi = ssid in config.wlan
                        config = config.add('wlan',"SSID_" + str(wifiNumber),newssid)
                        config = config.add('wlan',"PASSW_" + str(wifiNumber),newpassword)
                        config = config.add('station',"latitude",latitude)
                        config = config.add('station',"longitude",longitude)
                        # now send a confirmation page, wait ten seconds and reboot
                        #TODO
                        waiting_credentials = False
                        cl.close()
                        wlan.disconnect()
                        machine.soft_reset()

        except OSError as e:
            cl.close()
            print('connection closed')
