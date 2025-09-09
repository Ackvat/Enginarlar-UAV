#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import Base
from classes.Radio import E22LoRa
from classes.Motor import PCA9685

from services import JSONService

########################################
#            UAV SINIFLAR              #
########################################

class UAV(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Nesneye özel dönütler
        with open("lib/response/uav.json", "r", encoding="utf-8") as f:
            classResponse = json.load(f)
            self.response = JSONService.MergeJSON(self.response, classResponse)
        
        self.running = False

        self.systemFrequency = 30

        
        
    def Run(self):
        self.Initialize()
        self.MainLoop()
        self.Cleanup()

    def Initialize(self):
        self.transponder = E22LoRa(name="Transponder", port="/dev/ttyAMA0", baudrate=9600)
        self.transponder.OpenModule()
        self.transponder.StartReading()

        self.servoDriver = PCA9685(name="Servo Sürücüsü 1", logHandler=self.logHandler)
        self.servoDriver.OpenModule()
        #self.servoDriver.SetFrequency(333)
        #self.servoDriver.SetPulseLength(1363, 2726)
        #self.servoDriver.SetServoAngleRange(-90, 300) # TODO:Niye böyle bilmiyom, bakcam.

        self.servoDriver.SetFrequency(50)
        self.servoDriver.SetPulseLength(1000, 2500)
        self.servoDriver.SetServoAngleRange(0, 100)

        self.Log("uav_init_success", logging.INFO)

    def MainLoop(self):
        try:
            while True:
                if (transponderReceivedMessage := self.transponder.GetMessage()):
                    self.transponder.SendMessage(transponderReceivedMessage)

                    self.servoDriver.SetServoAngle(0, int(transponderReceivedMessage))
                time.sleep(1/self.systemFrequency)
        except KeyboardInterrupt:
            pass

    def Cleanup(self):
        self.Log("uav_closing", logging.INFO)
        self.servoDriver.CloseModule()
        self.transponder.CloseModule()
        self.Log("uav_closed", logging.INFO)
        
