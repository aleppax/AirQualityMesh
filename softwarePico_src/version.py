version = 65
folders = ['/', '/libs', '/html', '/logs']
#updates or new files. this file is manually updated and can only add or modify files or add folders
updated_files = {
    '/'     : ['main.py','opms.py'], # there is no need to include version.py
    '/libs/' : ['ahtx0.py','bmp280.py','config.py','cron.py','datalogger.py','filelogger.py','__init__.py','leadacid.py','logger.py','microdot.py','mqttlogger.py','picosngcja5.py','pms5003.py','qmc5883.py','sensors.py','simple.py','sps30.py','wlan.py'],
    '/logs/' : [],
    '/html/' : ['portal.html', 'portal-advanced.html', 'portal-basic.html', 'portal-datalogger.html', 'portal-mqtt.html', 'portal-network.html', 'portal-status.html', 'portal-syslogger.html'], 
}
# full update requires a list of all files
all_files = {
    '/'     : ['main.py','opms.py'], # there is no need to include version.py
    '/libs/' : ['ahtx0.py','bmp280.py','config.py','cron.py','datalogger.py','filelogger.py','__init__.py','leadacid.py','logger.py','microdot.py','mqttlogger.py','picosngcja5.py','pms5003.py','qmc5883.py','sensors.py','simple.py','sps30.py','wlan.py'],
    '/logs/' : [],
    '/html/' : ['portal.html', 'portal-advanced.html', 'portal-basic.html', 'portal-datalogger.html', 'portal-mqtt.html', 'portal-network.html', 'portal-status.html', 'portal-syslogger.html'], 
}
