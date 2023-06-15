#import rp2 #problems finding SSID when rp2.country is set
import machine
import network
import socket
import binascii
import time
from libs import logger, config, leadacid
from libs.cron import feed_wdt, pause_wdt

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
    pause_wdt()
    global wlan
    from sys import version
    from libs.sensors import sensorlist
    from libs.microdot import Microdot, Response, redirect
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

    @app.get('/')
    def redirect_basic(request):
        return redirect('/basic')
    
    @app.post('/basic')
    def save_basic_settings(request):
        logger.info(request.body)
        SSID_0 = request.form.get('cfg_wlan_SSID_0')
        PASSW_0 = request.form.get('cfg_wlan_PASSW_0')
        AP_SSID = request.form.get('cfg_wlan_SSID_AP')
        AP_PASSW = request.form.get('cfg_wlan_PASSW_AP')
        measurements_per_day = int(request.form.get('measures-per-day'))
        URL = request.form.get('datalogger-url')
        longitude = float(request.form.get('text-longitude'))
        latitude = float(request.form.get('text-latitude'))
        # for each setting, write to config if is changed
        if SSID_0 is not config.wlan['SSID_0']:
            config.set('wlan','SSID_0', SSID_0)
        if PASSW_0 is not config.wlan['PASSW_0']:
            config.set('wlan','PASSW_0', PASSW_0)
        if AP_SSID is not config.wlan['AP_SSID']:
            config.set('wlan','AP_SSID', AP_SSID)
        if AP_PASSW is not config.wlan['AP_PASSW']:
            config.set('wlan','AP_PASSW', AP_PASSW)
        if measurements_per_day is not config.cron['measurements_per_day']:
            config.set('cron','measurements_per_day', measurements_per_day)
        if URL is not config.datalogger['URL']:
            config.set('datalogger','URL', URL)
        if longitude is not config.station['longitude']:
            config.set('station','longitude', longitude)
        if latitude is not config.station['latitude']:
            config.set('station','latitude', latitude)

    @app.get('/basic')
    def load_form(request):
        html_portal = open('/html/portal-basic.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_wlan_SSID_0 = config.wlan['SSID_0'],
            cfg_wlan_PASSW_0 = config.wlan['PASSW_0'],
            cfg_wlan_SSID_AP = config.wlan['AP_SSID'],
            cfg_wlan_PASSW_AP = config.wlan['AP_PASSW'],
            cfg_cron_measurements_per_day = str(config.cron['measurements_per_day']),
            cfg_datalogger_URL = config.datalogger['URL'],
            cfg_station_longitude = str(config.station['longitude']),
            cfg_station_latitude = str(config.station['latitude']))

    @app.post('/mqtt')
    def save_mqtt_settings(request):
        logger.info(request.body)
        mqtt_enable = True if request.form.get('mqtt_enable') is 'on' else False
        cfg_mqtt_server = request.form.get('cfg_mqtt_server')
        cfg_mqtt_topic = request.form.get('cfg_mqtt_topic').encode('utf-8')
        cfg_mqtt_user = None if request.form.get('cfg_mqtt_user') is 'None' else request.form.get('cfg_mqtt_user')
        cfg_mqtt_pass = None if request.form.get('cfg_mqtt_pass') is 'None' else request.form.get('cfg_mqtt_pass')
        cfg_mqtt_QOS = int(request.form.get('cfg_mqtt_QOS'))
        # for each setting, write to config if is changed
        if mqtt_enable is not config.mqttlogger['enable']:
            config.set('mqttlogger','enable', mqtt_enable)
        if cfg_mqtt_server is not config.mqttlogger['server']:
            config.set('mqttlogger','server', cfg_mqtt_server)
        if cfg_mqtt_topic is not config.mqttlogger['topic']:
            config.set('mqttlogger','topic', cfg_mqtt_topic)
        if cfg_mqtt_user is not config.mqttlogger['user']:
            config.set('mqttlogger','user', cfg_mqtt_user)
        if cfg_mqtt_pass is not config.mqttlogger['pass']:
            config.set('mqttlogger','pass', cfg_mqtt_pass)
        if cfg_mqtt_QOS is not config.mqttlogger['QOS']:
            config.set('mqttlogger','QOS', cfg_mqtt_QOS)

    @app.get('/mqtt')
    def load_mqtt(request):
        html_portal = open('/html/portal-mqtt.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_mqtt_enable = 'checked' if config.mqttlogger['enable'] else '',
            cfg_mqtt_server = config.mqttlogger['server'],
            cfg_mqtt_topic = config.mqttlogger['topic'].decode('utf-8'),
            cfg_mqtt_user = config.mqttlogger['user'],
            cfg_mqtt_pass = config.mqttlogger['pass'],
            cfg_mqtt_QOS = str(config.mqttlogger['QOS']))

    @app.get('/status')
    def load_status(request):
        leadacid_levels = leadacid.levels()
        html_portal = open('/html/portal-status.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_station_UID = config.station['UID'],
            cfg_station_serial = config.station['station'],
            cfg_status_temperature = leadacid_levels[0],
            cfg_status_percentage = leadacid_levels[1],
            cfg_status_vvvoltage = leadacid_levels[2],
            cfg_status_is_charging = leadacid_levels[3],
            cfg_cron_current_version = config.cron['current_version'],
            cfg_cron_last_update_check = logger.timetuple_to_DTF(time.gmtime(config.cron['last_update_check'])),
            cfg_micropython_version = version,
            sensors_list = sensorlist())

    @app.post('/network')
    def save_network_settings(request):
        logger.info(request.body)
        SSID_0 = request.form.get('cfg_wlan_SSID_0')
        PASSW_0 = request.form.get('cfg_wlan_PASSW_0')
        AP_SSID = request.form.get('cfg_wlan_SSID_AP')
        AP_PASSW = request.form.get('cfg_wlan_PASSW_AP')
        URL = request.form.get('datalogger-url')
        NTP_server = request.form.get('NTP-url')
        NTPsync_interval = int(request.form.get('NTPsync_interval'))*3600
        update_interval = int(request.form.get('update_interval'))*3600
        repository = request.form.get('repository')
        # for each setting, write to config if is changed
        if SSID_0 is not config.wlan['SSID_0']:
            config.set('wlan','SSID_0', SSID_0)
        if PASSW_0 is not config.wlan['PASSW_0']:
            config.set('wlan','PASSW_0', PASSW_0)
        if AP_SSID is not config.wlan['AP_SSID']:
            config.set('wlan','AP_SSID', AP_SSID)
        if AP_PASSW is not config.wlan['AP_PASSW']:
            config.set('wlan','AP_PASSW', AP_PASSW)
        if URL is not config.datalogger['URL']:
            config.set('datalogger','URL', URL)
        if NTP_server is not config.cron['NTP_server']:
            config.set('cron','NTP_server', NTP_server)
        if NTPsync_interval is not config.cron['NTPsync_interval']:
            config.set('cron','NTPsync_interval', NTPsync_interval)
        if update_interval is not config.cron['update_interval']:
            config.set('cron','update_interval', update_interval)
        if repository is not config.cron['repository']:
            config.set('cron','repository', repository)

    @app.get('/network')
    def load_network(request):
        html_portal = open('/html/portal-network.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_wlan_SSID_0 = config.wlan['SSID_0'],
            cfg_wlan_PASSW_0 = config.wlan['PASSW_0'],
            cfg_wlan_SSID_AP = config.wlan['AP_SSID'],
            cfg_wlan_PASSW_AP = config.wlan['AP_PASSW'],
            cfg_datalogger_URL = config.datalogger['URL'],
            cfg_cron_NTP_server = config.cron['NTP_server'],
            cfg_cron_NTPsync_interval = int(config.cron['NTPsync_interval']/3600),
            cfg_cron_update_interval = int(config.cron['update_interval']/3600),
            cfg_cron_repository = config.cron['repository'])

    @app.post('/datalogger')
    def save_datalogger_settings(request):
        logger.info(request.body)
        measurements_per_day = int(request.form.get('measures-per-day'))
        URL = request.form.get('datalogger-url')
        data_submission_interval = int(request.form.get('data_submission_interval'))*60
        data_submission_just_in_time = True if request.form.get('data_submission_just_in_time') is 'on' else False
        data_submission_on_daylight = True if request.form.get('data_submission_on_daylight') is 'on' else False
        morning = int(request.form.get('morning'))
        evening = int(request.form.get('evening'))
        average_measurements = int(request.form.get('average_measurements'))
        average_measurement_interval_ms = int(request.form.get('average_interval_ms'))*1000
        # for each setting, write to config if is changed
        if measurements_per_day is not config.cron['measurements_per_day']:
            config.set('cron','measurements_per_day', measurements_per_day)
        if URL is not config.datalogger['URL']:
            config.set('datalogger','URL', URL)
        if data_submission_interval is not config.cron['data_submission_interval']:
            config.set('cron','data_submission_interval', data_submission_interval)
        if data_submission_just_in_time is not config.cron['data_submission_just_in_time']:
            config.set('cron','data_submission_just_in_time', data_submission_just_in_time)
        if data_submission_on_daylight is not config.cron['data_submission_on_daylight']:
            config.set('cron','data_submission_on_daylight', data_submission_on_daylight)
        if morning is not config.cron['morning']:
            config.set('cron','morning', morning)
        if evening is not config.cron['evening']:
            config.set('cron','evening', evening)
        if average_measurements is not config.sensors['average_particle_measurements']:
            config.set('sensors','average_particle_measurements', average_measurements)
        if average_measurement_interval_ms is not config.sensors['average_measurement_interval_ms']:
            config.set('sensors','average_measurement_interval_ms', average_measurement_interval_ms)

    @app.get('/datalogger')
    def load_datalogger(request):
        html_portal = open('/html/portal-datalogger.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_cron_measurements_per_day = str(config.cron['measurements_per_day']),
            cfg_datalogger_URL = config.datalogger['URL'],
            cfg_cron_data_submission_interval = int(config.cron['data_submission_interval']/60),
            cfg_cron_data_submission_just_in_time = 'checked' if config.cron['data_submission_just_in_time'] else '',
            cfg_cron_data_submission_on_daylight = 'checked' if config.cron['data_submission_on_daylight'] else '',
            cfg_cron_morning = config.cron['morning'],
            cfg_cron_evening = config.cron['evening'],
            average_measurements = config.sensors['average_particle_measurements'],
            average_interval_ms = int(config.sensors['average_measurement_interval_ms']/1000))

    @app.post('/syslogger')
    def save_syslogger_settings(request):
        logger.info(request.body)
        loglevel = int(request.form.get('loglevel'))
        logfileCount = int(request.form.get('logfileCount'))
        print_log = True if request.form.get('print_log') is 'on' else False
        # for each setting, write to config if is changed
        if loglevel is not config.logger['loglevel']:
            config.set('logger','loglevel', loglevel)
        if logfileCount is not config.logger['logfileCount']:
            config.set('logger','logfileCount', logfileCount)
        if print_log is not config.logger['print_log']:
            config.set('logger','print_log', print_log)

    @app.get('/syslogger')
    def load_syslogger(request):
        log_lines = []
        try:
            with open('/logs/' + logger.logfile, 'r') as f:
                log_lines = f.readlines()
        except Exception as e:
            print("Could not read file: /logs/" + logger.logfile)
            print(e)
        lastlog_txt = "\n".join(log_lines)
        html_portal = open('/html/portal-syslogger.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            latest_log = lastlog_txt,
            cfg_logger_loglevel = config.logger['loglevel'],
            cfg_logger_logfileCount = config.logger['logfileCount'],
            cfg_logger_print_log = 'checked' if config.logger['print_log'] else '')

    @app.post('/advanced')
    def save_advanced_settings(request):
        logger.info(request.body)
        use_wdt = True if request.form.get('use_wdt') is 'on' else False
        enable_sensors = True if request.form.get('enable_sensors') is 'on' else False
        repository = request.form.get('repository')
        sensor_preheating_s = request.form.get('sensor_preheating_s')
        # for each setting, write to config if is changed
        if use_wdt is not config.cron['use_wdt']:
            config.set('cron','use_wdt', use_wdt)
        if enable_sensors is not config.sensors['enable_sensors']:
            config.set('sensors','enable_sensors', enable_sensors)
        if repository is not config.cron['repository']:
            config.set('cron','repository', repository)
        if sensor_preheating_s is not config.cron['sensor_preheating_s']:
            config.set('cron','sensor_preheating_s', sensor_preheating_s)

    @app.get('/advanced')
    def load_advanced(request):
        html_portal = open('/html/portal-advanced.html')
        html_form = html_portal.read()
        html_portal.close()
        return html_form.format(
            cfg_cron_use_wdt = 'checked' if config.cron['use_wdt'] else '',
            enable_sensors = 'checked' if config.sensors['enable_sensors'] else '',
            cfg_cron_repository = config.cron['repository'],
            cfg_sensor_preheating_s = config.cron['sensor_preheating_s'])

    # activate wifi
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
