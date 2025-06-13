#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from smbus2 import SMBus

import lib.responseService as rs

########################################
#           ARAYÜZ SINIFI              #
########################################

class INTERFACE:
    def __init__(self, uav=None):
        self.devName = "INTERFACE"

        self.uav = uav
        self.i2c = SMBus(1)
    
    def Response(self, response=None, name="", padding=False):
        if response["reason"]["level"] <= self.uav.responseLevel:
            print(rs.Format(response["text"], response["reason"], name, padding))
    
    def I2CRead(self, address, register, length):
        try:
            read = self.i2c.read_i2c_block_data(address, register, length)
            return read
        except Exception as e:
            self.Response({"text": f"Read failed: {e}", "reason": rs.reasons["ERROR"]}, self.devName)
            return None
