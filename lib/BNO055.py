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
            "LINEAR_ACCELERATION": lambda linAccel: {"text": f'{self.devName} doğrusal ivme: {linAccel}', "reason": rs.reasons["VERBOSE"]},
            "GRAVITY": lambda gravity: {"text": f'{self.devName} yer çekimi: {gravity}', "reason": rs.reasons["VERBOSE"]},
            "EULER_ORIENTATION": lambda euler: {"text": f'{self.devName} küresel yönelim (Euler): {euler}', "reason": rs.reasons["VERBOSE"]},
            "QUATERNION_ORIENTATION": lambda quaternion: {"text": f'{self.devName} küresel yönelim (Quaternion): {quaternion}', "reason": rs.reasons["VERBOSE"]},
            "ANGULAR_VELOCITY": lambda gyro: {"text": f'{self.devName} açısal hız: {gyro}', "reason": rs.reasons["VERBOSE"]},
            "MAGNETOMETER": lambda mag: {"text": f'{self.devName} manyetometre: {mag}', "reason": rs.reasons["VERBOSE"]},
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
            "GET_LINEAR_ACCELERATION_ERROR": lambda error : {"text": f'Doğrusal ivme okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_GRAVITY_ERROR": lambda error: {"text": f'Yer çekimi okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_EULER_ORIENTATION_ERROR": lambda error: {"text": f'Küresel yönelim (Euler) okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_QUATERNION_ORIENTATION_ERROR": lambda error: {"text": f'Küresel yönelim (Quaternion) okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_ANGULAR_VELOCITY_ERROR": lambda error: {"text": f'Açısal hız okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_MAGNETOMETER_ERROR": lambda error: {"text": f'Manyetometre okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
            "GET_CALIBRATION_STATUS_ERROR": lambda error: {"text": f'Kalibrasyon durumu okuma hatası: {error}', "reason": rs.reasons["ERROR"]},
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

        self.uav = uav

        self.uav.interface.Response(self.response["PREPARING"], self.devName)

        self.sysCalibrationStatus = 0
        self.accelCalibrationStatus = 0
        self.magCalibrationStatus = 0
        self.gyroCalibrationStatus = 0

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
            self.uav.i2c.write_byte(self.address["BNO055"], self.address["CHIP_ID"])
            chipID = self.uav.i2c.read_byte(self.address["BNO055"])
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
            self.uav.i2c.write_byte_data(self.address["BNO055"], self.address["UNIT_SEL"], unit)
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
            self.uav.i2c.write_byte_data(self.address["BNO055"], self.address["OPR_MODE"], operatingMode)
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
            self.uav.i2c.write_byte_data(self.address["BNO055"], self.address["PWR_MODE"], powerMode)
        except Exception as error:
            self.uav.interface.Response(self.response["SET_PWR_MODE_ERROR"](error), self.devName)
            return False

        self.uav.interface.Response(self.response["PWR_MODE"](powerMode), self.devName)

        return True

    def GetAcceleration(self):
        try:
            accelXLSB, accelXMSB, accelYLSB, accelYMSB, accelZLSB, accelZMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["ACCEL_X_LSB"], 6)

            self.acceleration.x = (((accelXMSB << 8) | accelXLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelXMSB << 8) | accelXLSB) >= 0x8000 else ((accelXMSB << 8) | accelXLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.acceleration.y = (((accelYMSB << 8) | accelYLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelYMSB << 8) | accelYLSB) >= 0x8000 else ((accelYMSB << 8) | accelYLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.acceleration.z = (((accelZMSB << 8) | accelZLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((accelZMSB << 8) | accelZLSB) >= 0x8000 else ((accelZMSB << 8) | accelZLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_ACCELERATION_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["ACCELERATION"](self.acceleration), self.devName)

        return self.acceleration
    
    def GetLinearAcceleration(self):
        try:
            linAccelXLSB, linAccelXMSB, linAccelYLSB, linAccelYMSB, linAccelZLSB, linAccelZMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["LINEAR_ACCEL_DATA_X_LSB"], 6)

            self.linearAcceleration.x = (((linAccelXMSB << 8) | linAccelXLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((linAccelXMSB << 8) | linAccelXLSB) >= 0x8000 else ((linAccelXMSB << 8) | linAccelXLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.linearAcceleration.y = (((linAccelYMSB << 8) | linAccelYLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((linAccelYMSB << 8) | linAccelYLSB) >= 0x8000 else ((linAccelYMSB << 8) | linAccelYLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
            self.linearAcceleration.z = (((linAccelZMSB << 8) | linAccelZLSB) - 0x10000)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"] if ((linAccelZMSB << 8) | linAccelZLSB) >= 0x8000 else ((linAccelZMSB << 8) | linAccelZLSB)*self.settings["ACCEL_UNIT_LSB"]*self.settings["ACCEL_X_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_LINEAR_ACCELERATION_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["LINEAR_ACCELERATION"](self.linearAcceleration), self.devName)

        return self.linearAcceleration

    def GetGravity(self):
        try:
            gravityXLSB, gravityXMSB, gravityYLSB, gravityYMSB, gravityZLSB, gravityZMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["GRAVITY_DATA_X_LSB"], 6)

            self.gravity.x = (((gravityXMSB << 8) | gravityXLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_X_MASK"] if ((gravityXMSB << 8) | gravityXLSB) >= 0x8000 else ((gravityXMSB << 8) | gravityXLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_X_MASK"]
            self.gravity.y = (((gravityYMSB << 8) | gravityYLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Y_MASK"] if ((gravityYMSB << 8) | gravityYLSB) >= 0x8000 else ((gravityYMSB << 8) | gravityYLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Y_MASK"]
            self.gravity.z = (((gravityZMSB << 8) | gravityZLSB) - 0x10000)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Z_MASK"] if ((gravityZMSB << 8) | gravityZLSB) >= 0x8000 else ((gravityZMSB << 8) | gravityZLSB)*self.settings["GRAVITY_UNIT_LSB"]*self.settings["GRAVITY_Z_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_GRAVITY_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["GRAVITY"](self.gravity), self.devName)

        return self.gravity

    def GetEulerOrientation(self):
        try:
            eulerHLSB, eulerHMSB, eulerRLSB, eulerRMSB, eulerPLSB, eulerPMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["EULER_H_LSB"], 6)

            self.eulerOrientation.x = (((eulerHMSB << 8) | eulerHLSB) - 0x10000)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_H_MASK"] if ((eulerHMSB << 8) | eulerHLSB) >= 0x8000 else ((eulerHMSB << 8) | eulerHLSB)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_H_MASK"]
            self.eulerOrientation.y = (((eulerRMSB << 8) | eulerRLSB) - 0x10000)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_R_MASK"] if ((eulerRMSB << 8) | eulerRLSB) >= 0x8000 else ((eulerRMSB << 8) | eulerRLSB)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_R_MASK"]
            self.eulerOrientation.z = (((eulerPMSB << 8) | eulerPLSB) - 0x10000)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_P_MASK"] if ((eulerPMSB << 8) | eulerPLSB) >= 0x8000 else ((eulerPMSB << 8) | eulerPLSB)*self.settings["EULER_UNIT_LSB"]*self.settings["EULER_P_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_EULER_ORIENTATION_ERROR"](error), self.devName)
            return None
        
        self.uav.interface.Response(self.response["EULER_ORIENTATION"](self.eulerOrientation), self.devName)

        return self.eulerOrientation

    def GetQuaternionOrientation(self):
        try:
            quaternionWLSB, quaternionWMSB, quaternionXLSB, quaternionXMSB, quaternionYLSB, quaternionYMSB, quaternionZLSB, quaternionZMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["QUATERNION_DATA_W_LSB"], 8)

            self.quaternionOrientation.w = (((quaternionWMSB << 8) | quaternionWLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_W_MASK"] if ((quaternionWMSB << 8) | quaternionWLSB) >= 0x8000 else ((quaternionWMSB << 8) | quaternionWLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_W_MASK"]
            self.quaternionOrientation.x = (((quaternionXMSB << 8) | quaternionXLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_X_MASK"] if ((quaternionXMSB << 8) | quaternionXLSB) >= 0x8000 else ((quaternionXMSB << 8) | quaternionXLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_X_MASK"]
            self.quaternionOrientation.y = (((quaternionYMSB << 8) | quaternionYLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Y_MASK"] if ((quaternionYMSB << 8) | quaternionYLSB) >= 0x8000 else ((quaternionYMSB << 8) | quaternionYLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Y_MASK"]
            self.quaternionOrientation.z = (((quaternionZMSB << 8) | quaternionZLSB) - 0x10000)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Z_MASK"] if ((quaternionZMSB << 8) | quaternionZLSB) >= 0x8000 else ((quaternionZMSB << 8) | quaternionZLSB)*self.settings["QUATERNION_UNIT_LSB"]*self.settings["QUATERNION_Z_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_QUATERNION_ORIENTATION_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["QUATERNION_ORIENTATION"](self.quaternionOrientation), self.devName)

        return self.quaternionOrientation

    def GetAngularVelocity(self):
        try:
            gyroXLSB, gyroXMSB, gyroYLSB, gyroYMSB, gyroZLSB, gyroZMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["GYRO_X_LSB"], 6)

            self.angularVelocity.x = (((gyroXMSB << 8) | gyroXLSB) - 0x10000)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_X_MASK"] if ((gyroXMSB << 8) | gyroXLSB) >= 0x8000 else ((gyroXMSB << 8) | gyroXLSB)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_X_MASK"]
            self.angularVelocity.y = (((gyroYMSB << 8) | gyroYLSB) - 0x10000)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Y_MASK"] if ((gyroYMSB << 8) | gyroYLSB) >= 0x8000 else ((gyroYMSB << 8) | gyroYLSB)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Y_MASK"]
            self.angularVelocity.z = (((gyroZMSB << 8) | gyroZLSB) - 0x10000)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Z_MASK"] if ((gyroZMSB << 8) | gyroZLSB) >= 0x8000 else ((gyroZMSB << 8) | gyroZLSB)*self.settings["GYRO_UNIT_LSB"]*self.settings["GYRO_Z_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_ANGULAR_VELOCITY_ERROR"](error), self.devName)
            return None

        self.uav.interface.Response(self.response["ANGULAR_VELOCITY"](self.angularVelocity), self.devName)

        return self.angularVelocity

    def GetMagnetometer(self):
        try:
            magXLSB, magXMSB, magYLSB, magYMSB, magZLSB, magZMSB = self.uav.i2c.read_i2c_block_data(self.address["BNO055"], self.address["MAG_X_LSB"], 6)

            self.compass.x = (((magXMSB << 8) | magXLSB) - 0x10000)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_X_MASK"] if ((magXMSB << 8) | magXLSB) >= 0x8000 else ((magXMSB << 8) | magXLSB)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_X_MASK"]
            self.compass.y = (((magYMSB << 8) | magYLSB) - 0x10000)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Y_MASK"] if ((magYMSB << 8) | magYLSB) >= 0x8000 else ((magYMSB << 8) | magYLSB)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Y_MASK"]
            self.compass.z = (((magZMSB << 8) | magZLSB) - 0x10000)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Z_MASK"] if ((magZMSB << 8) | magZLSB) >= 0x8000 else ((magZMSB << 8) | magZLSB)*self.settings["MAG_UNIT_LSB"]*self.settings["MAG_Z_MASK"]
        except Exception as error:
            self.uav.interface.Response(self.response["GET_MAGNETOMETER_ERROR"](error), self.devName)
            return None
        
        self.uav.interface.Response(self.response["MAGNETOMETER"](self.compass), self.devName)

        return self.compass

    def GetCalibrationStatus(self):
        try:
            calibrationStatus = self.uav.i2c.read_byte_data(self.address["BNO055"], self.address["CALIB_STAT"])
        except Exception as error:
            self.uav.interface.Response(self.response["GET_CALIBRATION_STATUS_ERROR"](error), self.devName)
            return None

        self.sysCalibrationStatus = (calibrationStatus >> 6) & 0x03
        self.accelCalibrationStatus = (calibrationStatus >> 4) & 0x03
        self.magCalibrationStatus = (calibrationStatus >> 2) & 0x03
        self.gyroCalibrationStatus = (calibrationStatus >> 0) & 0x03

        self.uav.interface.Response(self.response["CALIB_STAT"](f'Sys: {self.sysCalibrationStatus}, Accel: {self.accelCalibrationStatus}, Mag: {self.magCalibrationStatus}, Gyro: {self.gyroCalibrationStatus}'), self.devName)

        return calibrationStatus



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

    def SuspendSensor(self):
        self.SetPowerMode(self.byteData["PWR_MODE"]["SUSPEND"])
        return True

    def WakeUpSensor(self):
        self.SetPowerMode(self.byteData["PWR_MODE"]["NORMAL"])
        return True

