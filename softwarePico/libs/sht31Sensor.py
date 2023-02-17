"""
Module      sht31Sensor.py
Author      2023-01-04 Charles Geiser (https://www.dodeka.ch)

Purpose     Reads a Sensirion SHT31 temperature and humidity sensor connected
            to the i2c bus and provides the methods
                - getValues         returns a list of measurements [tC, tF, rH, dP]
                - printValues()     prints the measured values to the terminal as
                                        tC = 23.2 °C
                                        tF = 73.8 °F
                                        rH = 49.7 %
                                        dP = 12.1 °💧
Board       ESP8266
Firmware    micropython from https://micropython.org

References  https://github.com/kfricke/micropython-sht31

Usage       # Code in main program:
            from machine import Pin, I2C
            import sht31Sensor
            i2c = I2C(sda=Pin(4), scl=Pin(5))
            addr = i2c.scan()[0]
            sensorSHT31 = sht31.SHT31Sensor(i2c, addr)
            sensorSHT31.printValues()
            v = sensorSHT31.getValues()
            print('Dewpoint is %4.1f 💧°C' % v[3])
"""
from machine import I2C
from math import log
import time

SHT31_I2CADDR = const(0x44)

R_HIGH   = const(1)
R_MEDIUM = const(2)
R_LOW    = const(3)

class SHT31Sensor:
    _commands = {                   # commands: choose clock stretching true or false and
    	True: {                     #           one of the 3 repeatabilities
            R_HIGH   : b'\x2c\x06',
            R_MEDIUM : b'\x2c\x0d',
            R_LOW    : b'\x2c\x10'
            },
        False: {
            R_HIGH   : b'\x24\x00',
            R_MEDIUM : b'\x24\x0b',
            R_LOW    : b'\x24\x16'
            }
        }

    """
    Initializes a sensor object on the given I2C bus with 
    access via the specified address which defaults to 0x44 = 68
    """
    def __init__(self, i2c, addr=SHT31_I2CADDR):
        self._i2c = i2c
        self._addr = addr
        self._values = [0,0,0,0]

    """
    Sends the given buffer object over I2C to the sensor.
    """
    def _send(self, buf):
        self._i2c.writeto(self._addr, buf)

    """
    Read nBytes bytes from i2c object.
    Returns a bytearray as result.
    """
    def _recv(self, nBytes):
        return self._i2c.readfrom(self._addr, nBytes)

    """
    Read raw temperature and humidity from the sensor.
    No CRC checking is done.
    Returns a tuple (tCraw, rHraw).
    """
    def _getRawValues(self, r=R_HIGH, cs=True):
        self._send(self._commands[cs][r])
        time.sleep_ms(50)
        raw = self._recv(6)
        return (raw[0] << 8) + raw[1], (raw[3] << 8) + raw[4]

    def getValues(self, repeatability=R_HIGH, clockStretch=True):
        tCraw, rHraw = self._getRawValues(repeatability, clockStretch)
        self._values[0] = -45 + (175 * (tCraw / 65535))   # tC °C
        self._values[1] = -49 + (315 * (tCraw / 65535))   # tF °F
        self._values[2] = 100 * rHraw / 65535             # rH %
        k = log(self._values[2] / 100) + (17.62 * self._values[0]) / (243.12 + self._values[0])
        self._values[3] = 243.12 * k / (17.62 - k)       # t💧°C dewpoint
        return self._values

    def printValues(self, repeatability=R_HIGH, clockStretch=True):
        self.getValues(repeatability=R_HIGH, clockStretch=True)
        print('tC = %4.1f °C\ntF = %4.1f °F\nrH = %4.1f %%\ndP = %4.1f °💧\n' % (self._values[0], self._values[1], self._values[2], self._values[3]))
    