#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import serial

from classes.Base import Base

from services import responseService
from services import langService
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

        self.Initiate(**kwargs)

    def Initiate(self, **kwargs):
        responseService.Respond(
            text=lang.moduleResponses["UAV"]["INITIATE"],
            reason=responseService.reasons["INFO"],
            name=self.name)
        try:
            self.interface = Interface(uav=self, **kwargs)
            self.interface.Response(
                text=lang.moduleResponses["UAV"]["UAV_READY"],
                reason=responseService.reasons["SUCCESS"],
                name=self.name,
                responseLevel=self.responseLevel)
        except Exception as e:
            responseService.Respond(
                text=lang.moduleResponses["UAV"]["UAV_FAILED"],
                reason=responseService.reasons["FAIL"],
                name=self.name)
            raise e



class Interface(Base):
    def __init__(self, name=lang.names["INTERFACE"], **kwargs):
        super().__init__(**kwargs)

        self.name = name

        self.response = lang.moduleResponses["INTERFACE"] | self.response
        self.states = {
            "UART1_READY": False,
        } | self.states

        self.Initiate(**kwargs)
    
    def Initiate(self, **kwargs):
        responseService.Respond(
            text=lang.moduleResponses["INTERFACE"]["INITIATE"],
            reason=responseService.reasons["INFO"],
            name=self.name)

        self.uav = kwargs.get("uav", None)

        try:
            self.UART1 = kwargs.get("UART1", serial.Serial(
                port=kwargs.get("uart1Port", "/dev/ttyAMA0"),
                baudrate=kwargs.get("uart1Baudrate", 115200),
                timeout=kwargs.get("uart1Timeout", 1)
            ))
            self.states["UART1_READY"] = True
            responseService.Respond(
                text=lang.moduleResponses["INTERFACE"]["RESPONSE_SERVICE_READY"],
                reason=responseService.reasons["SUCCESS"],
                name=self.name)
            self.Response(
                text=lang.moduleResponses["INTERFACE"]["UART_READY"](f'UART1 - {self.UART1.portstr}'),
                reason=responseService.reasons["SUCCESS"],
                name=self.name,
                responseLevel=self.uav.responseLevel)
        except serial.SerialException as e:
            self.states["UART1_READY"] = False
            self.Response(
                text=lang.moduleResponses["INTERFACE"]["UART_FAILED"](f'UART1 - {self.UART1.portstr}'),
                reason=responseService.reasons["FAIL"],
                name=self.name,
                responseLevel=self.uav.responseLevel)
            raise e
    
    def Response(self, text=None, reason=None, name=None, padding=False, responseLevel=0):
        if reason is not None and reason["level"] <= responseLevel:
            response = responseService.Format(
                text=text,
                reason=reason,
                name=name,
                padding=padding
            )
            print(response)
            

