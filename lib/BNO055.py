#!/venv/bin/python3
from lib.mathService import Vector3

########################################
#            BAĞLANTILAR               #
########################################

import lib.responseService as rs

########################################
#            BNO055 SINIFI             #
########################################

class BNO055:
    def __init__(self, devName="BNO055", uav=None):
        self.devName = devName

        self.address = {
            "BNO055": 0x28,

            "CHIP_ID": 0x00,
            "ACCEL_X_LSB": 0x08,
            "ACCEL_X_MSB": 0x09,
            
            "TEMP": 0x34,
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
                "NDOF": 0x0C,
            },
            "PWR_MODE": {
                "NORMAL": 0x00,
                "LOWPOWER": 0x01,
                "SUSPEND": 0x02,
            }
        }

        self.response = {
            "PREPARING": {"text": f'{self.devName} hazırlanıyor...', "reason": rs.reasons["DEBUG"]},
            "PREPARED": {"text": f'{self.devName} hazırlandı.', "reason": rs.reasons["DEBUG"]},

            "CHIP_ID": lambda chipID: {"text": f'{self.devName} çip kimliği: {chipID}', "reason": rs.reasons["VERBOSE"]},
            "UNIT_SEL": lambda unit: {"text": f'{self.devName} birim seçimi: {hex(unit)}', "reason": rs.reasons["VERBOSE"]},
            "OPR_MODE": lambda mode: {"text": f'{self.devName} çalışma modu: {hex(mode)}', "reason": rs.reasons["VERBOSE"]},
            "PWR_MODE": lambda mode: {"text": f'{self.devName} güç modu: {hex(mode)}', "reason": rs.reasons["VERBOSE"]},
            "ACCELERATION": lambda accel: {"text": f'{self.devName} ivme: {accel}', "reason": rs.reasons["VERBOSE"]},

            "CHIP_ID_CORRECT": {"text": "Sensör çip kimliği doğrulandı!", "reason": rs.reasons["SUCCESS"]},

            "WRONG_CHIP_ID": {"text": "Sensör çip kimliği yanlış!", "reason": rs.reasons["FAIL"]},
            "INIT_FAILED": {"text": f'{self.devName} başlatılamadı!', "reason": rs.reasons["FAIL"]},

            "CHECK_CHIP_ID_ERROR": {"text": "Sensör çip kimliği doğrulanamadı!", "reason": rs.reasons["ERROR"]},
            "UNIT_SEL_INVALID_SELECTION": {"text": "Geçersiz birim seçimi!", "reason": rs.reasons["ERROR"]},
            "UNIT_SEL_ERROR": lambda error: {"text": f'Birim seçimi hatası: {error}', "reason": rs.reasons["ERROR"]},
            "OPR_MODE_INVALID_SELECTION": {"text": "Geçersiz çalışma modu seçimi!", "reason": rs.reasons["ERROR"]},
            "SET_OPR_MODE_ERROR": lambda error: {"text": f'Çalışma modu ayarı hatası: {error}', "reason": rs.reasons["ERROR"]},
            "PWR_MODE_INVALID_SELECTION": {"text": "Geçersiz güç modu seçimi!", "reason": rs.reasons["ERROR"]},
            "SET_PWR_MODE_ERROR": lambda error: {"text": f'Güç modu ayarı hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_ACCELERATION_ERROR": lambda error: {"text": f'İvme okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
        }
        
        self.settings = {
            "ACCEL_UNIT_LSB": 1/100,
        }

        self.uav = uav
        self.i2c = uav.i2c

        self.uav.interface.Response(self.response["PREPARING"], self.devName)

        self.acceleration = Vector3(0, 0, 0)

        if not self.checkChipID():
            self.uav.interface.Response(self.response["INIT_FAILED"], self.devName)
            return None

        self.setOperatingMode(self.byteData["OPR_MODE"]["CONFIG"])

        self.setUnitSelector(self.byteData["UNIT_SEL"]["METRIC"])
        self.setPowerMode(self.byteData["PWR_MODE"]["NORMAL"])

        self.setOperatingMode(self.byteData["OPR_MODE"]["NDOF"])

        self.uav.interface.Response(self.response["PREPARED"], self.devName)
    
    def checkChipID(self):
        try:
            self.i2c.write_byte(self.address["BNO055"], self.address["CHIP_ID"])
            chipID = self.i2c.read_byte(self.address["BNO055"])
        except Exception as error:
            self.uav.interface.Response(self.response["CHECK_CHIP_ID_ERROR"], self.devName)
            return False

        self.uav.interface.Response(self.response["CHIP_ID"](chipID), self.devName)

        if chipID != 0xA0:
            self.uav.interface.Response(self.response["WRONG_CHIP_ID"], self.devName)
            return False

        self.uav.interface.Response(self.response["CHIP_ID_CORRECT"], self.devName)
        return True
    
    def setUnitSelector(self, unit=0x00):
        if not unit in self.byteData["UNIT_SEL"].values():
            self.uav.interface.Response(self.response["UNIT_SEL_INVALID_SELECTION", self.devName])
            return False

        try:
            self.i2c.write_byte_data(self.address["BNO055"], self.address["UNIT_SEL"], unit)
        except Exception as error:
            self.uav.interface.Response(self.response["SET_UNIT_SEL_ERROR"](error), self.devName)
            return False

        self.uav.interface.Response(self.response["UNIT_SEL"](unit), self.devName)

        return True

    def setOperatingMode(self, operatingMode=0x0C):
        if not operatingMode in self.byteData["OPR_MODE"].values():
            self.uav.interface.Response(self.response["OPR_MODE_INVALID_SELECTION"], self.devName)
            return False

        try:
            self.i2c.write_byte_data(self.address["BNO055"], self.address["OPR_MODE"], operatingMode)
        except Exception as error:
            self.uav.interface.Response(self.response["SET_OPR_MODE_ERROR"](error), self.devName)
            return False

        self.uav.interface.Response(self.response["OPR_MODE"](operatingMode), self.devName)

        return True

    def setPowerMode(self, powerMode=0x00):
        if not powerMode in self.byteData["PWR_MODE"].values():
            self.uav.interface.Response(self.response["PWR_MODE_INVALID_SELECTION"], self.devName)
            return False
        
        try:
            self.i2c.write_byte_data(self.address["BNO055"], self.address["PWR_MODE"], powerMode)
        except Exception as error:
            self.uav.interface.Response(self.response["SET_PWR_MODE_ERROR"](error), self.devName)
            return False

        self.uav.interface.Response(self.response["PWR_MODE"](powerMode), self.devName)

        return True


    
    def getAcceleration(self):
        try:
            self.i2c.write_byte(self.address["BNO055"], self.address["ACCEL_X_LSB"])
            accelX_LSB = self.i2c.read_byte(self.address["BNO055"])
            self.i2c.write_byte(self.address["BNO055"], self.address["ACCEL_X_MSB"])
            accelX_MSB = self.i2c.read_byte(self.address["BNO055"])

            self.acceleration.x = (((accelX_MSB << 8) | accelX_LSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"] if ((accelX_MSB << 8) | accelX_LSB) >= 0x8000 else ((accelX_MSB << 8) | accelX_LSB)*self.settings["ACCEL_UNIT_LSB"]
            self.acceleration.y = 0
            self.acceleration.z = 0
        except Exception as error:
            self.uav.interface.Response(self.response["GET_ACCELERATION_ERROR"](error), self.devName)
            return False

        self.uav.interface.Response(self.response["ACCELERATION"](self.acceleration), self.devName)

        return self.acceleration



    def suspendSensor(self):
        self.setPowerMode(self.byteData["PWR_MODE"]["SUSPEND"])
        return True
