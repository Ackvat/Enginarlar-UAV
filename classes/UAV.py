#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import Base
from classes.Radio import E22LoRa, R12DS
from classes.Motor import PCA9685

import services.mathService as math

########################################
#            UAV SINIFLAR              #
########################################

class UAV(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.running = False

        self.systemFrequency = 30

        
        
    def Run(self):
        self.Initialize()
        self.MainLoop()
        self.Cleanup()
        return True

    def Initialize(self):
        self.Log("İHA başlatılıyor...", logging.INFO)

        self.transponder = E22LoRa(name="Transponder", port="/dev/ttyAMA0", baudrate=9600, debug=True)
        if self.transponder.OpenModule():
            self.transponder.StartReading()

        self.controlReceiver = R12DS(name="Kontrol Alıcısı", port="/dev/ttyAMA3", baudrate=100000, tiemout=0.01)
        if self.controlReceiver.OpenModule():
            self.controlReceiver.StartReading()

        self.servoDriver = PCA9685(name="Servo Sürücüsü 1", logHandler=self.logHandler)
        if self.servoDriver.OpenModule():
            self.servoDriver.SetFrequency(333)
            self.servoDriver.SetPulseLength(1000, 2500)
            self.servoDriver.SetSignalRange(0, 100)

        self.Log("İHA başlatıldı.", logging.INFO)
        return True

    def MainLoop(self):
        self.Log("İHA anayordam döngüsü başlatılıyor...", logging.INFO)
        try:
            if self.running:
                self.Log("İHA anayordam döngü sanal kapısı zaten açık! Döngü fonksiyonuna yine de giriliyor!", logging.WARNING)
            else:
                self.running = True
            while self.running:
                if (transponderReceivedMessage := self.transponder.GetMessage()):
                    self.transponder.SendMessage(transponderReceivedMessage)
                    self.servoDriver.SetChannelSignal(1, int(transponderReceivedMessage))
                if (controlReceivedMessage := self.controlReceiver.GetMessage()):
                    #value = math.Map(controlReceivedMessage[0][2], 311, 1693, 0, 100)
                    value = controlReceivedMessage
                    #print(value)
                    #self.servoDriver.SetChannelSignal(0, int(value))
                
                time.sleep(1/self.systemFrequency)
            return True
        except KeyboardInterrupt:
            self.Log("İHA anayordam döngüsüne durdurma emri geldi.", logging.INFO)
            return False

    def Cleanup(self):
        self.Log("İHA yordamları ve modülleri kapatılıyor...", logging.INFO)
 
        self.servoDriver.CloseModule() 
        self.transponder.CloseModule()
        self.controlReceiver.CloseModule()
    
        self.Log("İHA yordamları ve modülleri temizlendi ve kapatıldı.", logging.INFO)
        self.Log("Tekrar görüşmek üzere Uzay Enginarı o7", logging.DEBUG)
        return True
        
