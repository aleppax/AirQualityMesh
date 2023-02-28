version = 3
folders = ['/', '/libs', '/html', '/logs']
#updates or new files. this file is manually updated and can only add or modify files or add folders
updated_files = {
    '/'     : ['main.py',], # there is no need to include version.py
    '/libs' : ['datalogger.py','config.py',],
    '/html' : [], 
}
# full update requires a list of all files
all_files = {
    '/'     : ['main.py',], # there is no need to include version.py
    '/libs' : ['ahtx0.py','config.py','__init__.py','logger.py','datalogger.py','sensors.py','wlan.py','bmp280.py','cron.py','leadacid.py','picosngcja5.py','sps30.py'],
    '/logs' : [],
    '/html' : ['portal.html'], 
}
