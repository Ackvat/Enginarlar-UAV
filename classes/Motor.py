#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import I2CBase

import services.mathService as math

########################################
#           MOTOR SINIFLAR             #
########################################

class MotorDriverBase(I2CBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.open = False
        self.running = False
        self.runType = kwargs.get("runType", 0)
        self.signalUpdateFrequency = kwargs.get("signalUpdateFrequency", 120)
    


    # Birimi açmak için.
    def OpenModule(self):
        self.Log("Birim başlatılıyor...", logging.INFO)
        if self.open:
            self.Log("Birim zaten açık!", logging.WARNING)
            return True
        else:
            try:
                self.open = True
                self.Log("Birim başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False

    # Birimi kapatmak için.
    def CloseModule(self):
        self.Log("Birim kapatılıyor...", logging.INFO)
        self.StopSignalLoop()
        if self.open:
            try:
                self.open = False
                self.Log("Birim kapatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim kapatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Birim zaten kapalı!", logging.WARNING)
            return True
    
    # Motor sürücüsünün sinyal ayarlama döngüsünü başlatma işlevi.
    def StartSignalLoop(self):
        self.Log("Birim sinyal ayarlama döngüsü başlatılıyor...", logging.INFO)

        if self.open and not self.running:
            self.running = True
            try:
                if self.runType == 0:
                    self.signalThread = threading.Thread(target=self._SignalLoop, daemon=True)
                    self.signalThread.start()
                    self.Log("Birim sinyal ayarlama döngüsü tek yordam koşutuyla başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim sinyal ayarlama döngüsü başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        elif self.open and self.running:
            self.Log("Birim sinyal ayarlama döngüsü zaten çalışıyor!", logging.WARNING)
            return True
        else:
            self.Log("Birim kapalı! Sinyal ayarlama döngüsü başlatılamaz!", logging.WARNING)
            return True

    # Motor sürücüsünün sinyal ayarlama döngüsü durdurur.
    def StopSignalLoop(self):
        if self.running:
            self.running = False
            try:
                if hasattr(self, 'signalThread'):
                    self.signalThread.join()
                self.Log("Birim sinyal ayarlama döngüsü durduruldu.", logging.INFO)
            except Exception as e:
                self.Log(f"Birimin sinyal ayarlama döngüsü kapatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Birim sanal sinyal ayarlama kapısı açıkken, sinyal ayarlama döngüsünün kendisi bulunamadı!", logging.WARNING)






class PCA9685(MotorDriverBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.signals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.address = {
            "SELF": 0x40,
            "ALL_CALL": 0x70,

            "MODE1": 0x00,
            "MODE2": 0x01,
            "SUBADR1": 0x02,
            "SUBADR2": 0x03,
            "SUBADR3": 0x04,

            "LED0_ON_L": 0x06,
            "LED0_ON_H": 0x07,
            "LED0_OFF_L": 0x08,
            "LED0_OFF_H": 0x09,
            "ALL_LED_ON_L": 0xFA,
            "ALL_LED_ON_H": 0xFB,
            "ALL_LED_OFF_L": 0xFC,
            "ALL_LED_OFF_H": 0xFD,

            "PRESCALE": 0xFE,
            "RESTART": 0x80,
            "SLEEP": 0x10,
            "ALLCALLADR": 0x70,
            "CHANNEL_COUNT": 16
        }

        self.settings = {
            "FREQUENCY": 50, # Varsayılan Birim çalışma frekansı
            "MIN_FREQUENCY": 24,
            "MAX_FREQUENCY": 1526,
            "MIN_PULSE": 1000, # 1000 @ 50 Hz | 1000 @ 333 Hz
            "MAX_PULSE": 2500, # 2500 @ 50 Hz | 2500 @ 333 Hz
            "MIN_PULSE_CHANNELS": [1000, 1000, 1000, 1000, 750, 750, 750, 750, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
            "MAX_PULSE_CHANNELS": [2500, 2500, 2500, 2500, 3600, 3600, 3600, 3600, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500],
            "PULSE_CHOICE": 1,
            "PULSE_LENGTH": 4095,  # 12-bit çözünürlük
            "CHANNEL_COUNT": 16,  # Azami servo sayısı
            "MIN_SIGNAL": 0,  # Servolar için asgari açı
            "MAX_SIGNAL": 180,  # Servolar için azami açı
            "DEF_SIGNAL": 90  # Servolar için varsayılan açı
        }

        self.lastInvalidSignal = 0
    


    # Birimin sinyal döngüsü. Bu döngü ayrı bir koşutda çalışarak, anayordam koşutunu meşgul etmemeli. Aksi takdirde, smbus2 kütüphanesinin talep yöneticisi devreye girmiyor.
    def _SignalLoop(self):
        while self.open and self.running:
            try:
                for i in range(8):
                    self.SetChannelSignal(i, self.signals[i])
            except Exception as error:
                pass
        return True



    # Birimi açmak için. [ÜSTÜN]
    def OpenModule(self):
        self.Log("Birim başlatılıyor...", logging.INFO)
        if self.open:
            self.Log("Birim zaten açık!", logging.WARNING)
            return True
        else:
            try:
                self.I2CWriteByte(address=self.address["SELF"], data=0x00) # Alttakiyle aynı şey galiba. Çünkü 0x00 + 0x00 = 0x00.
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x00)
                self.open = True
                self.Log("Birim başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False

    # Birimi kapatmak için. [ÜSTÜN]
    def CloseModule(self):
        self.Log("Birim kapatılıyor...", logging.INFO)
        self.StopSignalLoop()
        if self.open:
            try:
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x10)
                self.open = False
                self.Log("Birim kapatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Birim kapatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Birim zaten kapalı!", logging.WARNING)
            return True

    # Birimi yeniden başlatır.
    def RestartModule(self):
        self.Log("Birim yeniden başlatılıyor...", logging.INFO)
        try:
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x10)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x00)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x80)
            self.Log("Birim yeniden başlatıldı.", logging.INFO)
            return True
        except Exception as e:
            self.Log(f"Birim yeniden başlatılırken bir hata oluştu! {e}", logging.ERROR)
            return False
    
    

    # DİKKAT!!! Birim açıkken (MODE1 = 0x00) bu ayar işlevları çalışmaz!
    # PWM kanallarının frekansını ayarlar.
    def SetFrequency(self, frequency):
        try:
            if frequency < self.settings["MIN_FREQUENCY"] or frequency > self.settings["MAX_FREQUENCY"]:
                self.log(f"Birim için geçerli frekans aralığı dışında bir ayar talebinde bulunuldu! Gerekli ayar {self.settings['MIN_FREQUENCY']} Hz ve {self.settings['MAX_FREQUENCY']} Hz arasında olmalıdır!", logging.ERROR)
                return False

            self.settings["FREQUENCY"] = frequency

            prescaleVal = int(25000000.0 / (4096.0 * frequency) - 1)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x10) # Uyku moduna sokar, çünkü ayar sadece uyku modunda yapılır.
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["PRESCALE"], data=prescaleVal) # Ayarı verir. haha.
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x00) # Uyandırır.
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x80) # MANTIK yeniden başlatması yapar.

            self.Log(f"Birimin frekans ayarı {frequency} Hz olarak ayarlandı.", logging.INFO)
            return True
        except Exception as e:
            self.Log(f"Birimin frekans ayarı yapılırken bir hata oluştu! {e}", logging.ERROR)
            return False

    # Sinyal darbe uzunluğunu ayarlar.
    def SetPulseLength(self, minPulse, maxPulse):
        if minPulse < 0 or maxPulse > self.settings["PULSE_LENGTH"]:
            self.log(f"Birim için talep edilen sinyal darbe uzunluğu ayarı, sınırların dışında! Sinyal darbe uzunluğu 0 us ve {self.settings['PULSE_LENGTH']} us arasında olabilir!", logging.ERROR)
            return False
        if minPulse >= maxPulse:
            self.log(f"Birim için talep edilen asgari sinyal darbe uzunluğu, azami sinyal darbe uzunluğundan fazla! Talepdeki asgari değer: {minPulse} ve azami değer: {maxPulse}.", logging.ERROR)
            return False

        self.settings["MIN_PULSE"] = minPulse
        self.settings["MAX_PULSE"] = maxPulse

        self.Log(f"Birimin asgari ve azami sinyal darbe uzunluğu {minPulse} ve {maxPulse} olarak değiştirildi.", logging.INFO)
        return True

    # Sinyal değer aralığını ayarlar.
    def SetSignalRange(self, minSignal, maxSignal):
        self.settings["MIN_SIGNAL"] = minSignal
        self.settings["MAX_SIGNAL"] = maxSignal

        self.Log(f"Birim için sinyal limitleri {minSignal} ve {maxSignal} olarak değiştirildi.", logging.INFO)
        return True
    
    def SetSignalRangeChannels(self, minSignal, maxSignal):
        self.settings["MIN_SIGNAL_CHANNELS"] = minSignal
        self.settings["MAX_SIGNAL_CHANNELS"] = maxSignal

        self.Log(f"Birim için kanallarına özel sinyal limitleri {minSignal} ve {maxSignal} olarak değiştirildi.", logging.INFO)
        return True
        
    

    # Sinyal değeri ayarlamak için.
    def SetChannelSignal(self, channel, signal):
        if self.open:
            if self.settings["PULSE_CHOICE"] == 0:
                minPulse = self.settings["MIN_SIGNAL"]
                maxPulse = self.settings["MAX_SIGNAL"]
            elif self.settings["PULSE_CHOICE"] == 1:
                minPulse = self.settings["MIN_SIGNAL_CHANNELS"][channel]
                maxPulse = self.settings["MAX_SIGNAL_CHANNELS"][channel]

            # Sakat değerleri ayıklar.
            if channel < 0 or channel >= self.settings["CHANNEL_COUNT"]:
                self.Log(f"Verilen kanal numarası {channel}, Birimin sahip olduğu kanal sayısından ya fazla ya da negatif!", logging.WARNING)
                return False
            if (signal < self.settings["MIN_SIGNAL"] or signal > self.settings["MAX_SIGNAL"]) and signal != self.lastInvalidSignal:
                self.lastInvalidSignal = signal # Yoksa kumanda kapalıyken, log dosyasını doldurup taşırıyor.
                self.Log(f"Verilen sinyal değeri {signal}, asgari {self.settings['MIN_SIGNAL']} ve azami {self.settings['MAX_SIGNAL']} sinyal değerinin dışında!", logging.WARNING)
                return False
            
            # PWM için hesaplama
            pulse = int(math.Map(signal, self.settings["MIN_SIGNAL"], self.settings["MAX_SIGNAL"], minPulse, maxPulse))
            on_time = 0
            off_time = pulse
            
            # Teker teker adreslere verileri yollar. Ne kadar verimsiz olsada, şu anda PCA9685 için düzgün çalışan tek yöntem bu. TODO: Optimizasyon sonra yapılacak.
            try:
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_ON_L"] + 4 * channel, data=on_time & 0xFF)
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_ON_H"] + 4 * channel, data=on_time >> 8)
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_OFF_L"] + 4 * channel, data=off_time & 0xFF)
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_OFF_H"] + 4 * channel, data=off_time >> 8)
                return True
            except Exception as error:
                self.Log(f"Birime kanal sinyal ayarı için emir geldi ancak I2C paket yazma sırasında bir hata oluştu! {error}", logging.ERROR)
                return False
        else:
            self.Log("Birime kanal sinyal değişimi için emir geldi ancak birim açık değil!", logging.ERROR)
            return False
    
    # Otomatik adım atma özelliği ile tüm kanallara sinyal değeri ayarlamak için. !!!DİKKAT!!! 16 kanal için 64 byte paket büyüklüğü gerekiyor, ancak smbus2, I2C blok verisi yazmak için azami 32 byte destekliyor. Bunun yanında, otomatik adım atma PCA9685 için şu anda çalışmıyor, sebebini bulamadım.
    def SetBlockChannelSignal(self, channels=[0, 1, 2, 3], signals=[0, 0, 0, 0]):
        if self.open:

            dataToWrite = bytearray(32)
            for i in range(len(channels)):
                # PWM için hesaplama
                pulse = int(math.Map(signals[i], self.settings["MIN_SIGNAL"], self.settings["MAX_SIGNAL"], self.settings["MIN_PULSE"], self.settings["MAX_PULSE"]))
                on_time = 0
                off_time = pulse

                dataOffset = 4 * channels[i]
                dataToWrite[dataOffset + 0] = on_time & 0xFF
                dataToWrite[dataOffset + 1] = on_time >> 8
                dataToWrite[dataOffset + 2] = pulse & 0xFF
                dataToWrite[dataOffset + 3] = pulse >> 8
            try:
                self.I2CWriteBlockData(address=self.address["SELF"], offset=self.address["LED0_ON_L"], data=dataToWrite)
            except Exception as error:
                self.Log(f"Birim tüm kanallarına sinyal verisi işlerken bir hata oluştu! {error}", logging.ERROR)
            return True
        else:
            self.Log("Birime kanal sinyal değişimi için emir geldi ancak birim açık değil!", logging.ERROR)
            return False

    # Tüm kanalların sinyallerini ayarlar. TODO: Şu anda SetBlockChannelSignal ile aynı şekilde çalışıyor. Daha sonra döngü ile her bir kanala tekil sinyal ayarı ile yazması için değiştirilecek. Ancak zaten kullanım amacımızı karşılamayacak bir işlev.
    def SetAllBlockChannelSignal(self, signal):
        if self.open:
            pulse = int(math.Map(signal, self.settings["MIN_SIGNAL"], self.settings["MAX_SIGNAL"], self.settings["MIN_PULSE"], self.settings["MAX_PULSE"]))
            on_time = 0
            off_time = pulse

            dataToWrite = bytearray(32)
            dataToWrite[0] = on_time & 0xFF
            dataToWrite[1] = on_time >> 8
            dataToWrite[2] = pulse & 0xFF
            dataToWrite[3] = pulse >> 8

            self.I2CWriteBlockData(address=self.address["SELF"], offset=self.address["ALL_LED_ON_L"], data=dataToWrite)
        else:
            self.Log("Birime tüm kanalların sinyal değişimi için emir geldi ancak Birim açık değil!", logging.ERROR)
            return False

