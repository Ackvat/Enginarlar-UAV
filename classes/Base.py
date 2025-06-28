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

        self.ser = kwargs.get("serial", None)  # Seri arayüzü nesnesi

        self.OpenSerial(**kwargs)  # Seri arayüzü başlatma

    # Arayüzü başlatma
    def OpenSerial(self, **kwargs):
        self.Log("uart_opening", logging.INFO)
        if self.ser is None:
            self.Log("uart_no_serial", logging.ERROR)
            self.Log("uart_initiating_port", logging.INFO)

            try:
                # Varsayılan seri arayüzü
                self.ser = serial.Serial(
                    port=kwargs.get("port", "/dev/ttyAMA0"),
                    baudrate=kwargs.get("baudrate", 9600),
                    timeout=kwargs.get("timeout", 1),
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                )
                self.ser.flushInput()  # Giriş tamponunu temizle
                return True
            except Exception as e:
                self.Log(f"uart_open_error", logging.ERROR)
                self.Log(f"{e}", logging.ERROR)
                return False
        else:
            if not self.ser.is_open:
                try:
                    self.ser.open()
                    self.ser.flushInput()  # Giriş tamponunu temizle
                    self.Log("uart_open_success", logging.INFO)
                    return True
                except serial.SerialException as e:
                    self.Log(f"uart_open_error: {e}", logging.ERROR)
                    self.Log(f"{e}", logging.ERROR)
                    return False
            else:
                self.Log("uart_already_open", logging.WARNING)
                return True
    
    # Arayüzü kapat
    def CloseSerial(self):
        self.Log("uart_closing", logging.INFO)
        if self.ser.is_open:
            try:
                self.ser.close()
                self.Log("uart_close_success", logging.INFO)
                return True
            except serial.SerialException as e:
                self.Log(f"uart_close_error: {e}", logging.ERROR)
                self.Log(f"{e}", logging.ERROR)
                return False
        else:
            self.Log("uart_already_closed", logging.WARNING)
            return True

    # Arayüz kanalını değiştirme fonksiyonu
    def ChangeSerial(self, **kwargs):
        self.Log("uart_changing", logging.INFO)
        if self.CloseSerial():
            pass
            

    # Veri gönderme
    def WriteToSerial(self, data, newLine=True):
        if not self.ser.is_open:
            self.Log("uart_not_open", logging.ERROR)
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
            self.Log("uart_write_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)
            return False
    
    # Veri okuma
    def ReadFromSerial(self, size=1):
        if not self.ser.is_open:
            self.Log("uart_not_open", logging.ERROR)
            return None
        try:
            # Burada loglama olmamalı çünkü yüksek döngülerde kullanılabilir
            data = self.ser.readline().decode('utf-8').strip()
            return data
        except serial.SerialException as e:
            self.Log("uart_read_error", logging.ERROR)
            self.Log(f"{e}", logging.ERROR)
            return None
