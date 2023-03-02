from libs import logger , config, wlan
from libs.cron import wdt
from time import localtime
import urequests as requests
import ujson

url_site = "https://lettori.org"   #RR  da metter in config 
str_post_measure = "/opms/api.php/records/measurements"  #RR  da metter in config 

url_post_measure = url_site + str_post_measure

headers = ""
#headers["Content-Type"] = "application/json"

data = """

  {
    "station": 1,
    "datetime": "2023-01-27",
    "humidity": "50.1234",
    "temperature": "15.55",
    "pm1.0": "10.11",
    "pm2.5": "25.55",
    "pm4": "",
    "pm10": "100.1",
    "pm1.0_ch2": "",
    "pm2.5_ch2": "",
    "pm4_ch2": "",
    "pm10_ch2": "",
    "sound pressure": "",
    "barometric pressure": "",
    "battery charge percentage": "",
    "O3": "",
    "NO2": "",
    "internal temperature": "",
    "wind direction": "",
    "wind speed": ""
  }
"""

datajson = ujson.loads(data)

def init():
    wdt.feed()
    logger.info('DB connected')

def dbpub_measure_test(wlan,txt):
    wdt.feed()
    yr, mo, md, h, m, s, wd = localtime()[:7]
    fst = '{} {:02d}:{:02d}:{:02d} on {:02d}/{:02d}/{:02d}'
    print(fst.format(txt, h, m, s, md, mo, yr))
    
    t,h = 23.456, 55.5
    
    pm4_ch2 = 111.1
    
    data_empty = """
  {
    "station": 2,
    "datetime": "",
    "humidity": "",
    "temperature": "",
    "pm1.0": "",
    "pm2.5": "",
    "pm4": "",
    "pm10": "",
    "pm1.0_ch2": "",
    "pm2.5_ch2": "",
    "pm4_ch2": "",
    "pm10_ch2": ""
  }
"""

    print('post value', url_post_measure)
    datajson = ujson.loads(data_empty)
    
    yr, mo, md, h, m, s, wd = localtime()[:7]
    oggi = '{:02d}-{:02d}-{:02d}@{:02d}:{:02d}:{:02d}'
    print(oggi.format(md, mo, yr, h, m, s ))
    datajson["datetime"] = oggi.format(md, mo, yr, h, m, s )
    
    datajson["humidity"] = h
    datajson["temperature"] = t
    
    datajson["pm4_ch2"] = pm4_ch2

    data = ujson.dumps(datajson)
 
    try:
        requests.HTTP__version__ = "1.1"  #force HTTP 1.1 
        r = requests.post(url_post_measure ,  headers = headers, data= data)   #RRR todo post
        print('text: ',r.text)
    #     print('json: ', r.json)    
    #    headers = r.headers
    #    print('headers: ',headers)
    except Exception as e:
        print(e)

def dbpub_measures(measures,txt):
    wdt.feed()
    yr, mo, md, h, m, s, wd = localtime()[:7]
    fst = '{} {:02d}:{:02d}:{:02d} on {:02d}/{:02d}/{:02d}'
    print(fst.format(txt, h, m, s, md, mo, yr))
    
    t, h = measures['temperature'], measures['humidity']
    md_pm10,  md_pm2_5,  md_pm1_0 = measures['pm10'], measures['pm2.5'], measures['pm1.0']  # Panasonic SNGCJA5 PM sensor
    md_pm10_ch2, md_pm2_5_ch2, md_pm4_0_ch2, md_pm1_0_ch2 = measures['pm10_ch2'], measures['pm2.5_ch2'], measures['pm4_ch2'], measures['pm1.0_ch2']  # Sensirion SPS30 PM sensor
      
    data_empty = """
  {
    "station": 2,
    "datetime": "",
    "humidity": "",
    "temperature": "",
    "pm1.0": "",
    "pm2.5": "",
    "pm4": "",
    "pm10": "",
    "pm1.0_ch2": "",
    "pm2.5_ch2": "",
    "pm4_0_ch2": "",
    "pm10_ch2": ""
  }
"""

    print('post value', url_post_measure)
    datajson = ujson.loads(data_empty)
    
    yr, mo, md, h, m, s, wd = localtime()[:7]
    oggi = '{:02d}-{:02d}-{:02d}@{:02d}:{:02d}:{:02d}'
    print(oggi.format(md, mo, yr, h, m, s ))
    datajson["datetime"] = oggi.format(md, mo, yr, h, m, s )
    
    datajson["humidity"] = h
    datajson["temperature"] = t
    datajson["pm1.0"] = md_pm1_0
    datajson["pm2.5"] = md_pm2_5
#    datajson["pm4"] = md_pm4
    datajson["pm10"] = md_pm10
    datajson["pm1.0_ch2"] = md_pm1_0_ch2
    datajson["pm2.5_ch2"] = md_pm2_5_ch2
    datajson["pm4_0_ch2"] = md_pm4_0_ch2
    datajson["pm10_ch2"] = md_pm10_ch2

    data = ujson.dumps(datajson)
 
    try:
        requests.HTTP__version__ = "1.1"  #force HTTP 1.1 
        r = requests.post(url_post_measure ,  headers = headers, data= data)   #RRR todo post
        print('text: ',r.text)
    #     print('json: ', r.json)    
    #    headers = r.headers
    #    print('headers: ',headers)
    except Exception as e:
        print(e)

