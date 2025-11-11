#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import I2CBase

from services.mathService import Vector3, Quaternion

########################################
#          SENSÖR SINIFLAR             #
########################################

class IMUBase(I2CBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.open = False
        self.suspended = False
        self.status = False
        self.running = False
        self.runType = kwargs.get("runType", 0)
        self.readingFrequency = kwargs.get("readingFrequency", 100)


    # Birimi açma ve hazırlama işlevi
    def OpenModule(self):
        self.Log("Birim başlatılıyor...", logging.INFO)
        if self.open:
            self.Log("Birim zaten açık!", logging.WARNING)
        else:
            self.open = True
            self.Log("Birim başlatıldı.", logging.WARNING)
        return True
                
    # Birimi kapatma işlevi
    def CloseModule(self):
        self.Log("Birim kapatılıyor...", logging.INFO)
        self.StopReadingLoop()
        if self.open:
            self.open = False
            self.Log("Birim kapatıldı.", logging.INFO)
        else:
            self.Log("Birim sanal kapısı zaten kapalıydı!", logging.WARNING)
        return True

    # Sensör okuma döngüsü için koşut iş parçacığı başlatma işlevi.
    def StartReadingLoop(self):
        self.Log("Birim sensör okuma döngüsü başlatılıyor...", logging.INFO)

        if self.open and not self.running:
            self.running = True
            try:
                if self.runType == 0:
                    self.readThread = threading.Thread(target=self._ReadingLoop, daemon=True)
                    self.readThread.start()
                    self.Log("Birim sensör okuma döngüsü tek yordam koşutuyla başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim sensör okuma döngüsü başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        elif self.open and self.running:
            self.Log("Birim sensör okuma döngüsü zaten çalışıyor!", logging.WARNING)
            return True
        else:
            self.Log("Birim kapalı! Sensör okuma döngüsü başlatılamaz!", logging.WARNING)
            return True

    # Sensör okuma döngüsü durdurur.
    def StopReadingLoop(self):
        if self.running:
            self.running = False
            try:
                if hasattr(self, 'readThread'):
                    self.readThread.join()
                self.Log("Birim sensör okuma döngüsü durduruldu.", logging.INFO)
            except Exception as e:
                self.Log(f"Birimin sensör okuma döngüsü kapatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Birim sanal sensör okuma kapısı açıkken, sensör okuma döngüsünün kendisi bulunamadı!", logging.WARNING)






# TODO: OFFSET adreslerini ve offsetleme yi ekle. Aynı şey MPU9250 için de geçerli.
class BNO055(IMUBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.address = {
            "SELF": 0x28,

            "CHIP_ID": 0x00,
            "ACCEL_X_LSB": 0x08,
            "ACCEL_X_MSB": 0x09,
            "ACCEL_Y_LSB": 0x0A,
            "ACCEL_Y_MSB": 0x0B,
            "ACCEL_Z_LSB": 0x0C,
            "ACCEL_Z_MSB": 0x0D,
            "MAG_X_LSB": 0x0E,
            "MAG_X_MSB": 0x0F,
            "MAG_Y_LSB": 0x10,
            "MAG_Y_MSB": 0x11,
            "MAG_Z_LSB": 0x12,
            "MAG_Z_MSB": 0x13,
            "GYRO_X_LSB": 0x14,
            "GYRO_X_MSB": 0x15,
            "GYRO_Y_LSB": 0x16,
            "GYRO_Y_MSB": 0x17,
            "GYRO_Z_LSB": 0x18,
            "GYRO_Z_MSB": 0x19,
            "EULER_H_LSB": 0x1A,
            "EULER_H_MSB": 0x1B,
            "EULER_R_LSB": 0x1C,
            "EULER_R_MSB": 0x1D,
            "EULER_P_LSB": 0x1E,
            "EULER_P_MSB": 0x1F,
            "QUATERNION_DATA_W_LSB": 0x20,
            "QUATERNION_DATA_W_MSB": 0x21,
            "QUATERNION_DATA_X_LSB": 0x22,
            "QUATERNION_DATA_X_MSB": 0x23,
            "QUATERNION_DATA_Y_LSB": 0x24,
            "QUATERNION_DATA_Y_MSB": 0x25,
            "QUATERNION_DATA_Z_LSB": 0x26,
            "QUATERNION_DATA_Z_MSB": 0x27,
            "LINEAR_ACCEL_DATA_X_LSB": 0x28,
            "LINEAR_ACCEL_DATA_X_MSB": 0x29,
            "LINEAR_ACCEL_DATA_Y_LSB": 0x2A,
            "LINEAR_ACCEL_DATA_Y_MSB": 0x2B,
            "LINEAR_ACCEL_DATA_Z_LSB": 0x2C,
            "LINEAR_ACCEL_DATA_Z_MSB": 0x2D,
            "GRAVITY_DATA_X_LSB": 0x2E,
            "GRAVITY_DATA_X_MSB": 0x2F,
            "GRAVITY_DATA_Y_LSB": 0x30,
            "GRAVITY_DATA_Y_MSB": 0x31,
            "GRAVITY_DATA_Z_LSB": 0x32,
            "GRAVITY_DATA_Z_MSB": 0x33,
            
            "TEMP": 0x34,

            "CALIB_STAT": 0x35,

            "UNIT_SEL": 0x3B,
            "OPR_MODE": 0x3D,
            "PWR_MODE": 0x3E,
        }

        self.byteData = {
            "UNIT_SEL": {
                "METRIC": 0x00,
            },
            "OPR_MODE": {
                "CONFIG": 0x00,
                "NDOF": 0x0C, # Tüm sensörler + Mutlak oriyantasyon
            },
            "PWR_MODE": {
                "NORMAL": 0x00,
                "LOWPOWER": 0x01,
                "SUSPEND": 0x02,
            }
        }

        self.settings = {
            "ACCEL_UNIT_LSB": 1/10**2,
            "GRAVITY_UNIT_LSB": 1/10**2,
            "EULER_UNIT_LSB": 1/16,
            "QUATERNION_UNIT_LSB": 1/2**14,
            "GYRO_UNIT_LSB": 1/16,
            "MAG_UNIT_LSB": 1/16,

            "ACCEL_X_MASK": 1,
            "ACCEL_Y_MASK": 1,
            "ACCEL_Z_MASK": 1,

            "GRAVITY_X_MASK": 1,
            "GRAVITY_Y_MASK": 1,
            "GRAVITY_Z_MASK": 1,

            "LINEAR_ACCEL_X_MASK": 1,
            "LINEAR_ACCEL_Y_MASK": 1,
            "LINEAR_ACCEL_Z_MASK": 1,

            "EULER_H_MASK": 1,
            "EULER_R_MASK": 1,
            "EULER_P_MASK": 1,

            "QUATERNION_W_MASK": 1,
            "QUATERNION_X_MASK": 1,
            "QUATERNION_Y_MASK": 1,
            "QUATERNION_Z_MASK": 1,

            "GYRO_X_MASK": 1,
            "GYRO_Y_MASK": 1,
            "GYRO_Z_MASK": 1,

            "MAG_X_MASK": 1,
            "MAG_Y_MASK": 1,
            "MAG_Z_MASK": 1,
        }

        self.sysCalibrationStatus = 0
        self.accelCalibrationStatus = 0
        self.magCalibrationStatus = 0
        self.gyroCalibrationStatus = 0

        self.acceleration = Vector3()
        self.linearAcceleration = Vector3()
        self.gravity = Vector3()
        self.eulerOrientation = Vector3()
        self.quaternionOrientation = Quaternion()
        self.angularVelocity = Vector3()
        self.compass = Vector3()

        # Döngülerden çıkan hatalar kendini tekrarlamasın diye, en son hatayı burda kaydediyoruz ve sonra döngülerde ona göre hatayı çıkartıyoruz.
        self.lastErrorCode = 0

        self.states = {
            "ERROR": {
                "NO_ERROR": 0,
                "READ_ERROR": 1
            }
        }



    # Birimin okuma frekansı 100 Hz'e limitli olduğu için özel bir okuma döngüsüne ihtiyacı var.
    def _ReadingLoop(self):
        while self.open and self.running and self.status:
            self.ReadAll()
            time.sleep(1/self.readingFrequency)
    


    # Birimi açma ve hazırlama işlevi. [ÜSTÜN]
    def OpenModule(self):
        self.Log("Birim başlatılıyor...", logging.INFO)
        if self.open:
            self.Log("Birim zaten açık!", logging.WARNING)
        else:
            self.open = True
            
            self.status = self.CheckChipID()

            self.SetOperatingMode(self.byteData["OPR_MODE"]["CONFIG"])

            # Uyuyorsa uyandırır.
            self.SetPowerMode(self.byteData["PWR_MODE"]["NORMAL"])
            self.SetReadingUnit(self.byteData["UNIT_SEL"]["METRIC"])

            self.SetOperatingMode(self.byteData["OPR_MODE"]["NDOF"])

        
        if self.status:
            self.Log("Birim başlatıldı.", logging.INFO)
            return True
        else:
            self.Log("Birim başlatılırken bir hata oluştu!", logging.ERROR)
            return False
                
    # Birimi kapatma işlevi. [ÜSTÜN]
    def CloseModule(self):
        self.Log("Birim kapatılıyor...", logging.INFO)
        self.StopReadingLoop()
        if self.open:
            if not self.suspended:
                self.SuspendSensor()
            self.open = False
            self.Log("Birim kapatıldı.", logging.INFO)
        else:
            self.Log("Birim sanal kapısı zaten kapalıydı!", logging.WARNING)
        return True
    
    # Birimi duraklatır.
    def SuspendSensor(self):
        self.suspended = True
        self.SetPowerMode(self.byteData["PWR_MODE"]["SUSPEND"])
        return True

    # Birimi geri uyandırır.
    def WakeUpSensor(self):
        self.suspended = False
        self.SetPowerMode(self.byteData["PWR_MODE"]["NORMAL"])
        return True
    


    # Birimin I2C'de sunduğu kimlik numarasını kontrol eder. Yanlış çıkmamalı.
    def CheckChipID(self):
        if self.open:
            try:
                self.I2CWriteByte(self.address["SELF"], self.address["CHIP_ID"])
                chipID = self.I2CReadByte(self.address["SELF"])
            except Exception as error:
                self.Log(f"Birim kimlik numarası okunamadı! {error}", logging.ERROR)
                return False
            
            self.Log(f"Birimin kimlik numarası okundu: {chipID}|{hex(chipID)}", logging.INFO)

            if chipID != 0xA0:
                self.Log("Birimden gelen kimlik yanlış!", logging.ERROR)
                return False
            else:
                self.Log("Birimin kimliği doğru.", logging.INFO)
                return True
    
    # Birimin okuduğu değerlerin hangi sayı biriminde olacağını ayarlar.
    def SetReadingUnit(self, unit=0x00):
        if self.open and self.status:
            if not unit in self.byteData["UNIT_SEL"].values():
                self.Log("Birime sunulan sayı birim ayarı geçersiz!", logging.ERROR)
                return False

            try:
                self.I2CWriteByteData(self.address["SELF"], self.address["UNIT_SEL"], unit)
            except Exception as error:
                self.Log("Birim için sunulan sayı birim ayarı yapılırken bir hata oluştu!", logging.ERROR)
                return False

            setUnit = "NONE"
            for key, value in self.byteData["UNIT_SEL"].items():
                if value == unit:
                    setUnit = key

            self.Log(f"Birim için sayı birim ayarı yapıldı: {setUnit}: {unit}|{hex(unit)}", logging.INFO)
            return True
    
    # Birimin çalışma modunu ayarlar.
    def SetOperatingMode(self, operatingMode=0x0C):
        if self.open and self.status:
            if not operatingMode in self.byteData["OPR_MODE"].values():
                self.Log("Birime sunulan çalışma modu ayarı geçersiz!", logging.ERROR)
                return False

            try:
                self.I2CWriteByteData(self.address["SELF"], self.address["OPR_MODE"], operatingMode)
            except Exception as error:
                self.Log("Birim için sunulan çalışma modu ayarı yapılırken bir hata oluştu!", logging.ERROR)
                return False

            setMode = "NONE"
            for key, value in self.byteData["OPR_MODE"].items():
                if value == operatingMode:
                    setMode = key
            
            self.Log(f"Birim için çalışma modu ayarı yapıldı: {setMode}: {operatingMode}|{hex(operatingMode)}", logging.INFO)
            return True
    
    # Birimin güç modunu ayarlar.
    def SetPowerMode(self, powerMode=0x00):
        if self.open and self.status:
            if not powerMode in self.byteData["PWR_MODE"].values():
                self.Log("Birime sunulan güç modu ayarı geçersiz!", logging.ERROR)
                return False
            
            try:
                self.I2CWriteByteData(self.address["SELF"], self.address["PWR_MODE"], powerMode)
            except Exception as error:
                self.Log("Birim için sunulan güç modu ayarı yapılırken bir hata oluştu!", logging.ERROR)
                return False

            setMode = "NONE"
            for key, value in self.byteData["PWR_MODE"].items():
                if value == powerMode:
                    setMode = key
            
            self.Log(f"Birim için güç modu ayarı yapıldı: {setMode}: {powerMode}|{hex(powerMode)}", logging.INFO)
            return True
    


    # Ham ivme ölçümü.
    def GetAcceleration(self):
        try:
            accelXLSB, accelXMSB, accelYLSB, accelYMSB, accelZLSB, accelZMSB = self.I2CReadBlockData(self.address["SELF"], self.address["ACCEL_X_LSB"], 6)

            self.acceleration.x = (((accelXMSB << 8) | accelXLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelXMSB << 8) | accelXLSB) >= 0x8000 else ((accelXMSB << 8) | accelXLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.acceleration.y = (((accelYMSB << 8) | accelYLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelYMSB << 8) | accelYLSB) >= 0x8000 else ((accelYMSB << 8) | accelYLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.acceleration.z = (((accelZMSB << 8) | accelZLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelZMSB << 8) | accelZLSB) >= 0x8000 else ((accelZMSB << 8) | accelZLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim ham ivme ölçerken hata meydana geldi: {error}", logging.ERROR)
            return None

        if self.debug:
            self.Log(f"Ham İvme: {self.acceleration}", logging.DEBUG)

        return self.acceleration
    
    # Yerçekimi hariç (Doğrusal) ivme ölçümü.
    def GetLinearAcceleration(self):
        try:
            linAccelXLSB, linAccelXMSB, linAccelYLSB, linAccelYMSB, linAccelZLSB, linAccelZMSB = self.I2CReadBlockData(self.address["SELF"], self.address["LINEAR_ACCEL_DATA_X_LSB"], 6)

            self.linearAcceleration.x = (((linAccelXMSB << 8) | linAccelXLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((linAccelXMSB << 8) | linAccelXLSB) >= 0x8000 else ((linAccelXMSB << 8) | linAccelXLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.linearAcceleration.y = (((linAccelYMSB << 8) | linAccelYLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((linAccelYMSB << 8) | linAccelYLSB) >= 0x8000 else ((linAccelYMSB << 8) | linAccelYLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.linearAcceleration.z = (((linAccelZMSB << 8) | linAccelZLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((linAccelZMSB << 8) | linAccelZLSB) >= 0x8000 else ((linAccelZMSB << 8) | linAccelZLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim doğrusal ivme ölçerken hata meydana geldi: {error}", logging.ERROR)
            return None

        if self.debug:
            self.Log(f"Doğrusal İvme: {self.linearAcceleration}", logging.DEBUG)

        return self.linearAcceleration

    # Yerçekimi yön ölçümü.
    def GetGravity(self):
        try:
            gravityXLSB, gravityXMSB, gravityYLSB, gravityYMSB, gravityZLSB, gravityZMSB = self.I2CReadBlockData(self.address["SELF"], self.address["GRAVITY_DATA_X_LSB"], 6)

            self.gravity.x = (((gravityXMSB << 8) | gravityXLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_X_MASK"] if ((gravityXMSB << 8) | gravityXLSB) >= 0x8000 else ((gravityXMSB << 8) | gravityXLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_X_MASK"]
            self.gravity.y = (((gravityYMSB << 8) | gravityYLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Y_MASK"] if ((gravityYMSB << 8) | gravityYLSB) >= 0x8000 else ((gravityYMSB << 8) | gravityYLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Y_MASK"]
            self.gravity.z = (((gravityZMSB << 8) | gravityZLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Z_MASK"] if ((gravityZMSB << 8) | gravityZLSB) >= 0x8000 else ((gravityZMSB << 8) | gravityZLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Z_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim yer çekimi yönünü ölçerken hata meydana geldi: {error}", logging.ERROR)
            return None

        if self.debug:
            self.Log(f"Yer Çekimi Yönü: {self.gravity}", logging.DEBUG)

        return self.gravity

    # Euler yönelim açılarının ölçümü.
    def GetEulerOrientation(self):
        try:
            eulerHLSB, eulerHMSB, eulerRLSB, eulerRMSB, eulerPLSB, eulerPMSB = self.I2CReadBlockData(self.address["SELF"], self.address["EULER_H_LSB"], 6)

            self.eulerOrientation.x = (((eulerHMSB << 8) | eulerHLSB) - 0x10000)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_H_MASK"] if ((eulerHMSB << 8) | eulerHLSB) >= 0x8000 else ((eulerHMSB << 8) | eulerHLSB)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_H_MASK"]
            self.eulerOrientation.y = (((eulerRMSB << 8) | eulerRLSB) - 0x10000)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_R_MASK"] if ((eulerRMSB << 8) | eulerRLSB) >= 0x8000 else ((eulerRMSB << 8) | eulerRLSB)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_R_MASK"]
            self.eulerOrientation.z = (((eulerPMSB << 8) | eulerPLSB) - 0x10000)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_P_MASK"] if ((eulerPMSB << 8) | eulerPLSB) >= 0x8000 else ((eulerPMSB << 8) | eulerPLSB)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_P_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim Euler yönelim açılarını okurken hata meydana geldi: {error}", logging.ERROR)
            return None
        
        if self.debug:
            self.Log(f"Euler Yönelimi: {self.eulerOrientation}", logging.DEBUG)

        return self.eulerOrientation

    # Quaternion yönelimi. Allah yardımcımız olsun.
    def GetQuaternionOrientation(self):
        try:
            quaternionWLSB, quaternionWMSB, quaternionXLSB, quaternionXMSB, quaternionYLSB, quaternionYMSB, quaternionZLSB, quaternionZMSB = self.I2CReadBlockData(self.address["SELF"], self.address["QUATERNION_DATA_W_LSB"], 8)

            self.quaternionOrientation.w = (((quaternionWMSB << 8) | quaternionWLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_W_MASK"] if ((quaternionWMSB << 8) | quaternionWLSB) >= 0x8000 else ((quaternionWMSB << 8) | quaternionWLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_W_MASK"]
            self.quaternionOrientation.x = (((quaternionXMSB << 8) | quaternionXLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_X_MASK"] if ((quaternionXMSB << 8) | quaternionXLSB) >= 0x8000 else ((quaternionXMSB << 8) | quaternionXLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_X_MASK"]
            self.quaternionOrientation.y = (((quaternionYMSB << 8) | quaternionYLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Y_MASK"] if ((quaternionYMSB << 8) | quaternionYLSB) >= 0x8000 else ((quaternionYMSB << 8) | quaternionYLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Y_MASK"]
            self.quaternionOrientation.z = (((quaternionZMSB << 8) | quaternionZLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Z_MASK"] if ((quaternionZMSB << 8) | quaternionZLSB) >= 0x8000 else ((quaternionZMSB << 8) | quaternionZLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Z_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim Quaternion yönelim açılarını okurken hata meydana geldi: {error}", logging.ERROR)
            return None

        if self.debug:
            self.Log(f"Quaternion Yönelimi: {self.quaternionOrientation}", logging.DEBUG)

        return self.quaternionOrientation

    # Açısal hız ölçümü.
    def GetAngularVelocity(self):
        try:
            gyroXLSB, gyroXMSB, gyroYLSB, gyroYMSB, gyroZLSB, gyroZMSB = self.I2CReadBlockData(self.address["SELF"], self.address["GYRO_X_LSB"], 6)

            self.angularVelocity.x = (((gyroXMSB << 8) | gyroXLSB) - 0x10000)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_X_MASK"] if ((gyroXMSB << 8) | gyroXLSB) >= 0x8000 else ((gyroXMSB << 8) | gyroXLSB)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_X_MASK"]
            self.angularVelocity.y = (((gyroYMSB << 8) | gyroYLSB) - 0x10000)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Y_MASK"] if ((gyroYMSB << 8) | gyroYLSB) >= 0x8000 else ((gyroYMSB << 8) | gyroYLSB)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Y_MASK"]
            self.angularVelocity.z = (((gyroZMSB << 8) | gyroZLSB) - 0x10000)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Z_MASK"] if ((gyroZMSB << 8) | gyroZLSB) >= 0x8000 else ((gyroZMSB << 8) | gyroZLSB)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Z_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim açısal hızı okurken hata meydana geldi: {error}", logging.ERROR)
            return None

        if self.debug:
            self.Log(f"Açısal Hız: {self.angularVelocity}", logging.DEBUG)

        return self.angularVelocity

    # Manyetometre (pusula) ölçümü.
    def GetMagnetometer(self):
        try:
            magXLSB, magXMSB, magYLSB, magYMSB, magZLSB, magZMSB = self.I2CReadBlockData(self.address["SELF"], self.address["MAG_X_LSB"], 6)

            self.compass.x = (((magXMSB << 8) | magXLSB) - 0x10000)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_X_MASK"] if ((magXMSB << 8) | magXLSB) >= 0x8000 else ((magXMSB << 8) | magXLSB)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_X_MASK"]
            self.compass.y = (((magYMSB << 8) | magYLSB) - 0x10000)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Y_MASK"] if ((magYMSB << 8) | magYLSB) >= 0x8000 else ((magYMSB << 8) | magYLSB)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Y_MASK"]
            self.compass.z = (((magZMSB << 8) | magZLSB) - 0x10000)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Z_MASK"] if ((magZMSB << 8) | magZLSB) >= 0x8000 else ((magZMSB << 8) | magZLSB)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Z_MASK"]
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim manyetometreyi okurken hata meydana geldi: {error}", logging.ERROR)
            return None
        
        if self.debug:
            self.Log(f"Pusula: {self.compass}", logging.DEBUG)

        return self.compass

    # Kalibrasyon durumu. Durum, 0 ile 3 arasında bir değer alır. 0 hiç kalibrasyon yok demekken, 3 tam kalibre halde demektir.
    def GetCalibrationStatus(self):
        try:
            calibrationStatus = self.I2CReadByteData(self.address["SELF"], self.address["CALIB_STAT"])
        
            if self.lastErrorCode == self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["NO_ERROR"]
                self.Log(f"Birim veri okumaya devam ediyor.", logging.INFO)
        except Exception as error:
            if self.lastErrorCode != self.states["ERROR"]["READ_ERROR"]:
                self.lastErrorCode = self.states["ERROR"]["READ_ERROR"]
                self.Log(f"Birim kalibrasyon durumlarını okurken hata meydana geldi: {error}", logging.ERROR)
            return None

        if calibrationStatus:
            self.sysCalibrationStatus = (calibrationStatus >> 6) & 0x03
            self.accelCalibrationStatus = (calibrationStatus >> 4) & 0x03
            self.magCalibrationStatus = (calibrationStatus >> 2) & 0x03
            self.gyroCalibrationStatus = (calibrationStatus >> 0) & 0x03

        if self.debug:
            self.Log(f"Kalibrasyon Durumları:\n\tSistem: {self.sysCalibrationStatus}\n\tİvme: {self.accelCalibrationStatus}\n\tPusula: {self.magCalibrationStatus}\n\tJiroskop: {self.gyroCalibrationStatus}", logging.DEBUG)

        return calibrationStatus
    
    # Tüm sensör okumalarını aynı anda yapar.
    def ReadAll(self):
        self.GetAcceleration()
        self.GetLinearAcceleration()
        self.GetGravity()
        self.GetEulerOrientation()
        self.GetQuaternionOrientation()
        self.GetAngularVelocity()
        self.GetMagnetometer()
        self.GetCalibrationStatus()
        return True






class MPU9250(IMUBase):
    def __init__(self):
        super().__init__(**kwargs)
        
        self.address = {
            "SELF": 0x28,

            "CONFIG": 0x1A
        }

        self.byteData = {
            "UNIT_SEL": {
                "METRIC": 0x00,
            },
            "OPR_MODE": {
                "CONFIG": 0x00,
                "NDOF": 0x0C, # Tüm sensörler + Mutlak oriyantasyon
            },
            "PWR_MODE": {
                "NORMAL": 0x00,
                "LOWPOWER": 0x01,
                "SUSPEND": 0x02,
            }
        }

        self.settings = {
            "ACCEL_UNIT_LSB": 1/10**2,
            "GRAVITY_UNIT_LSB": 1/10**2,
            "EULER_UNIT_LSB": 1/16,
            "QUATERNION_UNIT_LSB": 1/2**14,
            "GYRO_UNIT_LSB": 1/16,
            "MAG_UNIT_LSB": 1/16,

            "ACCEL_X_MASK": -1,
            "ACCEL_Y_MASK": 1,
            "ACCEL_Z_MASK": 1,

            "GRAVITY_X_MASK": -1,
            "GRAVITY_Y_MASK": -1,
            "GRAVITY_Z_MASK": -1,

            "LINEAR_ACCEL_X_MASK": -1,
            "LINEAR_ACCEL_Y_MASK": 1,
            "LINEAR_ACCEL_Z_MASK": 1,

            "EULER_H_MASK": -1,
            "EULER_R_MASK": -1,
            "EULER_P_MASK": -1,

            "QUATERNION_W_MASK": -1,
            "QUATERNION_X_MASK": -1,
            "QUATERNION_Y_MASK": -1,
            "QUATERNION_Z_MASK": -1,

            "GYRO_X_MASK": -1,
            "GYRO_Y_MASK": -1,
            "GYRO_Z_MASK": -1,

            "MAG_X_MASK": -1,
            "MAG_Y_MASK": -1,
            "MAG_Z_MASK": -1,
        }