from dotenv import load_dotenv

import adafruit_bno055

import lib.ackmetton as acklib

devName = "BNO055"
ack = acklib.Ackmetton(name=devName, color="GREEN")
load_dotenv()

# Yeni sensör değeri eklendiğinde, GetError kısmına eklemelerini yapmayı unutma!!!

class Sensor:
    def __init__(self, uav=None, i2c=None):
        ack.Debug(f'Sensör hazırlanıyor...', color="CYAN")

        try:
            self.name = devName
            self.uav = uav

            self.count = True

            self.i2c = i2c
            self.sensor = adafruit_bno055.BNO055_I2C(i2c)
            self.lastTemperature = 0
            self.tempSuccessCount = 0
            self.tempErrorCount = 0
            self.tempErrorRatio = 1

            self.lastGravity = (0, 0, 0)
            self.gravitySuccessCount = 0
            self.gravityErrorCount = 0
            self.gravityErrorRatio = 1

            self.lastEuler = (0, 0, 0)
            self.eulerSuccessCount = 0
            self.eulerErrorCount = 0
            self.eulerErrorRatio = 1
        except Exception as error:
            ack.Error(f'Sensör hazırlanırken bir hata oluştu.\n\t{error}')

        ack.Debug(f'Sensör başarıyla aşağıdaki parametrelerle hazırlandı:\n\tI2C arayüzü = {self.i2c}', color="GREEN")

    def GetGravity(self):
        ack.Debug(f'Yer çekimi değeri okunuyor...')
        result = self.sensor.gravity

        ack.Verbose(f'Okunan ve son yer çekimi değeri: {result}/{self.lastGravity}')
        
        if result[0] is None:
            ack.Warn(f'Yer çekimi değeri okunamadı. Veri çöpe atılıyor ve eski değer geçiliyor.')
            if self.count: self.gravityErrorCount += 1
            return self.lastGravity
        else:
            self.lastGravity = result
            if self.count: self.gravitySuccessCount += 1
            return result
    
    def GetEuler(self):
        ack.Debug(f'Euler açı değeri okunuyor...')
        result = self.sensor.euler

        ack.Verbose(f'Okunan ve son euler değeri: {result}/{self.lastEuler}')
        
        if result[0] is None:
            ack.Warn(f'Euler açı değeri okunamadı. Veri çöpe atılıyor ve eski değer geçiliyor.')
            if self.count: self.eulerErrorCount += 1
            return self.lastEuler
        else:
            self.lastEuler = result
            if self.count: self.eulerSuccessCount += 1
            return result

    def GetTemperature(self):
        ack.Debug(f'Sıcaklık değeri okunuyor...')
        result = self.sensor.temperature

        if abs(result - self.lastTemperature) == 128:
            ack.Debug(f'Okunan değer, son değerden 128 birim farklı.')
            result = self.sensor.temperature
            if abs(result - self.lastTemperature) == 128:
                ack.Debug(f'Yeniden okunan değer, son değerden 128 birim farklı.')
                return 0b00111111 & result

        ack.Verbose(f'Okunan ve son sıcaklık değerleri: {result}/{self.lastTemperature}')
        
        if result < 0:
            ack.Warn(f'Sıcaklık değeri negatif görüldü. Veri çöpe atılıyor ve eski değer geçiliyor.')
            if self.count: self.tempErrorCount += 1
            return self.lastTemperature
        else:
            self.lastTemperature = result
            if self.count: self.tempSuccessCount += 1
            return result
    
    def GetError(self):
        if self.tempErrorCount > 0:
            self.tempErrorRatio = self.tempSuccessCount/self.tempErrorCount
            ack.Verbose(f'Sıcaklık sensör okuma başarı oranı: {self.tempErrorRatio:.2f}', color="GREEN" if self.tempErrorRatio >= 1 else "RED")

        if self.gravityErrorCount > 0:
            self.gravityErrorRatio = self.gravitySuccessCount/self.gravityErrorCount
            ack.Verbose(f'Yer çekimi sensör okuma başarı oranı: {self.gravityErrorRatio:.2f}', color="GREEN" if self.gravityErrorRatio >= 1 else "RED")

        if self.eulerErrorCount > 0:
            self.eulerErrorRatio = self.eulerSuccessCount/self.eulerErrorCount
            ack.Verbose(f'Euler açı sensör okuma başarı oranı: {self.eulerErrorRatio:.2f}', color="GREEN" if self.eulerErrorRatio >= 1 else "RED")
