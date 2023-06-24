# The source code is taken from the following repository 
# https://github.com/dvsu/sps30.git
# original license: MIT License
# Copyright (c) 2021 Dave
# and is adapted to the Raspberry Pi Pico by Leo Rutten (lrutten)
# https://github.com/lrutten/rpi-pico-python-sps30-demo.git
# The code is furthermore adapted by Aleppax
# to accept a different I2C connection

# also consider checking which firmware version has your sensor
# and read this: https://github.com/dvsu/sps30/issues/1

import sys
from time import sleep

# I2C commands
CMD_START_MEASUREMENT = [0x00, 0x10]
CMD_STOP_MEASUREMENT = [0x01, 0x04]
CMD_READ_DATA_READY_FLAG = [0x02, 0x02]
CMD_READ_MEASURED_VALUES = [0x03, 0x00]
CMD_SLEEP = [0x10, 0x01]
CMD_WAKEUP = [0x11, 0x03]
CMD_START_FAN_CLEANING = [0x56, 0x07]
CMD_AUTO_CLEANING_INTERVAL = [0x80, 0x04]
CMD_PRODUCT_TYPE = [0xD0, 0x02]
CMD_SERIAL_NUMBER = [0xD0, 0x33]
CMD_FIRMWARE_VERSION = [0xD1, 0x00]
#CMD_FIRMWARE_VERSION = bytearray(b"\xD1\x00")
CMD_READ_STATUS_REGISTER = [0xD2, 0x06]
CMD_CLEAR_STATUS_REGISTER = [0xD2, 0x10]
CMD_RESET = [0xD3, 0x04]

# Length of response in bytes
NBYTES_READ_DATA_READY_FLAG = 3
NBYTES_MEASURED_VALUES_FLOAT = 60  # IEEE754 float
NBYTES_MEASURED_VALUES_INTEGER = 30  # unsigned 16 bit integer
NBYTES_AUTO_CLEANING_INTERVAL = 6
NBYTES_PRODUCT_TYPE = 12
NBYTES_SERIAL_NUMBER = 48
NBYTES_FIRMWARE_VERSION = 3
NBYTES_READ_STATUS_REGISTER = 6

# Packet size including checksum byte [data1, data2, checksum]
PACKET_SIZE = 3

# Size of each measurement data packet (PMx) including checksum bytes, in bytes
SIZE_FLOAT = 6  # IEEE754 float
SIZE_INTEGER = 3  # unsigned 16 bit integer


class SPS30:

    def __init__(self,  i2c, address: int = 0x69, sampling_period: int = 1, logger: str = None):
        self.logger = None
        if logger:
            self.logger = logger
        self.addr = address
        self.sampling_period = sampling_period
        self.i2c = i2c
        self.__data = {}
        self.__valid = {
            "mass_density": False,
            "particle_count": False,
            "particle_size": False
        }

    def crc_calc(self, data: list) -> int:
        crc = 0xFF
        for i in range(2):
            crc ^= data[i]
            for _ in range(8, 0, -1):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1

        # The checksum only contains 8-bit,
        # so the calculated value has to be masked with 0xFF
        return (crc & 0x0000FF)

    def firmware_version(self) -> str:
        print(f"self.addr {self.addr}")
        #self.i2c.writeto(self.addr, CMD_FIRMWARE_VERSION)
        #self.i2c.write(CMD_FIRMWARE_VERSION)
        #temp = bytearray(2)
        #temp[0] = CMD_FIRMWARE_VERSION[0]
        #temp[1] = CMD_FIRMWARE_VERSION[1]
        #self.i2c.writeto(self.addr, temp)
        self.i2c.writeto(self.addr, bytearray(CMD_FIRMWARE_VERSION))
        data = self.i2c.readfrom(self.addr, NBYTES_FIRMWARE_VERSION)

        if self.crc_calc(data[:2]) != data[2]:
            return "CRC mismatched"

        return ".".join(map(str, data[:2]))

    def product_type(self) -> str:
        self.i2c.writeto(self.addr, bytearray(CMD_PRODUCT_TYPE))
        data = self.i2c.readfrom(self.addr, NBYTES_PRODUCT_TYPE)
        sps_result = ""

        for i in range(0, NBYTES_PRODUCT_TYPE, 3):
            if self.crc_calc(data[i:i+2]) != data[i+2]:
                return "CRC mismatched"

            sps_result += "".join(map(chr, data[i:i+2]))

        return sps_result

    def serial_number(self) -> str:
        self.i2c.writeto(self.addr, bytearray(CMD_SERIAL_NUMBER))
        data = self.i2c.readfrom(self.addr, NBYTES_SERIAL_NUMBER)
        spss_result = ""

        for i in range(0, NBYTES_SERIAL_NUMBER, PACKET_SIZE):
            if self.crc_calc(data[i:i+2]) != data[i+2]:
                return "CRC mismatched"

            spss_result += "".join(map(chr, data[i:i+2]))

        return spss_result

    def read_status_register(self) -> dict:
        self.i2c.writeto(self.addr, bytearray(CMD_READ_STATUS_REGISTER))
        data = self.i2c.readfrom(self.addr, NBYTES_READ_STATUS_REGISTER)

        status = []
        for i in range(0, NBYTES_READ_STATUS_REGISTER, PACKET_SIZE):
            if self.crc_calc(data[i:i+2]) != data[i+2]:
                return "CRC mismatched"

            status.extend(data[i:i+2])

        binary = '{:032b}'.format(
            status[0] << 24 | status[1] << 16 | status[2] << 8 | status[3])
        speed_status = "too high/ too low" if int(binary[10]) == 1 else "ok"
        laser_status = "out of range" if int(binary[26]) == 1 else "ok"
        fan_status = "0 rpm" if int(binary[27]) == 1 else "ok"

        return {
            "speed_status": speed_status,
            "laser_status": laser_status,
            "fan_status": fan_status
        }

    def clear_status_register(self) -> None:
        self.i2c.writeto(self.addr, bytearray(CMD_CLEAR_STATUS_REGISTER))

    def read_data_ready_flag(self) -> bool:
        self.i2c.writeto(self.addr, bytearray(CMD_READ_DATA_READY_FLAG))
        data = self.i2c.readfrom(self.addr, NBYTES_READ_DATA_READY_FLAG)

        if self.crc_calc(data[:2]) != data[2]:
            if self.logger:
                self.logger.warning(
                    "'read_data_ready_flag' CRC mismatched!" +
                    f"  Data: {data[:2]}" +
                    f"  Calculated CRC: {self.crc_calc(data[:2])}" +
                    f"  Expected: {data[2]}")
            else:
                print(
                    "'read_data_ready_flag' CRC mismatched!" +
                    f"  Data: {data[:2]}" +
                    f"  Calculated CRC: {self.crc_calc(data[:2])}" +
                    f"  Expected: {data[2]}")

            return False

        return True if data[1] == 1 else False

    def sleep(self) -> None:
        self.i2c.writeto(self.addr, bytearray(CMD_SLEEP))

    def _wakeup(self) -> None:
        self.i2c.writeto(self.addr, bytearray(CMD_WAKEUP))

    def start_fan_cleaning(self) -> None:
        self.i2c.writeto(self.addr, bytearray(CMD_START_FAN_CLEANING))

    def read_auto_cleaning_interval(self) -> int:
        self.i2c.writeto(self.addr, bytearray(CMD_AUTO_CLEANING_INTERVAL))
        data = self.i2c.readfrom(self.addr, NBYTES_AUTO_CLEANING_INTERVAL)

        interval = []
        for i in range(0, NBYTES_AUTO_CLEANING_INTERVAL, 3):
            if self.crc_calc(data[i:i+2]) != data[i+2]:
                return "CRC mismatched"

            interval.extend(data[i:i+2])

        return (interval[0] << 24 | interval[1] << 16 | interval[2] << 8 | interval[3])

    def write_auto_cleaning_interval_days(self, days: int) -> int:
        seconds = days * 86400  # 1day = 86400sec
        interval = []
        interval.append((seconds & 0xff000000) >> 24)
        interval.append((seconds & 0x00ff0000) >> 16)
        interval.append((seconds & 0x0000ff00) >> 8)
        interval.append(seconds & 0x000000ff)
        data = CMD_AUTO_CLEANING_INTERVAL
        data.extend([interval[0], interval[1]])
        data.append(self.crc_calc(data[2:4]))
        data.extend([interval[2], interval[3]])
        data.append(self.crc_calc(data[5:7]))
        self.i2c.writeto(self.addr, bytearray(data))
        sleep(0.05)
        return self.read_auto_cleaning_interval()

    def reset(self) -> None:
        self.i2c.writeto(self.addr, bytearray(CMD_RESET))

    def __ieee754_number_conversion(self, data: int) -> float:
        binary = "{:032b}".format(data)

        sign = int(binary[0:1])
        exp = int(binary[1:9], 2) - 127

        divider = 0
        if exp < 0:
            divider = abs(exp)
            exp = 0

        mantissa = binary[9:]

        real = int(('1' + mantissa[:exp]), 2)
        decimal = mantissa[exp:]

        dec = 0.0
        for i in range(len(decimal)):
            dec += int(decimal[i]) / (2**(i+1))

        if divider == 0:
            return round((((-1)**(sign) * real) + dec), 3)
        else:
            return round((((-1)**(sign) * real) + dec) / pow(2, divider), 3)

    def __mass_density_measurement(self, data: list) -> dict:
        category = ["pm1.0", "pm2.5", "pm4.0", "pm10"]

        density = {
            "pm1.0": 0.0,
            "pm2.5": 0.0,
            "pm4.0": 0.0,
            "pm10": 0.0
        }

        for block, (pm) in enumerate(category):
            pm_data = []
            for i in range(0, SIZE_FLOAT, PACKET_SIZE):
                offset = (block * SIZE_FLOAT) + i
                if self.crc_calc(data[offset:offset+2]) != data[offset+2]:
                    if self.logger:
                        self.logger.warning(
                            "'__mass_density_measurement' CRC mismatched!" +
                            f"  Data: {data[offset:offset+2]}" +
                            f"  Calculated CRC: {self.crc_calc(data[offset:offset+2])}" +
                            f"  Expected: {data[offset+2]}")
                    else:
                        print(
                            "'__mass_density_measurement' CRC mismatched!" +
                            f"  Data: {data[offset:offset+2]}" +
                            f"  Calculated CRC: {self.crc_calc(data[offset:offset+2])}" +
                            f"  Expected: {data[offset+2]}")
                    self.__valid["mass_density"] = False
                    return {}

                pm_data.extend(data[offset:offset+2])

            density[pm] = self.__ieee754_number_conversion(
                pm_data[0] << 24 | pm_data[1] << 16 | pm_data[2] << 8 | pm_data[3])

        self.__valid["mass_density"] = True

        return density

    def __particle_count_measurement(self, data: list) -> dict:
        category = ["pm0.5", "pm1.0", "pm2.5", "pm4.0", "pm10"]

        count = {
            "pm0.5": 0.0,
            "pm1.0": 0.0,
            "pm2.5": 0.0,
            "pm4.0": 0.0,
            "pm10": 0.0
        }

        for block, (pm) in enumerate(category):
            pm_data = []
            for i in range(0, SIZE_FLOAT, PACKET_SIZE):
                offset = (block * SIZE_FLOAT) + i
                if self.crc_calc(data[offset:offset+2]) != data[offset+2]:
                    if self.logger:
                        self.logger.warning(
                            "'__particle_count_measurement' CRC mismatched!" +
                            f"  Data: {data[offset:offset+2]}" +
                            f"  Calculated CRC: {self.crc_calc(data[offset:offset+2])}" +
                            f"  Expected: {data[offset+2]}")
                    else:
                        print(
                            "'__particle_count_measurement' CRC mismatched!" +
                            f"  Data: {data[offset:offset+2]}" +
                            f"  Calculated CRC: {self.crc_calc(data[offset:offset+2])}" +
                            f"  Expected: {data[offset+2]}")

                    self.__valid["particle_count"] = False
                    return {}

                pm_data.extend(data[offset:offset+2])

            count[pm] = self.__ieee754_number_conversion(
                pm_data[0] << 24 | pm_data[1] << 16 | pm_data[2] << 8 | pm_data[3])

        self.__valid["particle_count"] = True

        return count

    def __particle_size_measurement(self, data: list) -> float:
        size = []
        for i in range(0, SIZE_FLOAT, PACKET_SIZE):
            if self.crc_calc(data[i:i+2]) != data[i+2]:
                if self.logger:
                    self.logger.warning(
                        "'__particle_size_measurement' CRC mismatched!" +
                        f"  Data: {data[i:i+2]}" +
                        f"  Calculated CRC: {self.crc_calc(data[i:i+2])}" +
                        f"  Expected: {data[i+2]}")
                else:
                    print(
                        "'__particle_size_measurement' CRC mismatched!" +
                        f"  Data: {data[i:i+2]}" +
                        f"  Calculated CRC: {self.crc_calc(data[i:i+2])}" +
                        f"  Expected: {data[i+2]}")

                self.__valid["particle_size"] = False
                return 0.0

            size.extend(data[i:i+2])

        self.__valid["particle_size"] = True

        return self.__ieee754_number_conversion(size[0] << 24 | size[1] << 16 | size[2] << 8 | size[3])

    def __read_measured_value(self) -> None:
        running = True
        while running:
            try:
                if not self.read_data_ready_flag():
                    continue

                running = False
                self.i2c.writeto(self.addr, bytearray(CMD_READ_MEASURED_VALUES))
                data = self.i2c.readfrom(self.addr, NBYTES_MEASURED_VALUES_FLOAT)

                spsv_result = {
                        "mass_density": self.__mass_density_measurement(data[:24]),
                        "particle_count": self.__particle_count_measurement(data[24:54]),
                        "particle_size": self.__particle_size_measurement(data[54:]),
                        "mass_density_unit": "ug/m3",
                        "particle_count_unit": "#/cm3",
                        "particle_size_unit": "um"
                    }

                #print(f"result " + str(spsv_result))
                self.__data = spsv_result if all(self.__valid.values()) else {}

            except KeyboardInterrupt:
                if self.logger:
                    self.logger.warning("Stopping measurement...")
                else:
                    print("Stopping measurement...")

                self.stop_measurement()
                sys.exit()

            except Exception as e:
                if self.logger:
                    self.logger.warning(f"{type(e).__name__}: {e}")
                else:
                    print(f"{type(e).__name__}: {e}")

            finally:
                sleep(self.sampling_period)

    def start_measurement(self) -> None:
        data_format = {
            "IEEE754_float": 0x03,
            "unsigned_16_bit_integer": 0x05
        }

        data = CMD_START_MEASUREMENT
        data.extend([data_format["IEEE754_float"], 0x00])
        data.append(self.crc_calc(data[2:4]))
        self.i2c.writeto(self.addr, bytearray(data))
        sleep(0.05)
        self.__read_measured_value()

    def get_measurement(self) -> dict:
        return self.__data

    def stop_measurement(self) -> None:
        #self.i2c.write(CMD_STOP_MEASUREMENT)
        self.i2c.writeto(self.addr, bytearray(CMD_STOP_MEASUREMENT))

    def measure(self) -> dict:
        self.__read_measured_value()
        return self.__data

    # opms custom measurement wrapper
    def add_measure_to(self, report, is_aux):
        pm_0_data = self.measure()['mass_density']
        if is_aux:
            report['pm2.5_ch2'] += pm_0_data['pm2.5']
            report['pm1.0_ch2'] += pm_0_data['pm1.0']            
        else:
            report['pm2.5'] += pm_0_data['pm2.5']
            report['pm1.0'] += pm_0_data['pm1.0']

    # opms custom wakeup wrapper
    def wakeup(self, clean=False):
        self.start_measurement()
        # check if sps30 requires to be cleaned, it can be done while preheating
        if clean:
            self.start_fan_cleaning()
