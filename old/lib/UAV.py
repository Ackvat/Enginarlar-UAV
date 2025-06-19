#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import time

import lib.responseService as responseService

from lib.INTERFACE import INTERFACE
from lib.PICOEXTEND import PICOEXTEND
from lib.BNO055 import BNO055
from lib.R12DS import R12DS
from lib.PCA9685 import PCA9685

########################################
#             İHA SINIFI               #
########################################

class UAV:
    def __init__(self):
        self.devName = "İHA"

        self.response = {
            "PREPARING": {"text": "İHA hazırlanıyor...", "reason": responseService.reasons["DEBUG"]},
            "PREPARED": {"text": "İHA hazırlandı.", "reason": responseService.reasons["DEBUG"]},

            "INIT_ERROR": {"text": "İHA başlatılamadı.", "reason": responseService.reasons["ERROR"]},
        }

        self.responseLevel = 6

        self.interface = INTERFACE(uav=self)

        self.interface.Response(self.response["PREPARING"], self.devName)

        self.systemFrequency = 60

        self.i2c = self.interface.i2c

        self.extended = PICOEXTEND(devName="PICO ARAYÜZ", uav=self)
        self.receiver = R12DS(devName="R12DS", uav=self)
        self.bodyIMU = BNO055(devName="GÖVDE AÖS", uav=self)
        self.heavySC = PCA9685(devName="SK1", uav=self)
        
        self.interface.Response(self.response["PREPARED"], self.devName)
        
    
    def mainCycle(self):
        self.bodyIMU.ReadAll()

        receivedData = self.receiver.Read()
        if receivedData:
            print(receivedData)

        time.sleep(1/self.systemFrequency)