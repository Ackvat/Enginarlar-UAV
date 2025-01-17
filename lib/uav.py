from dotenv import load_dotenv

import board

import lib.ackmetton as acklib

import lib.imu as imulib
import lib.nacelle as nacellelib

devName = "UAV"
ack = acklib.Ackmetton(name=devName, color="WHITE")
load_dotenv()

class UAV:
    def __init__(self, adress=0x40, channels=16, freq=333, actuationRange=190, pwRange=[500, 2600]):
        ack.Debug(f'İHA hazırlanıyor...', color="CYAN")

        try:
            self.name = devName

            self.i2c = board.I2C()

            self.nacelles = nacellelib.Nacelles(uav=self)
            self.imu = imulib.Sensor(uav=self, i2c=self.i2c)
        except Exception as error:
            ack.Error(f'İHA hazırlanırken bir hata oluştu.\n\t{error}')
        