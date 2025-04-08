#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import lib.responseService as rs
from lib.mathService import Vector3, Quaternion

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
            "GRAVITY": lambda gravity: {"text": f'{self.devName} yer çekimi: {gravity}', "reason": rs.reasons["VERBOSE"]},
            "QUATERNION_ORIENTATION": lambda quaternion: {"text": f'{self.devName} küresel yönelim (quaternion): {quaternion}', "reason": rs.reasons["VERBOSE"]},
            "CALIB_STAT": lambda status: {"text": f'{self.devName} kalibrasyon durumu: {status}', "reason": rs.reasons["VERBOSE"]},

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
            "GET_GRAVITY_ERROR": lambda error: {"text": f'Yer çekimi okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_QUATERNION_ORIENTATION_ERROR": lambda error: {"text": f'Küresel yönelim (quaternion) okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_CALIBRATION_STATUS_ERROR": lambda error: {"text": f'Kalibrasyon durumu okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
        }
        
        self.settings = {
            "ACCEL_UNIT_LSB": 1/10**2,
            "GRAVITY_UNIT_LSB": 1/10**2,
            "QUATERNION_UNIT_LSB": 1/2**14,

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

        self.uav = uav
        self.i2c = uav.i2c

        self.uav.interface.Response(self.response["PREPARING"], self.devName)

        self.acceleration = Vector3(0, 0, 0)
        self.linearAcceleration = Vector3(0, 0, 0)
        self.gravity = Vector3(0, 0, 0)

        self.eulerOrientation = Vector3(0, 0, 0)
        self.quaternionOrientation = Quaternion(0, 0, 0, 0)
        
        self.angularVelocity = Vector3(0, 0, 0)

        self.compass = Vector3(0, 0, 0)
        

        if not self.CheckChipID():
            self.uav.interface.Response(self.response["INIT_FAILED"], self.devName)
            return None

        self.SetOperatingMode(self.byteData["OPR_MODE"]["CONFIG"])

        self.SetUnitSelector(self.byteData["UNIT_SEL"]["METRIC"])
        self.SetPowerMode(self.byteData["PWR_MODE"]["NORMAL"])

        self.SetOperatingMode(self.byteData["OPR_MODE"]["NDOF"])

        self.uav.interface.Response(self.response["PREPARED"], self.devName)
    
    def CheckChipID(self):
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
    
    def SetUnitSelector(self, unit=0x00):
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

    def SetOperatingMode(self, operatingMode=0x0C):
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

    def SetPowerMode(self, powerMode=0x00):
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


    
    def GetAcceleration(self):
        try:
            accelXLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["ACCEL_X_LSB"])
            accelXMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["ACCEL_X_MSB"])
            accelYLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["ACCEL_Y_LSB"])
            accelYMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["ACCEL_Y_MSB"])
            accelZLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["ACCEL_Z_LSB"])
            accelZMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["ACCEL_Z_MSB"])

            self.acceleration.x = (((accelXMSB << 8) | accelXLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelXMSB << 8) | accelXLSB) >= 0x8000 else ((accelXMSB << 8) | accelXLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.acceleration.y = (((accelYMSB << 8) | accelYLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelYMSB << 8) | accelYLSB) >= 0x8000 else ((accelYMSB << 8) | accelYLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.acceleration.z = (((accelZMSB << 8) | accelZLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelZMSB << 8) | accelZLSB) >= 0x8000 else ((accelZMSB << 8) | accelZLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_ACCELERATION_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["ACCELERATION"](self.acceleration), self.devName)

        return self.acceleration
    
    def GetGravity(self):
        try:
            gravityXLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["GRAVITY_DATA_X_LSB"])
            gravityXMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["GRAVITY_DATA_X_MSB"])
            gravityYLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["GRAVITY_DATA_Y_LSB"])
            gravityYMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["GRAVITY_DATA_Y_MSB"])
            gravityZLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["GRAVITY_DATA_Z_LSB"])
            gravityZMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["GRAVITY_DATA_Z_MSB"])

            self.gravity.x = (((gravityXMSB << 8) | gravityXLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_X_MASK"] if ((gravityXMSB << 8) | gravityXLSB) >= 0x8000 else ((gravityXMSB << 8) | gravityXLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_X_MASK"]
            self.gravity.y = (((gravityYMSB << 8) | gravityYLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Y_MASK"] if ((gravityYMSB << 8) | gravityYLSB) >= 0x8000 else ((gravityYMSB << 8) | gravityYLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Y_MASK"]
            self.gravity.z = (((gravityZMSB << 8) | gravityZLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Z_MASK"] if ((gravityZMSB << 8) | gravityZLSB) >= 0x8000 else ((gravityZMSB << 8) | gravityZLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Z_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_GRAVITY_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["GRAVITY"](self.gravity), self.devName)

        return self.gravity

    def GetQuaternionOrientation(self):
        try:
            quaternionWLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_W_LSB"])
            quaternionWMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_W_MSB"])
            quaternionXLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_X_LSB"])
            quaternionXMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_X_MSB"])
            quaternionYLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_Y_LSB"])
            quaternionYMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_Y_MSB"])
            quaternionZLSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_Z_LSB"])
            quaternionZMSB = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["QUATERNION_DATA_Z_MSB"])

            self.quaternionOrientation.w = (((quaternionWMSB << 8) | quaternionWLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_W_MASK"] if ((quaternionWMSB << 8) | quaternionWLSB) >= 0x8000 else ((quaternionWMSB << 8) | quaternionWLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_W_MASK"]
            self.quaternionOrientation.x = (((quaternionXMSB << 8) | quaternionXLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_X_MASK"] if ((quaternionXMSB << 8) | quaternionXLSB) >= 0x8000 else ((quaternionXMSB << 8) | quaternionXLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_X_MASK"]
            self.quaternionOrientation.y = (((quaternionYMSB << 8) | quaternionYLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Y_MASK"] if ((quaternionYMSB << 8) | quaternionYLSB) >= 0x8000 else ((quaternionYMSB << 8) | quaternionYLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Y_MASK"]
            self.quaternionOrientation.z = (((quaternionZMSB << 8) | quaternionZLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Z_MASK"] if ((quaternionZMSB << 8) | quaternionZLSB) >= 0x8000 else ((quaternionZMSB << 8) | quaternionZLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Z_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_QUATERNION_ORIENTATION_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["QUATERNION_ORIENTATION"](self.quaternionOrientation), self.devName)

        return self.quaternionOrientation

    def GetCalibrationStatus(self):
        try:
            calibrationStatus = self.uav.interface.I2CReadRegister(self.address["BNO055"], self.address["CALIB_STAT"])
        except Exception as error:
            self.uav.interface.Response(self.response["GET_CALIBRATION_STATUS_ERROR"](error), self.devName)
            return None

        sysCalib = (calibrationStatus >> 6) & 0x03
        gyroCalib = (calibrationStatus >> 4) & 0x03
        accelCalib = (calibrationStatus >> 2) & 0x03
        magCalib = calibrationStatus & 0x03

        self.uav.interface.Response(self.response["CALIB_STAT"](f'FULL: {hex(calibrationStatus)} SYS: {sysCalib}, GYRO: {gyroCalib}, ACCEL: {accelCalib}, MAG: {magCalib}'), self.devName)

        return calibrationStatus

    def SuspendSensor(self):
        self.SetPowerMode(self.byteData["PWR_MODE"]["SUSPEND"])
        return True
