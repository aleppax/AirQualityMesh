from libs import config, cron, leadacid, logger, wlan

# init logger
logger.info('booting')
# init network
wlan.initialize()
# init RTC
cron.initialize()


