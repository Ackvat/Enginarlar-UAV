#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json
import logging
import time
import threading

from classes.Base import I2CBase

########################################
#           MOTOR SINIFLAR             #
########################################

class PCA9685(I2CBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.open = False

        self.servoDebug = False

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
            "FREQUENCY": 50, # Varsayılan modül çalışma frekansı
            "MIN_FREQUENCY": 24,
            "MAX_FREQUENCY": 1526,
            "MIN_PULSE": 1000, # 1000 @ 50 Hz | 1000 @ 333 Hz
            "MAX_PULSE": 2500, # 2500 @ 50 Hz | 2500 @ 333 Hz
            "PULSE_LENGTH": 4095,  # 12-bit çözünürlük
            "CHANNEL_COUNT": 16,  # Azami servo sayısı
            "MIN_SIGNAL": 0,  # Servolar için asgari açı
            "MAX_SIGNAL": 180,  # Servolar için azami açı
            "DEF_SIGNAL": 90  # Servolar için varsayılan açı
        }



    # Modülü açmak için.
    def OpenModule(self):
        self.Log("Modül başlatılıyor...", logging.INFO)
        if self.open:
            self.Log("Modül zaten açık!", logging.WARNING)
            return True
        else:
            try:
                self.I2CWriteByte(address=self.address["SELF"], data=0x00) # Alttakiyle aynı şey galiba. Çünkü 0x00 + 0x00 = 0x00.
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x00)
                self.open = True
                self.Log("Modül başlatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Modül başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False

    # Modülü kapatmak için.
    def CloseModule(self):
        self.Log("Modül kapatılıyor...", logging.INFO)
        if self.open:
            try:
                self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x10)
                self.CloseI2C()
                self.open = False
                self.Log("Modül kapatıldı.", logging.INFO)
                return True
            except Exception as e:
                self.Log(f"Modül kapatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            self.Log("Modül zaten kapalı!", logging.WARNING)
            return True

    # Modülü yeniden başlatır.
    def RestartModule(self):
        self.Log("Modül yeniden başlatılıyor...", logging.INFO)
        try:
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x10)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x00)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x80)
            self.Log("Modül yeniden başlatıldı.", logging.INFO)
            return True
        except Exception as e:
            self.Log(f"Modül yeniden başlatılırken bir hata oluştu! {e}", logging.ERROR)
            return False

    

    # DİKKAT!!! Modül açıkken (MODE1 = 0x00) bu ayar fonksiyonları çalışmaz!
    # PWM kanallarının frekansını ayarlar.
    def SetFrequency(self, frequency):
        try:
            if frequency < self.settings["MIN_FREQUENCY"] or frequency > self.settings["MAX_FREQUENCY"]:
                self.log(f"Modül için geçerli frekans aralığı dışında bir ayar talebinde bulunuldu! Gerekli ayar {self.settings['MIN_FREQUENCY']} Hz ve {self.settings['MAX_FREQUENCY']} Hz arasında olmalıdır!", logging.ERROR)
                return False

            self.settings["FREQUENCY"] = frequency

            prescaleVal = int(25000000.0 / (4096.0 * frequency) - 1)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x10) # Uyku moduna sokar, çünkü ayar sadece uyku modunda yapılır.
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["PRESCALE"], data=prescaleVal) # Ayarı verir. haha.
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x00) # Uyandırır.
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["MODE1"], data=0x80) # MANTIK yeniden başlatması yapar.

            self.Log(f"Modülün frekans ayarı {frequency} Hz olarak ayarlandı.", logging.INFO)
            return True
        except Exception as e:
            self.Log(f"Modülün frekans ayarı yapılırken bir hata oluştu! {e}", logging.ERROR)
            return False

    # Sinyal darbe uzunluğunu ayarlar.
    def SetPulseLength(self, minPulse, maxPulse):
        if minPulse < 0 or maxPulse > self.settings["PULSE_LENGTH"]:
            self.log(f"Modül için talep edilen sinyal darbe uzunluğu ayarı, sınırların dışında! Sinyal darbe uzunluğu 0 us ve {self.settings['PULSE_LENGTH']} us arasında olabilir!", logging.ERROR)
            return False
        if minPulse >= maxPulse:
            self.log(f"Modül için talep edilen asgari sinyal darbe uzunluğu, azami sinyal darbe uzunluğundan fazla! Talepdeki asgari değer: {minPulse} ve azami değer: {maxPulse}.", logging.ERROR)
            return False

        self.settings["MIN_PULSE"] = minPulse
        self.settings["MAX_PULSE"] = maxPulse

        self.Log(f"Modülün asgari ve azami sinyal darbe uzunluğu {minPulse} ve {maxPulse} olarak değiştirildi.", logging.INFO)
        return True

    # Sinyal değer aralığını ayarlar.
    def SetSignalRange(self, minSignal, maxSignal):
        self.settings["MIN_SIGNAL"] = minSignal
        self.settings["MAX_SIGNAL"] = maxSignal

        self.Log(f"Modül için sinyal limitleri {minSignal} ve {maxSignal} olarak değiştirildi.", logging.INFO)
        return True
        
    

    # Sinyal değeri emretmek için.
    def SetChannelSignal(self, channel, signal):
        if self.open:
            if channel < 0 or channel >= self.settings["CHANNEL_COUNT"]:
                self.Log(f"Verilen kanal numarası {channel}, modülün sahip olduğu kanal sayısından ya fazla ya da negatif!", logging.ERROR)
                return False
            if signal < self.settings["MIN_SIGNAL"] or signal > self.settings["MAX_SIGNAL"]:
                self.Log(f"Verilen sinyal değeri {signal}, asgari {self.settings['MIN_SIGNAL']} ve azami {self.settings['MAX_SIGNAL']} sinyal değerinin dışında!", logging.ERROR)
                return False
            
            # PWM için hesaplama
            minPulse = self.settings["MIN_PULSE"]
            maxPulse = self.settings["MAX_PULSE"]
            pulse = int(minPulse + (signal / (self.settings["MAX_SIGNAL"] - self.settings["MIN_SIGNAL"])) * (maxPulse - minPulse))

            on_time = 0
            off_time = pulse

            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_ON_L"] + 4 * channel, data=on_time & 0xFF)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_ON_H"] + 4 * channel, data=on_time >> 8)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_OFF_L"] + 4 * channel, data=off_time & 0xFF)
            self.I2CWriteByteData(address=self.address["SELF"], offset=self.address["LED0_OFF_H"] + 4 * channel, data=off_time >> 8)
            return True
        else:
            self.Log("Modüle kanal sinyal değişimi için emir geldi ancak modül açık değil!", logging.ERROR)
            return True

    # Tüm kanalların sinyallerini emreder.
    def SetAllChannelSignal(self, signal):
        if self.open:
            if signal < self.settings["MIN_SIGNAL"] or signal > self.settings["MAX_SIGNAL"]:
                self.Log(f"Verilen sinyal değeri {signal}, asgari {self.address['MIN_SIGNAL']} ve azami {self.settings['MAX_SIGNAL']} sinyal değerinin dışında!", logging.ERROR)
                return False

            for channel in range(self.settings["CHANNEL_COUNT"]):
                self.SetChannelSignal(channel, signal)
        else:
            self.Log("Modüle tüm kanalların sinyal değişimi için emir geldi ancak modül açık değil!", logging.ERROR)
            return False

