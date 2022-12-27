import machine
import network
import socket
import binascii

iam = machine.unique_id()
ssid = 'eigen'
ap = False

def connect_accesspoint():
    creds_file = open('./conf/wifi.conf')
    rawcreds = creds_file.read()
    ssid, password = rawcreds.split(',')
    ap = network.WLAN(network.STA_IF)
    ap.active(True)
    ap.connect(ssid, password)
    print(ap.isconnected())
    #wifi.conf found, trying to connect to the access point.
    # try to connect for a while, if can't connect, switch to credentials portal.

def serve_credentials_portal():
    print('running credentials portal')
    #last 8 digits of the System control CPUID register of the RP2040 chip
    passwd = binascii.hexlify(iam).decode('utf-8')[-8:]
    global ap
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=passwd)
    ap.active(True)
    while ap.active() == False:
        pass
    ipaddress = ap.ifconfig()[0]
    print('password is: ' + passwd)
    print('IP is: ' + ipaddress)
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
    print('listening on ', addrinfo)
    # Listen for connections
    waiting_credentials = True
    while waiting_credentials:
        try:
            cl, addr = s.accept()
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            cl.send(html_form)
            print('client connected from', addr)
            request = cl.recv(1024)
            request = str(request.decode('utf-8'))
            reqstrings = request.split("\r\n")
            for part in reqstrings:
                if 'GET /?' in part:
                    subparts = part.split("&")
                    if 'text-password=' in subparts[1]:
                        newpassword = subparts[1].split('=')[1]
                        print('newpassword = ' + newpassword)
                        newssid = subparts[0].split('=')[1]
                        print('newssid = ' + newssid)
                        # validate ssid and password
                        #TODO
                        # write to conf/wifi.conf
                        wificonf_file = open('./conf/wifi.conf','w')
                        wificonf_file.write(newssid + ',' + newpassword)
                        wificonf_file.close()
                        # now send a confirmation page, wait ten seconds and reboot
                        #TODO
                        waiting_credentials = False
                        cl.close()
                        ap.disconnect()
                        machine.soft_reset()

        except OSError as e:
            cl.close()
            print('connection closed')