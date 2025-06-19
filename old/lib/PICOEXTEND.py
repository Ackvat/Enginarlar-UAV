#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import lib.responseService as rs

########################################
#          PICOEXTEND SINIFI           #
########################################

class PICOEXTEND:
    def __init__(self, devName="PICO ARAYUZ", uav=None):
        self.devName = devName

        self.address = {
            "PICO": 0x41,
        }

        self.byteData = {
        }

        self.response = {
            "PREPARING": {"text": f'{self.devName} hazırlanıyor...', "reason": rs.reasons["DEBUG"]},
            "PREPARED": {"text": f'{self.devName} hazırlandı.', "reason": rs.reasons["DEBUG"]},

            "INIT_FAILED": {"text": f'{self.devName} başlatılamadı.', "reason": rs.reasons["ERROR"]},
            "READ_FAILED": {"text": f'{self.devName} okuma hatası.', "reason": rs.reasons["ERROR"]},
        }
        
        self.settings = {
            
        }

        self.uav = uav

        self.uav.interface.Response(self.response["PREPARING"], self.devName)
        
        self.status = True
        
        if not self.status:
            self.uav.interface.Response(self.response["INIT_FAILED"], self.devName)
            return None

        self.uav.interface.Response(self.response["PREPARED"], self.devName)

    def Read(self, address=None, register=None):
        try:
            read = self.uav.interface.i2c.read_byte(self.address["PICO"], 0x01, 16)
            self.uav.interface.i2c.i2c_rdwr(read)
            return read
        except Exception as e:
            self.uav.interface.Response(self.response["READ_FAILED"], self.devName)
            return None

    def Write(self, address=None, register=None, data=None):
        try:
            write = self.uav.interface.i2c.write_byte(self.address["PICO"], 0x01, data)
            self.uav.interface.i2c.i2c_rdwr(write)
            return True
        except Exception as e:
            self.uav.interface.Response(self.response["READ_FAILED"], self.devName)
            return False