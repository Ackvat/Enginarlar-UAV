#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import serial

from classes.Base import Base
from classes.modules.Radio import E22LoRa

from old.v2 import responseService
from old.v2 import langService
lang = langService.GetLanguage("tr_tr")

########################################
#              İHA SINIF               #
########################################

class UAV(Base):
    def __init__(self, name=lang.names["UAV"], **kwargs):
        super().__init__(**kwargs)
        
        self.name = name
        self.responseLevel = kwargs.get("responseLevel", 0)

        self.response = lang.moduleResponses["UAV"] | self.response

        # Henüz arayüz hazırlanmadığından, gömülü tepki işlevları kullanılıyor.
        print(responseService.Format(text=lang.moduleResponses["UAV"]["INITIATE"], reason=responseService.reasons["INFO"], name=self.name))
        try:
            self.interface = Interface(uav=self)
            self.transponder = E22LoRa(uav=self, interface=self.interface)

            self.interface.Response(text=lang.moduleResponses["UAV"]["READY"], reason=responseService.reasons["SUCCESS"], name=self.name)
        except Exception as e:
            # Eğer arayüz başlatılamazsa, yine gömülü tepki işlevinu kullan.
            print(responseService.Format(text=lang.moduleResponses["UAV"]["FAILED"], reason=responseService.reasons["FAIL"], name=self.name))
            raise e



class Interface(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = kwargs.get("name", lang.names["INTERFACE"])

        self.response = lang.moduleResponses["INTERFACE"] | self.response
    
        # Arayüz için en gerekli olan nesneler.
        self.uav = kwargs.get("uav", None)
        self.responseLevel = kwargs.get("responseLevel", self.uav.responseLevel if self.uav else 0)

        self.Response(text=lang.moduleResponses["INTERFACE"]["INITIATE"], reason=responseService.reasons["INFO"], name=self.name)

        try:
            # Yanıt servisi burada ilk kez test edilecek.
            self.Response(text=lang.moduleResponses["INTERFACE"]["RESPONSE_SERVICE_READY"], reason=responseService.reasons["SUCCESS"], name=self.name)
            
            # Portların ayarlanması.
            self.UART1 = kwargs.get("UART1", self.UART(interface=self, name="UART1", port="/dev/ttyAMA0"))
            self.states["UART1_READY"] = True
            
            self.Response(text=lang.moduleResponses["INTERFACE"]["UART_READY"](f'UART1 - {self.UART1.port.portstr}'), reason=responseService.reasons["SUCCESS"], name=self.name)
        except serial.SerialException as e:
            self.states["UART1_READY"] = False
            self.Response(text=lang.moduleResponses["INTERFACE"]["UART_FAILED"](f'UART1 - {self.UART1.port.portstr}'), reason=responseService.reasons["FAIL"], name=self.name)
            raise e
    
    class UART(Base):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            
            self.port = None
            self.status = False

            self.interface = kwargs.get("interface", None)

            try:
                if self.port is None:
                    self.port = serial.Serial(
                        port=kwargs.get("port", "/dev/ttyAMA0"),
                        baudrate=kwargs.get("baudrate", 115200),
                        timeout=kwargs.get("timeout", 1)
                        )
                self.status = True
                self.interface.Response(text=lang.moduleResponses["INTERFACE"]["UART_READY"](self.port.portstr), reason=responseService.reasons["SUCCESS"], name=self.name)
            except serial.SerialException as e:
                self.status = False
                self.interface.Response(text=lang.moduleResponses["INTERFACE"]["UART_FAILED"](self.port.portstr), reason=responseService.reasons["FAIL"], name=self.name)
                raise e
    
    # H sınıf işlev.
    # Konsol ve kayır yanıtları.
    def Response(self, text=None, reason=None, name=None, padding=False):
        if reason is not None and reason["level"] <= self.uav.responseLevel:
            response = responseService.Format(
                text=text,
                reason=reason,
                name=name,
                padding=padding
            )
            print(response)
            

