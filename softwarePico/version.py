version = 6
folders = ['/', '/libs', '/html', '/logs']
#updates or new files. this file is manually updated and can only add or modify files or add folders
updated_files = {
    '/'     : ['main.py'], # there is no need to include version.py
    '/libs' : ['cron.py'],
    '/html' : [], 
}
# full update requires a list of all files
all_files = {
    '/'     : ['main.py',], # there is no need to include version.py
    '/libs' : ['ahtx0.py','bmp280.py','config.py','cron.py','datalogger.py','filelogger.py','__init__.py','leadacid.py','logger.py','picosngcja5.py','sensors.py','sps30.py','wlan.py'],
    '/logs' : [],
    '/html' : ['portal.html'], 
}
