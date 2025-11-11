#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import datetime
import threading

from classes.Base import Base
from classes.Radio import E22LoRa, R12DS
from classes.Motor import PCA9685
from classes.Sensor import BNO055
from classes.Queue import DiscardOldestQueue

import services.mathService as math
from services.mathService import Vector3, Quaternion, Basis
import services.utilitiesService as utility

########################################
#            UAV SINIFLAR              #
########################################

class UAV(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.running = False

        self.systemFrequency = kwargs.get("systemFrequency", 90)
        self.steps = 0
        self.debugSteps = 0
        self.debugStepAntiFrequency = self.systemFrequency
        self.printDebug = True

        self.commandChannels = [True, False, True] # E22 LoRa, NRF24L01, R12DS

        self.messageAddress = {
            "SELF": "UAVM",
            "GROUND_CONTROL_MASTER": "GCMS",
            "GROUND_CONTROL_SLAVE": "GCSL"
        }

        self.mainLoopDelta = 0.0
        
        self.controlInputs = {
            "CONTROLLER": {
                "THRUST": 0,
                "ROLL": 0,
                "PITCH": 0,
                "YAW": 0,
                "FLIGHT_MODE": "KILL",
                "FAIL_SAFE": False
            },
            
            "BODY_ORIENTATION_QUATERNION": Quaternion(),
            "BODY_ORIENTATION_BASIS": Basis()
        }
        self.controlOutputs = {
            "DESIRED_CURRENT_SYNCED": False,

            "CONTROLLER": {
                "THRUST": 0,
                "ROLL": 0,
                "PITCH": 0,
                "YAW": 0
            },

            "BODY_ORIENTATION_QUATERNION": Quaternion(),
            "BODY_ORIENTATION_BASIS": Basis()
        }
        
    # İHA'nın başlatılması, çalışması ve kapanması için çağırılması gereken işlev.
    def Run(self):
        self.Initialize()
        self.MainLoop()
        self.Cleanup()
        return True

    # İHA'nın birimlerini ve servislerini hazırlar.
    def Initialize(self):
        self.Log("İHA başlatılıyor...", logging.INFO)

        # Alıcılar
        self.transponder = E22LoRa(
            name="Transponder", port="/dev/ttyAMA0", baudrate=115200, timeout=1,
            messageFrequency=self.systemFrequency,
            inQueue=DiscardOldestQueue(maxsize=3),
            outQueue=DiscardOldestQueue(maxsize=3),
            runType=0, 
            debug=False)
        if self.transponder.OpenModule():
            self.transponder.StartMessageLoop()

        self.controllerReceiver = R12DS(
            name="Kontrol Alıcısı", port="/dev/ttyAMA3", baudrate=100000, timeout=1,
            messageFrequency = self.systemFrequency)
        if self.controllerReceiver.OpenModule():
            self.controllerReceiver.StartMessageLoop()
        
        # Sensörler
        self.bodyIMU = BNO055(name="Gövde AÖS",
        readingFrequency=self.systemFrequency,
        debug=False)
        if self.bodyIMU.OpenModule():
            self.bodyIMU.StartReadingLoop()

        # Sürücüler
        self.motorDriverA = PCA9685(name="Motor Sürücüsü A",
        signalUpdateFrequency=self.systemFrequency)#, logHandler=self.logHandler)
        if self.motorDriverA.OpenModule():
            self.motorDriverA.SetFrequency(333)
            #self.motorDriverA.SetPulseLength(1000, 2500) # 1) 750-3600, 2) 1000-2500
            self.motorDriverA.SetSignalRangeChannels(
                [1000, 1000, 1000, 1000, 750, 750, 750, 750, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
                [2500, 2500, 2500, 2500, 3600, 3600, 3600, 3600, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500]
            )
            self.motorDriverA.SetSignalRange(0, 100)
            self.motorDriverA.StartSignalLoop()

        self.Log("İHA başlatıldı.", logging.INFO)
        return True

    # İHA anayordam döngüsü.
    def MainLoop(self):
        self.Log("İHA anayordam döngüsü başlatılıyor...", logging.INFO)
        try:
            if self.running:
                self.Log("İHA anayordam döngü sanal kapısı zaten açık! Döngü işlevine yine de giriliyor!", logging.WARNING)
            else:
                self.running = True
            
            while self.running:
                mainLoopTimeStamp = utility.TimeStamper()

                # Alıcılar
                loraTimeStamp = utility.TimeStamper()
                if (transponderReceivedMessage := self.transponder.GetMessage()):
                    if self.commandChannels[0]:
                        self.CommandExecution(transponderReceivedMessage)
                loraDelta = loraTimeStamp.GetDelta()

                controlMessageTimeStamp = utility.TimeStamper()
                if (controllerReceivedMessage := self.controllerReceiver.GetMessage()):
                    self.ParseControllerInput(controllerReceivedMessage)
                controlMessageDelta = controlMessageTimeStamp.GetDelta()

                controlOutputTimeStamp = utility.TimeStamper()
                self.SetControlInputs()
                self.CalculateControlOutputs()
                controlOutputDelta = controlOutputTimeStamp.GetDelta()
                
                self.mainLoopDelta = mainLoopTimeStamp.GetDelta()

                self.steps += 1
                if self.steps % self.debugStepAntiFrequency == 0:
                    self.steps = 0
                    self.debugSteps += 1

                    if self.printDebug: 
                        self.Print(f"-----------------------------------------------")
                        self.Print(f"Adım: {self.debugSteps}")
                        self.Print(f"Frekans: {self.systemFrequency} Hz | {1000/self.systemFrequency:.2f} ms")
                        self.Print(f"Yordam Kronometresi:")
                        self.Print(f"\tLoRa Komutları:      {loraDelta} ms")
                        self.Print(f"\tKumanda Komutları:   {controlMessageDelta} ms")
                        self.Print(f"\tKontrol Algoritması: {controlOutputDelta} ms")
                        self.Print(f"\t                                       +")
                        self.Print(f"\t----------------------------------------")
                        self.Print(f"\tAnadöngü Toplam:     {self.mainLoopDelta} ms")

                        flightMode = self.controlInputs["CONTROLLER"]["FLIGHT_MODE"]
                        self.Print(f"Uçuş Modu: {flightMode}")
                
                time.sleep(math.Clamp(((1/self.systemFrequency)*1000.0-self.mainLoopDelta)/1000.0, 0, 1/self.systemFrequency))

            self.running = False
        except Exception as e:
            self.Log(f"Anayordam döngüsünde bir hata oluştu! {e}", logging.ERROR)
            return False
        except KeyboardInterrupt:
            self.Log("Anayordam döngüsünü KERNEL durdurma talebi geldi.", logging.INFO)
            return True

    # İHA'nın kapanırken, koşut yordamları ve döngüleri temizlemesi için.
    def Cleanup(self):
        self.Log("İHA yordamları ve birimleri kapatılıyor...", logging.INFO)

        self.motorDriverA.CloseModule()

        self.bodyIMU.CloseModule()

        self.controllerReceiver.CloseModule()
        self.transponder.CloseModule()
    
        self.Log("İHA yordamları ve birimleri temizlendi ve kapatıldı.", logging.INFO)
        self.Log("Tekrar görüşmek üzere Uzay Enginarı o7", logging.DEBUG)
        return True
    


    def CommandExecution(self, message):
        commands = message.strip().upper().split(";")

        #self.transponder.SendMessage(message) # Alınan bildiryi yansıt.

        if len(commands) > 0:
            if commands[0] == "CLOSE":
                self.running = False
                self.Log("Anayordamı durdurma komutu geldi.", logging.INFO)
            elif commands[0] == "SETSERVO":
                #self.motorDriverA.SetChannelSignal(int(commands[1]), int(commands[2]))
                pass
            elif commands[0] == "GCMS":
                if commands[1] == "UAVM":
                    if commands[2] == "GTIN":
                        sender = self.messageAddress["SELF"]
                        receiver = self.messageAddress["GROUND_CONTROL_MASTER"]
                        currentOrientationQuaternion = self.controlInputs["BODY_ORIENTATION_QUATERNION"]
                        desiredOrientationQuaternion = self.controlOutputs["BODY_ORIENTATION_QUATERNION"]
                        flightMode = self.controlInputs["CONTROLLER"]["FLIGHT_MODE"]
                        self.transponder.SendMessage(f"{sender};{receiver};GTIN;CQO:{currentOrientationQuaternion};DQO:{desiredOrientationQuaternion};DELT:{self.mainLoopDelta};MODE:{flightMode};CALB:{self.bodyIMU.sysCalibrationStatus}:{self.bodyIMU.accelCalibrationStatus}:{self.bodyIMU.gyroCalibrationStatus}:{self.bodyIMU.magCalibrationStatus}")
            else:
                self.Log(f"Geçersiz komut zinciri! {commands}", logging.WARNING)
    
    # Normalde, kumanda alıcısının kendi nesnesinde esas derleme yapılıyor, ancak burada kontrol algoritmasının işine yarayacak hale ayrıca getiriyoruz.
    def ParseControllerInput(self, controllerInput):
        controlChannels = controllerInput[0]
        ch17 = controllerInput[1]
        ch18 = controllerInput[2]
        failSafe = controllerInput[3]

        self.controlInputs["CONTROLLER"]["THRUST"] = int(math.Map(controlChannels[2], 306, 1693, 0, 100))
        self.controlInputs["CONTROLLER"]["ROLL"] = int(math.Map(controlChannels[0], 306, 1693, 0, 100))
        self.controlInputs["CONTROLLER"]["PITCH"] = int(math.Map(controlChannels[1], 306, 1693, 0, 100))
        self.controlInputs["CONTROLLER"]["YAW"] = int(math.Map(controlChannels[3], 306, 1693, 0, 100))

        flightModeMapped = [controlChannels[9]*0.5, controlChannels[9], controlChannels[9]*2]
        if controlChannels[9] == 74:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "HOVER"
        elif controlChannels[9] == 370:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "VERTICAL"
        elif controlChannels[9] == 667:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "AUTO_HOVER"
        elif controlChannels[9] == 963:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "HORIZONTAL"
        elif controlChannels[9] == 1194:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "AUTO_HORIZONTAL"
        elif controlChannels[9] == 1416:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "KILL"
        else:
            self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] = "ZENCİ"
        
        self.controlInputs["CONTROLLER"]["FAIL_SAFE"] = failSafe

    def SetControlInputs(self):
        self.controlOutputs["CONTROLLER"]["ROLL"] = (50 - self.controlInputs["CONTROLLER"]["ROLL"])*(1/1000)*self.mainLoopDelta
        self.controlOutputs["CONTROLLER"]["PITCH"] = (50 - self.controlInputs["CONTROLLER"]["PITCH"])*(-1/1000)*self.mainLoopDelta
        self.controlOutputs["CONTROLLER"]["YAW"] = (50 - self.controlInputs["CONTROLLER"]["YAW"])*(1/1000)*self.mainLoopDelta

        #self.controlInputs["BODY_ORIENTATION_QUATERNION"] = self.bodyIMU.quaternionOrientation.Normalized()
        #self.controlInputs["BODY_ORIENTATION_QUATERNION"] = math.LowPassFilterUpdate(0.05, self.controlInputs["BODY_ORIENTATION_QUATERNION"], self.bodyIMU.quaternionOrientation.Normalized())
        lowPassFiltered_BodyOrientation = math.LowPassFilterUpdate(0.1, self.controlInputs["BODY_ORIENTATION_QUATERNION"], self.bodyIMU.quaternionOrientation.Normalized())
        amplitudeImpedanceFiltered_BodyOrientation = math.AmplitudeImpedanceUpdate(1.5, self.controlInputs["BODY_ORIENTATION_QUATERNION"], lowPassFiltered_BodyOrientation)
        self.controlInputs["BODY_ORIENTATION_QUATERNION"] = amplitudeImpedanceFiltered_BodyOrientation
    
    # TODO: LOL
    def CalculateControlOutputs(self):
        #if not self.controlOutputs["DESIRED_CURRENT_SYNCED"]:
            #time.sleep(1)
            #self.controlOutputs["BODY_ORIENTATION_QUATERNION"] = self.controlInputs["BODY_ORIENTATION_QUATERNION"].Clone()
            #self.controlOutputs["DESIRED_CURRENT_SYNCED"] = True

        desiredRotationQuaternion = Quaternion.FromAxisAngle(self.controlOutputs["CONTROLLER"]["YAW"], Vector3(0, 0, 1)).Mult(Quaternion.FromAxisAngle(self.controlOutputs["CONTROLLER"]["PITCH"], Vector3(0, 1, 0))).Mult(Quaternion.FromAxisAngle(self.controlOutputs["CONTROLLER"]["ROLL"], Vector3(1, 0, 0)))
        self.controlOutputs["BODY_ORIENTATION_QUATERNION"] = self.controlOutputs["BODY_ORIENTATION_QUATERNION"].Mult(desiredRotationQuaternion).Normalized()
        currentToDesiredQuaternionError = self.controlOutputs["BODY_ORIENTATION_QUATERNION"].Mult(self.controlInputs["BODY_ORIENTATION_QUATERNION"].Conjugated())
        
        # Birden fazla tur gerekirse, en kısa mesafeye dönüştürür.
        if currentToDesiredQuaternionError.w < 0:
            currentToDesiredQuaternionError = currentToDesiredQuaternionError.Mult(Quaternion(0, 0, 0, -1))
        
        desiredRotationError = currentToDesiredQuaternionError.GetEulerAngles() # Roll, Pitch, Yaw geliyor.
        
        # Havada durma modu.
        if self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] == "HOVER":
            # Tahrik Motorları
            self.motorDriverA.signals[0] = math.Clamp(self.controlInputs["CONTROLLER"]["THRUST"] - math.Map(desiredRotationError.y, -180, 180, -50, 50) - math.Map(desiredRotationError.x, -180, 180, -50, 50), 0, 100) # Sol Ön
            self.motorDriverA.signals[1] = math.Clamp(self.controlInputs["CONTROLLER"]["THRUST"] - math.Map(desiredRotationError.y, -180, 180, -50, 50) + math.Map(desiredRotationError.x, -180, 180, -50, 50), 0, 100) # Sağ Ön
            self.motorDriverA.signals[2] = math.Clamp(self.controlInputs["CONTROLLER"]["THRUST"] + math.Map(desiredRotationError.y, -180, 180, -50, 50) - math.Map(desiredRotationError.x, -180, 180, -50, 50), 0, 100) # Sol Arka
            self.motorDriverA.signals[3] = math.Clamp(self.controlInputs["CONTROLLER"]["THRUST"] + math.Map(desiredRotationError.y, -180, 180, -50, 50) + math.Map(desiredRotationError.x, -180, 180, -50, 50), 0, 100) # Sağ Arka
            
            # Nacelle Servoları
            self.motorDriverA.signals[4] = math.Map(desiredRotationError.z, -180, 180, 0, 100) # Sol Ön
            self.motorDriverA.signals[5] = math.Map(desiredRotationError.z, -180, 180, 0, 100) # Sağ Ön
            self.motorDriverA.signals[6] = math.Map(desiredRotationError.z, -180, 180, 0, 100) # Sol Arka
            self.motorDriverA.signals[7] = math.Map(desiredRotationError.z, -180, 180, 0, 100) # Sağ Arka
        # Tam duruş.
        elif self.controlInputs["CONTROLLER"]["FLIGHT_MODE"] == "KILL" or self.controlInputs["CONTROLLER"]["FAIL_SAFE"]:
            # Tahrik Motorları
            self.motorDriverA.signals[0] = 0
            self.motorDriverA.signals[1] = 0
            self.motorDriverA.signals[2] = 0
            self.motorDriverA.signals[3] = 0
            
            # Nacelle Servoları
            self.motorDriverA.signals[4] = 50 # Sol Ön
            self.motorDriverA.signals[5] = 50 # Sağ Ön
            self.motorDriverA.signals[6] = 50 # Sol Arka
            self.motorDriverA.signals[7] = 50 # Sağ Arka
        else:
            # Tahrik Motorları
            self.motorDriverA.signals[0] = 0
            self.motorDriverA.signals[1] = 0
            self.motorDriverA.signals[2] = 0
            self.motorDriverA.signals[3] = 0
            
            # Nacelle Servoları
            self.motorDriverA.signals[4] = 50 # Sol Ön
            self.motorDriverA.signals[5] = 50 # Sağ Ön
            self.motorDriverA.signals[6] = 50 # Sol Arka
            self.motorDriverA.signals[7] = 50 # Sağ Arka
            
            

