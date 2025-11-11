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

        self.open = False
        self.running = False
        self.runType = kwargs.get("runType", 0)
        self.messageFrequency = kwargs.get("messageFrequency", 60)



    # Birimi açma ve hazırlama işlevi
    def OpenModule(self):
        self.Log("Birim başlatılıyor...", logging.INFO)
        if hasattr(self.ser, "is_open") and self.ser.is_open:
            if self.open:
                self.Log("Birim zaten açık!", logging.WARNING)
            else:
                self.open = True
                self.Log("Birim seri portu açık ancak sanal kapı yeni açıldı!", logging.WARNING)
            return True
        else:
            if self.open:
                self.Log("Birim seri portu açık değilken, sanal kapısı açıktı!", logging.WARNING)
            self.open = self.OpenSerial()
            if self.open:
                self.Log("Birim başlatıldı.", logging.INFO)
                return True
            else:
                self.Log("Birim başlatılırken bir hata oluştu!", logging.ERROR)
                return False
                
    # Birimi kapatma işlevi
    def CloseModule(self):
        self.Log("Birim kapatılıyor...", logging.INFO)
        self.StopMessageLoop()
        if self.open:
            self.CloseSerial()
            self.open = False
            self.Log("Birim kapatıldı.", logging.INFO)
        else:
            self.Log("Birim sanal kapısı zaten kapalıydı!", logging.WARNING)
        return True
    


    # Bildiri okuma döngüsü için koşut iş parçacığı başlatma işlevi.
    def StartMessageLoop(self):
        self.Log("Birim seri bildiri döngüsü başlatılıyor...", logging.INFO)

        if self.open and not self.running:
            self.running = True
            try:
                if self.runType == 0:
                    self.messageThread = threading.Thread(target=self._MessageLoop, daemon=True)
                    self.messageThread.start()
                    self.Log("Birim seri bildiri döngüsü tek yordam koşutuyla başlatıldı.", logging.INFO)
                if self.runType == 1:
                    self.readThread = threading.Thread(target=self._ReadLoop, daemon=True)
                    self.writeThread = threading.Thread(target=self._WriteLoop, daemon=True)
                    self.readThread.start()
                    self.writeThread.start()
                    self.Log("Birim seri bildiri döngüsü çift yordam koşutuyla başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim seri bildiri döngüsü başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        elif self.open and self.running:
            self.Log("Birim seri bildiri döngüsü zaten çalışıyor!", logging.WARNING)
            return True
        else:
            self.Log("Birim kapalı! Seri bildiri döngüsü başlatılamaz!", logging.WARNING)
            return True

    # Bildiri okuma döngüsü durdurur.
    def StopMessageLoop(self):
        if self.running:
            self.running = False
            try:
                if hasattr(self, 'messageThread'):
                    self.messageThread.join()
                if hasattr(self, 'readThread'):
                    self.readThread.join()
                if hasattr(self, 'writeThread'):
                    self.writeThread.join()
                self.Log("Birim seri okuma döngüsü durduruldu.", logging.INFO)
            except Exception as e:
                self.Log(f"Birimin seri okuma döngüsü kapatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Birim sanal seri okuma kapısı açıkken, seri okuma döngüsünün kendisi bulunamadı!", logging.WARNING)

    # Bildiriı tampondan alma işlevi
    def GetMessage(self):
        if not self.inQueue.empty():
            message = self.inQueue.get()
            if self.debug:
                self.Log(f"Birimden alınan bildiri: {message}", logging.DEBUG)
            return message
        else:
            return None
    
    # Paket bildiri yollama işlevi
    def SendMessage(self, message):
        self.outQueue.put(message)
        return True






class E22LoRa(RadioTelemetryBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
 
    
    # Koşut bildiri okuma işlevi.
    def _MessageLoop(self):
        self.lastEnqueueTime = 0

        while self.open and self.running:
            readMessage = False
            wroteMessage = False
            if self.ser.in_waiting > 0:
                message = self.ReadLine()
                if message:
                    #nowTime = time.time()
                    #if nowTime - self.lastEnqueueTime >= (1/self.messageFrequency):
                        #self.ser.reset_input_buffer()
                        #self.lastEnqueueTime = nowTime
                    self.inQueue.put(message)
                    readMessage = True
            if not self.outQueue.empty():
                #self.ser.reset_output_buffer()
                message = self.outQueue.get()
                self.Write(message)
                wroteMessage = True
            if not readMessage and not wroteMessage:
                time.sleep(1/self.messageFrequency)
    
    # Yalın okuma koşutu.
    def _ReadLoop(self):
        self.lastEnqueueTime = 0

        while self.open and self.running:
            readMessage = False
            if self.ser.in_waiting > 0:
                message = self.ReadLine()
                if message:
                    nowTime = time.time()
                    if nowTime - self.lastEnqueueTime >= (1/self.messageFrequency):
                        self.inQueue.put(message)
                        #self.ser.reset_input_buffer()
                        self.lastEnqueueTime = nowTime
                        readMessage = True
            else:
                time.sleep(1/self.messageFrequency)
    
    # Yalın yazma koşutu.
    def _WriteLoop(self):
        while self.open and self.running:
            wroteMessage = False
            if not self.outQueue.empty():
                #self.ser.reset_output_buffer()
                message = self.outQueue.get()
                self.Write(message)
                wroteMessage = True
            else:
                time.sleep(1/self.messageFrequency)
    


    # Çöp.
    def GetConfigurationParameters(self):
        self.ser.write(b"AT+PARAM?\r\n")
        self.ser.flush()
        time.sleep(0.1)
        params = self.ser.read(100).decode('utf-8')
        self.Log(f"Params: {params}", logging.INFO)





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



    # Koşut bildiri okuma işlevi
    def _MessageLoop(self):
        self.lastEnqueueTime = 0

        while self.open and self.running:
            readMessage = False
            if self.ser.in_waiting >= self.settings["PACKET_SIZE"]:
                message = self.Read(size=self.settings["PACKET_SIZE"])
                if message:
                    #nowTime = time.time()
                    #if nowTime - self.lastEnqueueTime >= (1/self.messageFrequency):
                        #self.lastEnqueueTime = nowTime
                    self.inQueue.put(self.ParseData(message))
                    readMessage = True
            if not readMessage: 
                time.sleep(1/self.messageFrequency)

    # Gelen kumanda verisini çözer.
    def ParseData(self, data):
        if len(data) != self.settings["PACKET_SIZE"] or data[0] != self.byteData["SBUS_START_BYTE"]:
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

