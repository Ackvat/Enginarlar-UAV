#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import serial

import lib.responseService as rs

########################################
#             R12DS SINIFI             #
########################################

class R12DS:
    def __init__(self, devName="R12DS", uav=None):
        self.devName = devName

        self.response = {
            "PREPARING": {"text": f'{self.devName} hazırlanıyor...', "reason": rs.reasons["DEBUG"]},
            "PREPARED": {"text": f'{self.devName} hazırlandı.', "reason": rs.reasons["DEBUG"]},
        }

        self.byteData = {
            "SBUS_START_BYTE": 0x0F,
            "SBUS_END_BYTE": 0x00
        }
        
        self.settings = {
        }

        self.uav = uav

        self.uav.interface.Response(self.response["PREPARING"], self.devName)

        self.Open()

        self.uav.interface.Response(self.response["PREPARED"], self.devName)
    
    def ParseData(self, data):
        if len(data) != 25 or data[0] != self.byteData["SBUS_START_BYTE"]:
            return None

        channels = [0] * 16

        # Bilgi paketini açma işlemi.
        channels[0]  = (data[1]     | data[2]  << 8) & 0x07FF
        channels[1]  = (data[2]  >> 3 | data[3]  << 5) & 0x07FF
        channels[2]  = (data[3]  >> 6 | data[4]  << 2 | data[5] << 10) & 0x07FF
        channels[3]  = (data[5]  >> 1 | data[6]  << 7) & 0x07FF
        channels[4]  = (data[6]  >> 4 | data[7]  << 4) & 0x07FF
        channels[5]  = (data[7]  >> 7 | data[8]  << 1 | data[9] << 9) & 0x07FF
        channels[6]  = (data[9]  >> 2 | data[10] << 6) & 0x07FF
        channels[7]  = (data[10] >> 5 | data[11] << 3) & 0x07FF
        channels[8]  = (data[12]     | data[13] << 8) & 0x07FF
        channels[9]  = (data[13] >> 3 | data[14] << 5) & 0x07FF
        channels[10] = (data[14] >> 6 | data[15] << 2 | data[16] << 10) & 0x07FF
        channels[11] = (data[16] >> 1 | data[17] << 7) & 0x07FF
        channels[12] = (data[17] >> 4 | data[18] << 4) & 0x07FF
        channels[13] = (data[18] >> 7 | data[19] << 1 | data[20] << 9) & 0x07FF
        channels[14] = (data[20] >> 2 | data[21] << 6) & 0x07FF
        channels[15] = (data[21] >> 5 | data[22] << 3) & 0x07FF

        flags = data[23]
        ch17 = bool(flags & (1 << 0))
        ch18 = bool(flags & (1 << 1))
        failsafe = bool(flags & (1 << 3))

        return channels, ch17, ch18, failsafe

    def Read(self):
        if self.serial.in_waiting > 0:
            data = self.serial.read(self.serial.in_waiting)
            return self.ParseData(data)
        return None
    

    
    def Open(self):
        self.serial = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=100000,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_TWO,
            timeout=0.1
        )
        self.serial.flush()

    def Close(self):
        if self.serial.is_open:
            self.serial.close()
            self.uav.interface.Response({"text": f'{self.devName} kapatıldı.', "reason": rs.reasons["DEBUG"]}, self.devName)
        else:
            self.uav.interface.Response({"text": f'{self.devName} zaten kapalı.', "reason": rs.reasons["WARN"]}, self.devName)