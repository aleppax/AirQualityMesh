from libs import micropyGPS

class NEO6M():
    
    def __init__(self,uart):
        self.gps_module = uart
        self.gps = micropyGPS.MicropyGPS(location_formatting='dd')

    def _read(self):
        length = self.gps_module.any()
        if length > 0:
            return self.gps_module.read(length)
    
    def update(self):
        data = self._read()
        for byte in data:
            message = self.gps.update(chr(byte))        

    def printLatLon(self):
        print(self.gps.latitude)
        print(self.gps.longitude)

    def to_bytes(self,x):
        return bytes((x & 0xff, (x >> 8) & 0xff))
    
    def calc_checksum(self,content):
        """
        Calculate checksum using 8-bit Fletcher's algorithm.
        :param bytes content: message content, excluding header and checksum bytes
        :return: checksum
        :rtype: bytes
        """
        check_a = 0
        check_b = 0
        for char in content:
            check_a += char
            check_a &= 0xFF
            check_b += check_a
            check_b &= 0xFF
        return bytes((check_a, check_b))

    def poll_settings(self,clsId,payload=b''):
        payloadlength = self.to_bytes(len(payload))
        msg = b'\xB5\x62' + clsId + payloadlength + payload + self.calc_checksum(clsId + payloadlength + payload)
        print(msg)
        print(self.gps_module.write(msg))
        self.gps_module.flush()
        return self.gps_module.readline()
        
    def poll_navEngine(self):
        msg = self.poll_settings(b'\x06\x24')
        print(msg)
        
    def pollSwHwVersion(self):
        msg = self.poll_settings(b'\x0A\x04')
        print(msg)

    # opms custom measurement wrapper
    def add_measure_to(self, report, options):
        self.update()
        report['latitude'] += self.gps.latitude
        report['longitude'] += self.gps.longitude

    def datetime(self):
        self.update()
        year = self.gps.date[2]+2000
        month = self.gps.date[1]
        day = self.gps.date[0]
        h = self.gps.timestamp[0]
        m = self.gps.timestamp[1]
        s = int(self.gps.timestamp[2])
        us = self.gps.timestamp[2]%1
        return (year, month, day, 0, h, m, s, us)

