#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from old.v2 import responseService
from old.v2 import langService
lang = langService.GetLanguage("tr_tr")

from classes.Base import Base

########################################
#            E22LoRa SINIF             #
########################################

class E22LoRa(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.name = kwargs.get("name", lang.names["E22LORA"])

        self.response = lang.moduleResponses["E22LORA"] | self.response
        
        self.paired = False

        # Birim başalıtması için en gerekli olan nesneler.
        self.uav = kwargs.get("uav", None)
        self.interface = self.uav.interface if self.uav else None

        if self.interface is None:
            raise responseService.Format(
                text=lang.moduleResponses["E22LORA"]["NO_INTERFACE"],
                reason=responseService.reasons["FAIL"],
                name=self.name)
        else:
            self.interface.Response(
                text=lang.moduleResponses["E22LORA"]["INITIATE"],
                reason=responseService.reasons["INFO"],
                name=self.name)
            try:
                # LoRa Biriminün ayarlamaları.
                self.port = kwargs.get("port", self.interface.UART1)

                self.interface.Response(
                text=lang.moduleResponses["E22LORA"]["READY"],
                reason=responseService.reasons["SUCCESS"],
                name=self.name)
            except Exception as e:
                self.interface.Response(
                    text=lang.moduleResponses["E22LORA"]["FAILED"],
                    reason=responseService.reasons["FAIL"],
                    name=self.name)
                raise e

    # H sınıf işlev.
    # LoRa Biriminün FIFO kuyruklu veri gönderme işlevi.
    def Send(self, data):
        pass

