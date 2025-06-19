#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from services import langService
lang = langService.GetLanguage('tr_tr')

########################################
#             TABAN SINIF              #
########################################

class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', lang.strings['NONAME'])
        print(self.name)
        self.responseLevel = kwargs.get('responseLevel', 0)
        
        self.response = {} | kwargs.get('response', {})
        self.address = {} | kwargs.get('address', {})
        self.byteData = {} | kwargs.get('byteData', {})
        self.settings = {} | kwargs.get('settings', {})

