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

        self.running = False
        self.open = False
        self.messageWaitTime = kwargs.get("messageWaitTime", 0.01)

        self.logMessage = False

        self.OpenModule()

        self.Log("e22lora_init_success", logging.INFO)
    
    # Paralel mesaj okuma fonksiyonu
    def _ReadMessage(self):
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    message = self.ser.readline().decode("utf-8").strip()
                    if message:
                        self.queue.put(message)
                except Exception as e:
                    self.Log(f"uart_read_error", logging.ERROR)
                    self.Log(f"{e}", logging.ERROR)
            else:
                time.sleep(self.messageWaitTime)

    # Modülü açma ve hazırlama fonksiyonu
    def OpenModule(self):
        self.Log("e22lora_module_opening", logging.INFO)
        if self.ser.is_open == False:
            self.OpenSerial()
        
        if self.ser.is_open:
            self.open = True
            self.Log("e22lora_module_opened", logging.INFO)
        else:
            self.Log("e22lora_module_open_error", logging.ERROR)
        
    # Modülü kapatma fonksiyonu
    def CloseModule(self):
        self.Log("e22lora_module_closing", logging.INFO)
        if self.open:
            self.open = False
            if self.running:
                self.running = False
                if hasattr(self, 'readThread'):
                    self.readThread.join()
                    self.Log("e22lora_reading_stopped", logging.INFO)
            self.CloseSerial()
            self.Log("e22lora_module_closed", logging.INFO)
        else:
            self.Log("e22lora_module_already_closed", logging.WARNING)

    # Mesajı tampondan alma fonksiyonu
    def GetMessage(self):
        if not self.queue.empty():
            # Burada alına mesajı loglama yapmadan alıyoruz
            # çünkü bu fonksiyon sürekli döngüde çalışacak
            # ve loglama çok fazla veri üretebilir.
            # Eğer loglama yapılması isteniyorsa, bu fonksiyon
            # ayar olarak loglama isteği alabilir.
            message = self.queue.get()
            if self.logMessage:
                self.Log(f"e22lora_message_received", logging.INFO)
                self.Log(f"{message}", logging.INFO)
            return message
        else:
            if self.logMessage:
                self.Log("e22lora_no_message", logging.WARNING)
            return None

    # Mesaj okuma döngüsü için paralel iş parçacığı başlatma fonksiyonu
    def StartReading(self):
        if not self.running:
            self.running = True
            self.readThread = threading.Thread(target=self._ReadMessage)
            self.readThread.start()
            self.Log("e22lora_reading_started", logging.INFO)
        else:
            self.Log("e22lora_reading_already_running", logging.WARNING)
