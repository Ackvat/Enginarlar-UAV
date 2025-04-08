from dotenv import load_dotenv

from adafruit_servokit import ServoKit

import lib.responseService as acklib

devName = "PCA9685"
ack = acklib.Ackmetton(name=devName, color="RED")
load_dotenv()

class Motors:
    def __init__(self, uav=None, adress=0x40, channels=16, freq=333, actuationRange=190, pwRange=[500, 2600]):
        ack.Debug(f'Sürücü hazırlanıyor...', color="CYAN")

        try:
            self.name = devName
            self.uav = uav

            self.driver = ServoKit(channels=16)
            self.driver.address = 0x40
            self.driver.frequency = 333

            self.driver.servo[0].actuation_range = 190
            self.driver.servo[0].set_pulse_width_range(500, 2600)
        except Exception as error:
            ack.Error(f'Sürücü hazırlanırken bir hata oluştu.\n\t{error}')
        
        ack.Debug(f'Sürücü başarıyla aşağıdaki parametrelerle hazırlandı:\n\tKanal Sayısı = {channels}\n\tFrekans = {freq} Hz\n\tAzami Açı = {actuationRange} derece\n\tPW Aralığı = [{pwRange[0]}, {pwRange[1]}] us', color="GREEN")
    
    def SetNacelle(self, nacelle=0, angle=95):
        ack.Verbose(f'{nacelle}. Servo -> {angle} derece.')
        self.driver.servo[nacelle].angle = angle
        