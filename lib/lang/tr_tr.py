#!/venv/bin/python3

########################################
#             KÜTÜPHANE                #
########################################

class LanguageLibrary:
    def __init__(self):
        self.langName = "Türkçe"

        self.strings = {
            "EMPTY": "Boş",
            "NONAME": "İsimsiz"
        }

        self.responseReasons = {
            "CONSOLE": "KONSOL",
            "INFO": "BİLGİ",
            "ANSWER": "YANIT",
            "DEBUG": "DEBUG",
            "VERBOSE": "VERBOSE",
            "SUCCESS": "BAŞARILI",
            "FAIL": "BAŞARISIZ",
            "WARN": "UYARI",
            "ERROR": "HATA"
        }

