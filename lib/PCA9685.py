#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import lib.responseService as rs

########################################
#             PCA9685 SINIFI             #
########################################

class PCA9685:
    def __init__(self, devName="PCA9685", uav=None):
        self.devName = devName

        self.address = {
            "PCA9685": 0x40,
            "ALL CALL": 0x70,

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

        self.response = {
            "PREPARING": {"text": f'{self.devName} hazırlanıyor...', "reason": rs.reasons["DEBUG"]},
            "PREPARED": {"text": f'{self.devName} hazırlandı.', "reason": rs.reasons["DEBUG"]},
            
            "INIT_ERROR": {"text": f'{self.devName} başlatılamadı.', "reason": rs.reasons["ERROR"]}
        }

        self.byteData = {
            
        }
        
        self.settings = {
            "FREQUENCY": 50, # Varsayılan modül çalışma frekansı
            "minPulse": 205, # 205 @ 50 Hz | 1363 @ 333 Hz
            "maxPulse": 410, # 410 @ 50 Hz | 2726 @ 333 Hz
            "PULSE_LENGTH": 4095,  # 12-bit çözünürlük
            "LED_COUNT": 16,  # Azami servo sayısı
            "SERVO_MIN": 0,  # Servolar için asgari açı
            "SERVO_MAX": 180,  # Servolar için azami açı
            "SERVO_DEFAULT": 90  # Servolar için varsayılan açı
        }

        self.uav = uav

        self.uav.interface.Response(self.response["PREPARING"], self.devName)

        self.status = False

        self.Open()

        if self.status:
            self.uav.interface.Response(self.response["PREPARED"], self.devName)
        else:
            self.uav.interface.Response(self.response["INIT_ERROR"], self.devName)
            return None
    
    def SetFrequency(self, frequency):
        if not self.status: return

        if frequency < 24 or frequency > 1526:
            raise ValueError("Frekans 24 Hz ile 1526 Hz arasında olmalıdır.")

        self.settings["FREQUENCY"] = frequency

        prescale_val = int(25000000.0 / (4096.0 * frequency) - 1)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["MODE1"], 0x10)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["PRESCALE"], prescale_val)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["MODE1"], 0x00)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["MODE1"], 0x80)
        self.uav.interface.Response({"text": f"{self.devName} frekansı {frequency} Hz olarak ayarlandı.", "reason": rs.reasons["DEBUG"]}, self.devName)
    
    def SetPulseLength(self, minPulse, maxPulse):
        if not self.status: return

        if minPulse < 0 or maxPulse > self.settings["PULSE_LENGTH"]:
            raise ValueError(f"Minimum ve maksimum darbe uzunlukları 0 ile {self.settings['PULSE_LENGTH']} arasında olmalıdır.")
        if minPulse >= maxPulse:
            raise ValueError("Minimum darbe uzunluğu maksimumdan büyük olamaz.")

        self.settings["minPulse"] = minPulse
        self.settings["maxPulse"] = maxPulse

        self.uav.interface.Response({"text": f"{self.devName} darbe uzunlukları {minPulse} ile {maxPulse} olarak ayarlandı.", "reason": rs.reasons["DEBUG"]}, self.devName)
    
    def SetServoAngle(self, servoNum, angle):
        if not self.status: return

        if servoNum < 0 or servoNum >= self.settings["LED_COUNT"]:
            raise ValueError("Servo numarası 0 ile 15 arasında olmalıdır.")
        if angle < self.settings["SERVO_MIN"] or angle > self.settings["SERVO_MAX"]:
            raise ValueError(f"Açı {self.settings['SERVO_MIN']} ile {self.settings['SERVO_MAX']} arasında olmalıdır.")
        
        # PWM için hesaplama
        minPulse = self.settings["minPulse"]
        maxPulse = self.settings["maxPulse"]
        pulse = int(minPulse + (angle / self.settings["SERVO_MAX"]) * (maxPulse - minPulse))

        on_time = 0
        off_time = pulse

        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["LED0_ON_L"] + 4 * servoNum, on_time & 0xFF)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["LED0_ON_H"] + 4 * servoNum, on_time >> 8)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["LED0_OFF_L"] + 4 * servoNum, off_time & 0xFF)
        self.uav.i2c.write_byte_data(self.address["PCA9685"], self.address["LED0_OFF_H"] + 4 * servoNum, off_time >> 8)

        self.uav.interface.Response({"text": f"{self.devName} servo {servoNum} açısı {angle} olarak ayarlandı.", "reason": rs.reasons["DEBUG"]}, self.devName)
    
    def SetAllServosAngle(self, angle):
        if not self.status: return

        if angle < self.settings["SERVO_MIN"] or angle > self.settings["SERVO_MAX"]:
            raise ValueError(f"Açı {self.settings['SERVO_MIN']} ile {self.settings['SERVO_MAX']} arasında olmalıdır.")

        for servoNum in range(self.settings["LED_COUNT"]):
            self.SetServoAngle(servoNum, angle)

        self.uav.interface.Response({"text": f"{self.devName} tüm servolar {angle} açısına ayarlandı.", "reason": rs.reasons["DEBUG"]}, self.devName)



    def Open(self):
            try:
                self.uav.i2c.write_byte(self.address["PCA9685"], 0x00)
            except Exception as e:
                self.uav.interface.Response({"text": f"{self.devName} açılırken hata oluştu: {str(e)}", "reason": rs.reasons["ERROR"]}, self.devName)
            else:
                self.status = True
                self.uav.interface.Response({"text": f"{self.devName} başarıyla açıldı.", "reason": rs.reasons["DEBUG"]}, self.devName)
        
