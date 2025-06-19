#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from services import responseService
from services import langService
lang = langService.GetLanguage('tr_tr')

from classes.Base import Base

########################################
#            E22LoRa SINIF             #
########################################

class E22LoRa(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.name = kwargs.get('name', 'E22LoRa')
        self.responseLevel = kwargs.get('responseLevel', 0)

        self.response = lang.moduleResponses["E22LoRa"] | self.response

    def Initiate(self):
        pass

