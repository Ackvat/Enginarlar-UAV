#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import os
import datetime
import json
import logging
from queue import Queue

from services import JSONService

# UARTBase için
import serial

########################################
#           TABAN SINIFLAR             #
########################################

class Base:
    def __init__(self, **kwargs):
        # Nesne dili, dönütleri ve ismi
        with open("lib/response/base.json", "r", encoding="utf-8") as f:
            self.response = json.load(f)
        self.lang = kwargs.get("lang", "tr")
        self.name = kwargs.get("name", self.response["no_name"][self.lang])

        # FIFO eylem sıralama nesnesi
        self.queue = Queue()
        
        # Log nesnesi ve ayarları
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.DEBUG)
        if not self.log.handlers:
            os.makedirs("logs", exist_ok=True)
            currentDate = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            os.makedirs(f'logs/{currentDate}', exist_ok=True)
            logPath = f"logs/{currentDate}/{self.name.strip().lower()}.log"
            handler = logging.FileHandler(logPath, encoding="utf-8", mode="w")
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(asctime)s | %(message)s')
            handler.setFormatter(formatter)
            self.log.addHandler(handler)
    
    # Tüm nesneler için loglama fonksiyonu
    def Log(self, response, level=logging.DEBUG):
        if response not in self.response:
            textResponse = response
        else:
            if self.lang not in self.response[response]:
                textResponse = self.response["unknown_language"].get("en", "unknown_language")
            else:
                textResponse = self.response[response].get(self.lang, response)

        self.log.log(level, textResponse)

        

class UARTBase(Base):
    def __init__(self, **kwargs):
        super().__init__(logName="uartBase", **kwargs)

        # Nesneye özel dönütler
        with open("lib/response/uartbase.json", "r", encoding="utf-8") as f:
            classResponse = json.load(f)
            self.response = JSONService.MergeJSON(self.response, classResponse)

        # Varsayılan seri arayüzü
        self.ser = kwargs.get("serial", serial.Serial(
            port=kwargs.get("port", "/dev/ttyAMA0"),
            baudrate=kwargs.get("baudrate", 9600),
            timeout=kwargs.get("timeout", 1)
        ))

        # Arayüzü temizle
        self.ser.flushInput()  # Giriş tamponunu temizle

    # Arayüzü başlatma
    def Open(self):
        self.Log("opening", logging.INFO)
        if not self.ser.is_open:
            try:
                self.ser.open()
                self.Log("open_success", logging.INFO)
            except serial.SerialException as e:
                self.Log(f"open_error: {e}", logging.ERROR)
                raise e
        else:
            self.Log("already_open", logging.WARNING)
    
    # Arayüzü kapat
    def Close(self):
        self.Log("closing", logging.INFO)
        if self.ser.is_open:
            try:
                self.ser.close()
                self.Log("close_success", logging.INFO)
            except serial.SerialException as e:
                self.Log(f"close_error: {e}", logging.ERROR)
                raise e
        else:
            self.Log("already_closed", logging.WARNING)

    # Veri gönderme
    def Write(self, data, newLine=True):
        if not self.ser.is_open:
            self.Log("not_open", logging.ERROR)
            return False
        try:
            # Burada loglama olmamalı çünkü yüksek döngülerde kullanılabilir
            if newLine:
                data += '\n'
            else:
                data += ''
            self.ser.write(data.encode('utf-8'))
            return True
        except serial.SerialException as e:
            self.Log("write_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)
            return False
    
    # Veri okuma
    def Read(self, size=1):
        if not self.ser.is_open:
            self.Log("not_open", logging.ERROR)
            return None
        try:
            # Burada loglama olmamalı çünkü yüksek döngülerde kullanılabilir
            data = self.ser.readline().decode('utf-8').strip()
            return data
        except serial.SerialException as e:
            self.Log("read_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)
            return None
