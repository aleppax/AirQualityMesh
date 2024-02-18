version = 67
folders = ['/', '/libs', '/html', '/logs']
#updates or new files. this file is manually updated and can only add or modify files or add folders
updated_files = {
    '/'     : [],
    '/libs/' : ['config.py','sensors.mpy'],
    '/logs/' : [],
    '/html/' : [], 
}
# full update requires a list of all files
all_files = {
    '/'     : ['main.py','opms.mpy'], # there is no need to include version.py
    '/libs/' : ['ahtx0.mpy','bmp280.mpy','config.py','cron.mpy','datalogger.mpy','filelogger.mpy','__init__.py','leadacid.mpy','logger.mpy','microdot.mpy','micropyGPS.mpy','mqttlogger.mpy','neo6m.mpy','picosngcja5.mpy','pms5003.mpy','qmc5883.mpy','sensors.mpy','simple.mpy','sps30.mpy','wlan.mpy'],
    '/logs/' : [],
    '/html/' : ['portal.html', 'portal-advanced.html', 'portal-basic.html', 'portal-datalogger.html', 'portal-mqtt.html', 'portal-network.html', 'portal-status.html', 'portal-syslogger.html', 'portal-opensensemap.html'], 
}
