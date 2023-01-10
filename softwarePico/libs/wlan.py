import machine
import network
import socket
import binascii
import time
from libs import logger, config

wlan = ''
trying = False

def initialize():
    connected = False
    if not hasattr(config,'wifi'):
        serve_captive_portal()
    connected = connect_from_list()
    if not connected:
        logger.warning("No way to connect. Rebooting in 20 seconds")
        machine.lightsleep(20000) # ms
        machine.soft_reset()

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

def connect(wifiNumber):
    global wlan, trying
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    ssid = "SSID_" + str(wifiNumber)
    password = "PASSW_" + str(wifiNumber)
    if ssid in config.wifi:
        ssid, password = config.wifi[ssid], config.wifi[password]
        wlan.connect(ssid, password)
        timeout = 10
        while timeout > 0:
            status = wlan.status()
            if status == -3:
                logger.warning('authentication failure')
                return False
            elif status == -2:
                logger.warning('No matching SSID found (could be out of range, or down)')
                return False
            elif status == -1:
                logger.warning('Connection failed')
                return False
            elif status == 0:
                logger.warning('Link is down')
                return False 
            elif status == 1:
                logger.info('Connected to wifi')
            elif status == 2:
                logger.info('Connected to wifi, but no IP address')
            elif status == 3:
                logger.info('Connected to wifi with an IP address')
                return True
            timeout -= 1
            time.sleep(1)
    else:
        logger.warning('There is no valid SSID/password pair.')
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
                        # write to conf/wifi.conf
                        wificonf_file = open('./conf/wifi.conf','w')
                        wificonf_file.write(newssid + ',' + newpassword)
                        wificonf_file.close()
                        geolocation_file = open('./conf/geolocation.conf','w')
                        geolocation_file.write(latitude + ',' + longitude)
                        geolocation_file.close()
                        # now send a confirmation page, wait ten seconds and reboot
                        #TODO
                        waiting_credentials = False
                        cl.close()
                        wlan.disconnect()
                        machine.soft_reset()

        except OSError as e:
            cl.close()
            print('connection closed')
