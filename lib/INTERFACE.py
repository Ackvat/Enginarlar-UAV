#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import lib.responseService as rs

########################################
#           ARAYÜZ SINIFI              #
########################################

class INTERFACE:
    def __init__(self, uav=None):
        self.devName = "INTERFACE"

        self.uav = uav
        self.i2c = self.uav.i2c
    
    def Response(self, response=None, name="", padding=False):
        if response["reason"]["level"] <= self.uav.responseLevel:
            print(rs.Format(response["text"], response["reason"], name, padding))

    def I2CReadRegister(self, devAddr, regAddr):
        self.i2c.write_byte(devAddr, regAddr)
        return self.i2c.read_byte(devAddr)