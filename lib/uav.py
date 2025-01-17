from dotenv import load_dotenv

import board

import lib.ackmetton as acklib

import lib.imu as imulib
import lib.motor as motorlib

devName = "UAV"
ack = acklib.Ackmetton(name=devName, color="WHITE")
load_dotenv()

class UAV:
    def __init__(self, freq=1):
        ack.Debug(f'İHA hazırlanıyor...', color="CYAN")

        try:
            self.name = devName

            self.i2c = board.I2C()

            self.motors = motorlib.Motors(uav=self)
            self.imu = imulib.Sensor(uav=self, i2c=self.i2c)

            self.systemFrequency = freq
            self.systemPeriod = 1/freq
        except Exception as error:
            ack.Error(f'İHA hazırlanırken bir hata oluştu.\n\t{error}')
        
        ack.Debug(f'İHA başarıyla aşağıdaki parametrelerle hazırlandı:\n\tSistem frekansı = {freq}\n\tMotor sürücüsü = {self.motors}\n\tAtalet sensörü = {self.imu}', color="GREEN")