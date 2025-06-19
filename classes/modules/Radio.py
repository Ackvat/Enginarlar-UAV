#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from services import responseService
from services import langService
lang = langService.GetLanguage("tr_tr")

from classes.Base import Base

########################################
#            E22LoRa SINIF             #
########################################

class E22LoRa(Base):
    def __init__(self, name=lang.names["E22LORA"], **kwargs):
        super().__init__(**kwargs)
        
        self.name = name

        self.response = lang.moduleResponses["E22LORA"] | self.response

    def Initiate(self):
        pass

