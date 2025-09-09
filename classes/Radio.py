#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import UARTBase

########################################
#           RADYO SINIFLAR             #
########################################

class RadioTelemetryBase(UARTBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.reading = False
        self.open = False
        self.messageWaitTime = kwargs.get("messageWaitTime", 0.01)



    # Modülü açma ve hazırlama fonksiyonu
    def OpenModule(self):
        self.Log("Modül başlatılıyor...", logging.INFO)
        if hasattr(self.ser, "is_open") and self.ser.is_open:
            if self.open:
                self.Log("Modül zaten açık!", logging.WARNING)
            else:
                self.open = True
                self.Log("Modül seri portu açık ancak sanal kapı yeni açıldı!", logging.WARNING)
            return True
        else:
            if self.open:
                self.Log("Modül seri portu açık değilken, sanal kapısı açıktı!", logging.WARNING)
            self.open = self.OpenSerial()
            if self.open:
                self.Log("Modül başlatıldı.", logging.INFO)
                return True
            else:
                self.Log("Modül başlatılırken bir hata oluştu!", logging.ERROR)
                return False
                
    
    # Modülü kapatma fonksiyonu
    def CloseModule(self):
        self.Log("Modül kapatılıyor...", logging.INFO)
        if self.reading:
            self.reading = False
            if hasattr(self, 'readThread'):
                try:
                    self.readThread.join()
                    self.Log("Modül seri okuma döngüsü durduruldu.", logging.INFO)
                except Exception as e:
                    self.Log(f"Modülün seri okuma döngüsü kapatılırken bir hata oluştu! {e}", logging.ERROR)
                    return False
            else:
                self.Log("Modül sanal seri okuma kapısı açıkken, seri okuma döngüsünün kendisi bulunamadı!", logging.WARNING)
        self.CloseSerial()
        if self.open:
            self.open = False
            self.Log("Modül kapatıldı.", logging.INFO)
        else:
            self.Log("Modül sanal kapısı zaten kapalıydı!", logging.WARNING)
    

    # Mesaj okuma döngüsü için paralel iş parçacığı başlatma fonksiyonu
    def StartReading(self):
        self.Log("Modül seri okuma döngüsü başlatılıyor...", logging.INFO)
        if self.open and not self.reading:
            try:
                self.readThread = threading.Thread(target=self._ReadMessage, daemon=True)
                self.readThread.start()
                self.Log("Modül seri okuma döngüsü başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Modül seri okuma döngüsü başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Modül seri okuma döngüsü zaten çalışıyor!", logging.WARNING)
            return True

    # Mesajı tampondan alma fonksiyonu
    def GetMessage(self):
        if not self.queue.empty():
            # Burada alına mesajı loglama yapmadan almalıyız
            # çünkü bu fonksiyon sürekli döngüde çalışacak
            # ve loglama çok fazla veri üretebilir.
            # Eğer loglama yapılması isteniyorsa, bu fonksiyon
            # ayar olarak loglama isteği alabilir.
            message = self.queue.get()
            if self.debug:
                self.Log(f"Modülün aldığı mesaj: {message}", logging.DEBUG)
            return message
        else:
            return None






class E22LoRa(RadioTelemetryBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
 
    
    # Paralel mesaj okuma fonksiyonu
    def _ReadMessage(self):
        self.reading = True
        while self.open and self.reading:
            if self.ser.in_waiting > 0:
                message = self.ReadLine()
                if message:
                    self.queue.put(message)
            else:
                time.sleep(self.messageWaitTime)
                
    # Paket mesaj yollama fonksiyonu
    def SendMessage(self, message):
        if self.open:
            self.WriteToSerial(message)
            return True
        else:
            return False






class R12DS(RadioTelemetryBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = {
            "PACKET_SIZE": 25,
        }

        self.byteData = {
            "SBUS_START_BYTE": 0x0F,
            "SBUS_END_BYTE": 0x00
        }



    # Paralel mesaj okuma fonksiyonu
    def _ReadMessage(self):
        self.reading = True
        while self.open and self.reading:
            if self.ser.in_waiting >= self.settings["PACKET_SIZE"]:
                message = self.ReadAllInWaiting(size=self.settings["PACKET_SIZE"])
                if message:
                    self.queue.put(message)
            else:
                time.sleep(self.messageWaitTime)

    def ParseData(self, data):
        if len(data) != self.settings["PACKET_SIZE"] or data[0] != self.byteData["SBUS_START_BYTE"]:
            return None

        channels = [0] * 16

        # Bit paketini işle.
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

