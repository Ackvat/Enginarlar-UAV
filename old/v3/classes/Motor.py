#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import I2CBase
from services import JSONService

########################################
#           MOTOR SINIFLAR             #
########################################

class PCA9685(I2CBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Nesneye özel dönütler
        with open("lib/response/pca9685.json", "r", encoding="utf-8") as f:
            classResponse = json.load(f)
            self.response = JSONService.MergeJSON(self.response, classResponse)

        self.open = False

        self.servoDebug = False

        self.address = {
            "SELF": 0x40,
            "ALL_CALL": 0x70,

            "MODE1": 0x00,
            "MODE2": 0x01,
            "SUBADR1": 0x02,
            "SUBADR2": 0x03,
            "SUBADR3": 0x04,

            "LED0_ON_L": 0x06,
            "LED0_ON_H": 0x07,
            "LED0_OFF_L": 0x08,
            "LED0_OFF_H": 0x09,
            "ALL_LED_ON_L": 0xFA,
            "ALL_LED_ON_H": 0xFB,
            "ALL_LED_OFF_L": 0xFC,
            "ALL_LED_OFF_H": 0xFD,

            "PRESCALE": 0xFE,
            "RESTART": 0x80,
            "SLEEP": 0x10,
            "ALLCALLADR": 0x70,
            "LED_COUNT": 16
        }

        self.settings = {
            "FREQUENCY": 50, # Varsayılan modül çalışma frekansı
            "MIN_PULSE": 1000, # 1000 @ 50 Hz | 1000 @ 333 Hz
            "MAX_PULSE": 2500, # 2500 @ 50 Hz | 2500 @ 333 Hz
            "PULSE_LENGTH": 4095,  # 12-bit çözünürlük
            "LED_COUNT": 16,  # Azami servo sayısı
            "SERVO_MIN": 0,  # Servolar için asgari açı
            "SERVO_MAX": 180,  # Servolar için azami açı
            "SERVO_DEFAULT": 90  # Servolar için varsayılan açı
        }

        self.Log("pca9685_module_init_success", logging.INFO)



    # Modülü açmak için.
    def OpenModule(self):
        self.Log("pca9685_module_opening", logging.INFO)
        try:
            self.I2CWriteByte(data=0x00) # Alttakiyle aynı şey galiba. Çünkü 0x00 + 0x00 = 0x00.
            self.I2CWriteByteData(offset=self.address["MODE1"], data=0x00)
            self.open = True
            self.Log("pca9685_module_open_success", logging.INFO)
        except Exception as e:
            self.Log("pca9685_module_open_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)

    # Modülü kapatmak için.
    def CloseModule(self):
        self.Log("pca9685_module_closing", logging.INFO)
        try:
            self.I2CWriteByteData(offset=self.address["MODE1"], data=0x10)
            self.open = False
            self.Log("pca9685_module_close_success", logging.INFO)
        except Exception as e:
            self.Log("pca9685_module_close_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)

    # Modülü yeniden başlatır.
    def RestartModule(self):
        self.I2CWriteByteData(offset=self.address["MODE1"], data=0x10)
        self.I2CWriteByteData(offset=self.address["MODE1"], data=0x00)
        self.I2CWriteByteData(offset=self.address["MODE1"], data=0x80)

    

    # PWM kanallarının frekansını ayarlar.
    def SetFrequency(self, frequency):
        if self.open:
            if frequency < 24 or frequency > 1526:
                raise self.log("pca9685_module_wrong_frequency_input", logging.ERROR)

            self.settings["FREQUENCY"] = frequency

            prescaleVal = int(25000000.0 / (4096.0 * frequency) - 1)
            self.I2CWriteByteData(offset=self.address["MODE1"], data=0x10) # Uyku moduna sokar, çünkü ayar sadece uyku modunda yapılır.
            self.I2CWriteByteData(offset=self.address["PRESCALE"], data=prescaleVal) # Ayarı verir. haha.
            self.I2CWriteByteData(offset=self.address["MODE1"], data=0x00) # Uyandırır.
            self.I2CWriteByteData(offset=self.address["MODE1"], data=0x80) # MANTIK yeniden başlatması yapar.

            self.Log("pca9685_module_frequency_change", logging.INFO)
            self.Log(f"Frekans {frequency} Hz olarak ayarlandı.", logging.INFO)

    # Sinyal darbe uzunluğunu ayarlar.
    def SetPulseLength(self, minPulse, maxPulse):
        if self.open:
            if minPulse < 0 or maxPulse > self.settings["PULSE_LENGTH"]:
                self.log("pca96585_module_pulserange_error", logging.ERROR)
                maxLength = self.settings['PULSE_LENGTH']
                self.log("0 ile {maxLength} arasında olmalı!", logging.ERROR)
            if minPulse >= maxPulse:
                self.log("pca96585_module_pulselength_exceed_error")

            self.settings["MIN_PULSE"] = minPulse
            self.settings["MAX_PULSE"] = maxPulse

            self.Log("pca9685_module_pulselength_change", logging.INFO)
            self.Log(f"Darbe uzunlukları {minPulse} ve {maxPulse} olarak ayarlandı.", logging.INFO)
        else:
            self.log("pca9685_module_not_open")

    # Sinyal değer aralığını ayarlar.
    def SetServoAngleRange(self, minAngle, maxAngle):
        if self.open:
            self.settings["SERVO_MIN"] = minAngle
            self.settings["SERVO_MAX"] = maxAngle

            self.Log("pca9685_module_anglerange_change", logging.INFO)
            self.Log(f"Açı aralığı {minAngle} ve {maxAngle} olarak ayarlandı.", logging.INFO)
        else:
            self.log("pca9685_module_not_open")
        
    

    # Servo açısı emretmek için.
    def SetServoAngle(self, servoNum, angle):
        if self.open:
            if servoNum < 0 or servoNum >= self.settings["LED_COUNT"]:
                self.Log("pca9685_module_servochannel_error", logging.ERROR)
                #return False
            if angle < self.settings["SERVO_MIN"] or angle > self.settings["SERVO_MAX"]:
                self.Log("pca96585_module_servoangle_error", logging.ERROR)
                minAngle = self.settings['SERVO_MIN']
                maxAngle = self.settings['SERVO_MAX']
                self.Log(f"Açı, {minAngle} ile {maxAngle} arasında olabilir!", logging.ERROR)
                #return False
            
            # PWM için hesaplama
            minPulse = self.settings["MIN_PULSE"]
            maxPulse = self.settings["MAX_PULSE"]
            pulse = int(minPulse + (angle / (self.settings["SERVO_MAX"] - self.settings["SERVO_MIN"])) * (maxPulse - minPulse))

            on_time = 0
            off_time = pulse

            self.I2CWriteByteData(offset=self.address["LED0_ON_L"] + 4 * servoNum, data=on_time & 0xFF)
            self.I2CWriteByteData(offset=self.address["LED0_ON_H"] + 4 * servoNum, data=on_time >> 8)
            self.I2CWriteByteData(offset=self.address["LED0_OFF_L"] + 4 * servoNum, data=off_time & 0xFF)
            self.I2CWriteByteData(offset=self.address["LED0_OFF_H"] + 4 * servoNum, data=off_time >> 8)

    # Tüm kanalların sinyallerini emreder.
    def SetAllServosAngle(self, angle):
        if self.open:
            if angle < self.settings["SERVO_MIN"] or angle > self.settings["SERVO_MAX"]:
                self.Log("pca96585_module_servoangle_error", logging.ERROR)
                minAngle = self.settings['SERVO_MIN']
                maxAngle = self.settings['SERVO_MAX']
                self.Log(f"Açı, {minAngle} ile {maxAngle} arasında olabilir!", logging.ERROR)
                return False

            for servoNum in range(self.settings["LED_COUNT"]):
                self.SetServoAngle(servoNum, angle)

