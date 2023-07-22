from libs import wlan, datalogger, filelogger
import micropython

micropython.alloc_emergency_exception_buf(100)

missinglines = 1  # per ciclare
while missinglines >0:
    wlan.connect()
    file_lines = filelogger.read()
    inviate = datalogger.send_data_list(file_lines)
    print (inviate)
    if inviate:  # true = è riuscito a inviare
        missinglines = filelogger.write_remaining_data()
    else:
        missinglines=0
