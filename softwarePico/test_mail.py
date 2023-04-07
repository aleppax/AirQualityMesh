# Complete project details: https://RandomNerdTutorials.com/micropython-send-emails-esp32-esp826/
# Micropython lib to send emails: https://github.com/shawwwn/uMail
from libs import umail,config
import network

# Your network credentials
ssid =  'TIM-XXX'
password =  'XXX'
ssid, password = config.wlan['SSID_0'], config.wlan['PASSW_0']

# Email details
sender_email = 'stationpm02@gmail.com'
sender_name = 'OPMStation02' #sender name
sender_app_password = 'unapassworddifantasia'
recipient_email ='rob.ferrero@gmail.com'
email_subject ='Message from NowhereInTime'

def connect_wifi(ssid, password):
  #Connect to your network
  station = network.WLAN(network.STA_IF)
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:
    pass
  print('Connection successful')
  print(station.ifconfig())
    
# Connect to your network
connect_wifi(ssid, password)

# Send the email
smtp = umail.SMTP('smtp.gmail.com', 465, ssl=True) # Gmail's SSL port
smtp.login(sender_email, sender_app_password)
smtp.to(recipient_email)
smtp.write("From:" + sender_name + "<"+ sender_email+">\n")
smtp.write("Subject:" + email_subject + "\n")
smtp.write("Hello from PicoW of the oPMs02")
smtp.send()
smtp.quit()