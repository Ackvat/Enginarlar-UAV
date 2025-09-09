#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import os
import datetime
import json
import logging
from queue import Queue
from smbus2 import SMBus

import serial

########################################
#           TABAN SINIFLAR             #
########################################

class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "İSİMSİZ")

        self.debug = kwargs.get("debug", False)
        
        # Log nesnesi ve ayarları
        self.log = logging.getLogger(self.name)
        self.log.setLevel(logging.DEBUG)
        self.logHandler = None
        self.logVerboseName = True
        if not self.log.handlers:
            givenHandler = kwargs.get("logHandler", None)
            if givenHandler:
                self.log.addHandler(givenHandler)
            else:
                os.makedirs("logs", exist_ok=True)
                currentDate = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
                os.makedirs(f'logs/{currentDate}', exist_ok=True)
                logPath = f"logs/{currentDate}/{self.name.strip().lower()}.log"
                self.logHandler = logging.FileHandler(logPath, encoding="utf-8", mode="w")
                self.logHandler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('[%(levelname)s] [%(name)s] %(asctime)s | %(message)s')
                self.logHandler.setFormatter(formatter)
                self.log.addHandler(self.logHandler)


    
    # Tüm nesneler için loglama fonksiyonu
    def Log(self, message, level=logging.DEBUG):
        self.log.log(level, message)

    # Tüm nesneler için yazdırma fonksiyonu.
    def Print(self, message, level=logging.DEBUG):
        print(message)

        




class UARTBase(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # FIFO eylem sıralama nesnesi
        self.queue = Queue()

        self.ser = kwargs.get("serial", None)  # Seri arayüzü nesnesi
        self.port = kwargs.get("port", "/dev/ttyAMA0")
        self.baudrate = kwargs.get("baudrate", 9600)
        self.timeout = kwargs.get("timeout", 1)



    # Arayüzü başlatma
    def OpenSerial(self, **kwargs):
        self.Log("UART arayüzü başlatılıyor...", logging.INFO)
        if self.ser is None:
            self.Log("UART seri portu bulunamadı!", logging.WARNING)
            self.Log("UART seri portu başlatılıyor...", logging.INFO)
            try:
                # Varsayılan seri arayüzü
                self.ser = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                )
                self.ser.flushInput()  # Giriş tamponunu temizle
                self.Log("UART seri arayüzü başlatıldı.", logging.INFO)
                self.Log(f'Adres: {self.ser.port} | BR: {self.ser.baudrate}', logging.INFO)
                return True
            except Exception as e:
                self.Log(f"UART arayüzü başlatılırken bir hata oluştu! {e}", logging.ERROR)
                return False
        else:
            if not self.ser.is_open:
                try:
                    self.ser.open()
                    self.ser.flushInput()  # Giriş tamponunu temizle
                    self.Log("UART portu bulundu ve arayüz başlatıldı.", logging.INFO)
                    return True
                except serial.SerialException as e:
                    self.Log(f"UART portu bulundu ama başlatılırken bir hata oluştu! {e}", logging.ERROR)
                    return False
            else:
                self.Log("UART portu ve arayüzü zaten var ve açık!", logging.WARNING)
                return True
    
    # Arayüzü kapat
    def CloseSerial(self):
        self.Log("UART arayüzü kapatılıyor.", logging.INFO)
        self.Log(f'Adres: {self.ser.port} | BR: {self.ser.baudrate}', logging.INFO)
        if hasattr(self.ser, "is_open") and self.ser.is_open:
            try:
                self.ser.close()
                self.Log("UART arayüzü kapatıldı!", logging.INFO)
                return True
            except serial.SerialException as e:
                self.Log(f"UART arayüzü kapatılırken bir hata oluştur! {e}", logging.ERROR)
                return False
        else:
            self.Log("UART arayüzü zaten kapalı!", logging.WARNING)
            return True

    # Arayüz kanalını değiştirme fonksiyonu
    def ChangeSerial(self, **kwargs):
        self.Log("UART arayüzü değiştiriliyor...", logging.INFO)
        if self.CloseSerial():
            pass # TODO: Buraya adres değişimini ekle.
            
            

    # Veri gönderme
    def WriteToSerial(self, data, newLine=True):
        if newLine:
            data += '\n'
        self.ser.write(data.encode('utf-8'))
        return True
    
    # Veri okuma
    def ReadLine(self, size=1):
        data = self.ser.readline().decode('utf-8').strip()
        if data:
            return data
        else:
            return None

    # Bekleyen veriyi okuma
    def ReadAllInWaiting(self, size=1):
        #data = self.ser.read(self.ser.in_waiting)
        data = self.ser.read(size)
        if data:
            return data
        else:
            return None



class I2CBase(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # FIFO eylem sıralama nesnesi
        self.queue = Queue()

        self.i2c = SMBus(1)

        self.address = kwargs.get("address", {})
        self.settings = kwargs.get("settings", {})



    def CloseI2C(self):
        return True
    

    # I2C nesnesinin belirtilen adresten yalın ve tek veri okumasını sağlar.
    def I2CReadByte(self, address, offset):
        readData = self.i2c.read_byte_data(address, offset)
        if readData:
            return readData
        else:
            return None

    # I2C nesnesinin belirtilen adresten veri öbeği okumasını sağlar.
    def I2CReadBlockData(self, address, offset, length):
        readData = self.i2c.read_i2c_block_data(address, offset, length)
        if readData:
            return readData
        else:
            return None
    
    # I2C nesnesinin belirtilen adrese yalın ve tek veri yollamasını sağlar.
    def I2CWriteByte(self, address, data):
        self.i2c.write_byte(address, data)
        return True
        
    # I2C nesesinin belirtilen adrese veri öbeği yollamasını sağlar.
    def I2CWriteByteData(self, address, offset, data):
        self.i2c.write_byte_data(address, offset, data)
        return True

    # I2C nesnesinin belirtilen adrese veri grubu yollamasını sağlar.
    def I2CWriteBlockData(self, address, offset, data):
        # Örneğin: data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        self.i2c.write_i2c_block_data(address, offset, data)
        return True