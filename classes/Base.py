#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from services import langService
lang = langService.GetLanguage("tr_tr")

########################################
#             TABAN SINIF              #
########################################

class Base:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", lang.strings["NONAME"])
        
        self.responseLevel = kwargs.get("responseLevel", 0)
        
        self.response = {} | kwargs.get("response", {})
        self.address = {} | kwargs.get("address", {})
        self.byteData = {} | kwargs.get("byteData", {})
        self.states = {} | kwargs.get("states", {})
        self.settings = {} | kwargs.get("settings", {})

    # Fonksiyon sınıfları:
    # B: Başlangıç, yüksek derinlikli değişkenleri ve argümanları destekler.
    # H: Hızlı, derinlik gerek değişkenler gerek argümanlar için desteklenmez.
    # N: Normal, duruma göre değişkenlik gösterebilir.
