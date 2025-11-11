#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import UARTBase
from services import JSONService

########################################
#           RADYO SINIFLAR             #
########################################

class E22LoRa(UARTBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Nesneye özel dönütler
        with open("lib/response/e22lora.json", "r", encoding="utf-8") as f:
            classResponse = json.load(f)
            self.response = JSONService.MergeJSON(self.response, classResponse)

        self.reading = False
        self.open = False
        self.messageWaitTime = kwargs.get("messageWaitTime", 0.01)

        self.debugMessage = kwargs.get("debugMessage", False)

        self.Log("e22lora_init_success", logging.INFO)



    # Birimi açma ve hazırlama işlevi
    def OpenModule(self):
        self.Log("e22lora_module_opening", logging.INFO)
        if self.ser.is_open == False:
            self.OpenSerial()
        if self.ser.is_open:
            self.open = True
            self.Log("e22lora_module_opened", logging.INFO)
        else:
            self.Log("e22lora_module_open_error", logging.ERROR)
        
    # Birimi kapatma işlevi
    def CloseModule(self):
        self.Log("e22lora_module_closing", logging.INFO)
        if self.open:
            self.open = False
            if self. reading:
                self. reading = False
                if hasattr(self, 'readThread'):
                    self.readThread.join()
                    self.Log("e22lora_reading_stopped", logging.INFO)
            self.CloseSerial()
            self.Log("e22lora_module_closed", logging.INFO)
        else:
            self.Log("e22lora_module_already_closed", logging.WARNING)
    
        
    
    # Koşut bildiri okuma işlevi
    def _ReadMessage(self):
        try:
            while self. reading and self.open:
                if self.ser.in_waiting > 0:
                    message = self.ReadFromSerial()
                    #message = self.ser.readline().decode("utf-8").strip()
                    if message:
                        self.queue.put(message)
                else:
                    time.sleep(self.messageWaitTime)
        except Exception as e:
            self.Log(f"e22lora_read_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)
                
    # Paket bildiri yollama işlevi
    def SendMessage(self, message):
        if self.open:
            self.Write(message)

    # Bildiri okuma döngüsü için koşut iş parçacığı başlatma işlevi
    def StartReading(self):
        if not self. reading:
            self. reading = True
            self.readThread = threading.Thread(target=self._ReadMessage)
            self.readThread.start()
            self.Log("e22lora_reading_started", logging.INFO)
        else:
            self.Log("e22lora_reading_already_reading", logging.WARNING)

    # Bildiriı tampondan alma işlevi
    def GetMessage(self):
        if not self.queue.empty():
            # Burada alına bildiryi loglama yapmadan almalıyız
            # çünkü bu işlev sürekli döngüde çalışacak
            # ve loglama çok fazla veri üretebilir.
            # Eğer loglama yapılması isteniyorsa, bu işlev
            # ayar olarak loglama isteği alabilir.
            message = self.queue.get()
            if self.debugMessage:
                self.Log(f"e22lora_message_received", logging.DEBUG)
                self.Log(f"{message}", logging.DEBUG)
            return message
        else:
            return None



class R12DS(UARTBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Nesneye özel dönütler
        with open("lib/response/e22lora.json", "r", encoding="utf-8") as f:
            classResponse = json.load(f)
            self.response = JSONService.MergeJSON(self.response, classResponse)

        self.reading = False
        self.open = False
        self.messageWaitTime = kwargs.get("messageWaitTime", 0.01)

        self.debugMessage = kwargs.get("debugMessage", False)

        self.byteData = {
            "SBUS_START_BYTE": 0x0F,
            "SBUS_END_BYTE": 0x00
        }

        self.Log("e22lora_init_success", logging.INFO)
    


    def OpenModule(self):
        self.serial = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=100000,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_TWO,
            timeout=0.1
        )
        self.serial.flush()

    def CloseModule(self):
        if self.serial.is_open:
            self.serial.close()
            self.uav.interface.Response({"text": f'{self.devName} kapatıldı.', "reason": rs.reasons["DEBUG"]}, self.devName)
        else:
            self.uav.interface.Response({"text": f'{self.devName} zaten kapalı.', "reason": rs.reasons["WARN"]}, self.devName)

    

    def ParseData(self, data):
        if len(data) != 25 or data[0] != self.byteData["SBUS_START_BYTE"]:
            return None

        channels = [0] * 16

        # Bilgi paketini işle.
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

