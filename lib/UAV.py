#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import time
from smbus2 import SMBus

import lib.responseService as responseService

from lib.INTERFACE import INTERFACE
from lib.BNO055 import BNO055

########################################
#             İHA SINIFI               #
########################################

class UAV:
    def __init__(self):
        self.devName = "İHA"

        self.response = {
            "PREPARING": {"text": "İHA hazırlanıyor...", "reason": responseService.reasons["DEBUG"]},
            "PREPARED": {"text": "İHA hazırlandı.", "reason": responseService.reasons["DEBUG"]},
        }
        
        self.responseLevel = 5
        self.systemFrequency = 60

        self.i2c = SMBus(1)

        self.interface = INTERFACE(uav=self)

        self.interface.Response(self.response["PREPARING"], self.devName)

        self.bodyIMU = BNO055(devName="GÖVDE AÖS", uav=self)
        
        self.interface.Response(self.response["PREPARED"], self.devName)
        
    
    def mainCycle(self):
        self.bodyIMU.GetCalibrationStatus()
        self.bodyIMU.GetAcceleration()
        self.bodyIMU.GetGravity()
        self.bodyIMU.GetQuaternionOrientation()

        time.sleep(1/self.systemFrequency)