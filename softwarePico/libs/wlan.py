#import rp2 #problems finding SSID when rp2.country is set
import machine
import network
import socket
import binascii
import time
from libs import logger, config, leadacid
from libs.cron import feed_wdt

wlan = None
trying = False
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
    feed_wdt()
    time.sleep_ms(200)
    if not hasattr(config,'wlan'):
        serve_captive_portal()
    return connect(0)

def turn_off():
    global wlan
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
    if wlan is None:
        return initialize()
    if wlan.status() == 3:
        return True
    else:
        return False

def connect(wifiNumber=0):
    feed_wdt()
    global wlan, trying
    #rp2.country(config.wlan['country_code'])
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    ssid = "SSID_" + str(wifiNumber)
    password = "PASSW_" + str(wifiNumber)
    if ssid in config.wlan:
        ssid, password = config.wlan[ssid], config.wlan[password]
        try:
            wlan.connect(ssid, password)
        except Exception:
            logger.error('Wrong wifi credentials')
        timeout = config.wlan['connection_timeout']
        prev_status = -4
        while timeout > 0:
            feed_wdt()
            status = wlan.status()
            if prev_status != status:
                logger.info(statuses[status])
                prev_status = status
            if status == 3:
                time.sleep_ms(100)
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
    from sys import version
    from libs.sensors import sensorlist
    from libs.microdot import Microdot, Response
    app = Microdot()
    Response.default_content_type = 'text/html'
    iam = machine.unique_id()
    if config.station['UID'] is None:
        iutf8 = binascii.hexlify(iam).decode('utf-8')
        config.set('station','UID', iutf8)

    @app.get('/restart')
    def restart(request):
        request.app.shutdown()
        machine.reset()

    @app.post('/')
    def save_settings(request):
        print(request.body)

    @app.get('/')
    def load_form(request):
        log_lines = []
        try:
            with open('/logs/' + logger.logfile, 'r') as f:
                log_lines = f.readlines()
        except Exception as e:
            print("Could not read file: /logs/" + logger.logfile)
            print(e)
        lastlog_txt = "\n".join(log_lines)
        leadacid_levels = leadacid.levels()
        html_portal = open('/html/portal.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_wlan_SSID_0 = config.wlan['SSID_0'],
            cfg_wlan_PASSW_0 = config.wlan['PASSW_0'],
            cfg_wlan_SSID_AP = config.wlan['AP_SSID'],
            cfg_wlan_PASSW_AP = config.wlan['AP_PASSW'],
            cfg_cron_measurements_per_day = str(config.cron['measurements_per_day']),
            cfg_datalogger_URL = config.datalogger['URL'],
            cfg_cron_NTP_server = config.cron['NTP_server'],
            cfg_cron_NTPsync_interval = int(config.cron['NTPsync_interval']/3600),
            cfg_cron_update_interval = int(config.cron['update_interval']/3600),
            cfg_cron_data_submission_interval = int(config.cron['data_submission_interval']/60),
            cfg_cron_data_submission_just_in_time = 1 if config.cron['data_submission_just_in_time'] else 0,
            cfg_cron_data_submission_on_daylight = 1 if config.cron['data_submission_on_daylight'] else 0,
            cfg_cron_morning = config.cron['morning'],
            cfg_cron_evening = config.cron['evening'],
            latest_log = lastlog_txt,
            cfg_logger_loglevel = config.logger['loglevel'],
            cfg_logger_logfileCount = config.logger['logfileCount'],
            cfg_logger_print_log = 1 if config.logger['print_log'] else 0,
            cfg_cron_use_wdt = 1 if config.cron['use_wdt'] else 0,
            cfg_sensors_enable_sensors = 1 if config.sensors['enable_sensors'] else 0,
            cfg_cron_repository = config.cron['repository'],
            cfg_station_longitude = str(config.station['longitude']),
            cfg_station_latitude = str(config.station['latitude']),
            cfg_station_UID = config.station['UID'],
            cfg_station_serial = config.station['station'],
            cfg_status_temperature = leadacid_levels[0],
            cfg_status_percentage = leadacid_levels[1],
            cfg_status_vvvoltage = leadacid_levels[2],
            cfg_status_is_charging = leadacid_levels[3],
            cfg_sensor_preheating_s = config.cron['sensor_preheating_s'],
            cfg_average_particle_measurements = config.sensors['average_particle_measurements'],
            cfg_average_measurement_interval_ms = int(config.sensors['average_measurement_interval_ms']/1000),
            cfg_cron_current_version = config.cron['current_version'],
            cfg_cron_last_update_check = logger.timetuple_to_DTF(time.gmtime(config.cron['last_update_check'])),
            cfg_micropython_version = version,
            sensors_list = sensorlist())
    wlan = network.WLAN(network.AP_IF)
    passwd = binascii.hexlify(iam).decode('utf-8')[-8:]
    wlan.config(essid=config.wlan['AP_SSID'], password=config.wlan['AP_PASSW'])
    wlan.active(True)
    while wlan.active() is False:
        pass
    print(wlan.ifconfig()[0])
    # now wait for a connection
    while wlan.isconnected() is False:
        pass
    app.run(port=80)
    #wlan.disconnect()
    #machine.soft_reset()
            # request = str(request.decode('utf-8'))
            # reqstrings = request.split("\r\n")
            # for part in reqstrings:
                # if 'GET /?' in part:
                    # subparts = part.split("&")
                    # if 'text-password=' in subparts[1]:
                        # newpassword = subparts[1].split('=')[1]
                        # newssid = subparts[0].split('=')[1]
                    # if 'text-latitude' in subparts[2]:
                        # latitude = subparts[2].split('=')[1]
                    # if 'text-longitude' in subparts[3]:
                        # longitude = subparts[3].split('=')[1]
                        # # validate field input
                        # #TODO
                        # exist_wifi = True
                        # wifiNumber = 0
                        # while exist_wifi:
                            # wifiNumber += 1
                            # ssid = "SSID_" + str(wifiNumber)
                            # exist_wifi = ssid in config.wlan
                        # config.set('wlan',"SSID_" + str(wifiNumber),newssid)
                        # config.set('wlan',"PASSW_" + str(wifiNumber),newpassword)
                        # config.set('station',"latitude",latitude)
                        # config.set('station',"longitude",longitude)
                        # now send a confirmation page, wait ten seconds and reboot
                        #TODO
