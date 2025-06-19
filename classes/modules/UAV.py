#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from classes.Base import Base

from services import langService
lang = langService.GetLanguage('tr_tr')

########################################
#              İHA SINIF               #
########################################

class UAV(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.name = kwargs.get('name', lang.strings['UAV'])
        self.responseLevel = kwargs.get('responseLevel', 0)

        self.response = lang.moduleResponses["UAV"] | self.response
        self.address = kwargs.get('address', {})
        self.byteData = kwargs.get('byteData', {})
        self.settings = kwargs.get('settings', {})

    def Initiate(self):
        pass