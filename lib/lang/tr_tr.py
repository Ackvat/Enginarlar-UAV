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

        self.names = {
            "UAV": "İHA",
            "INTERFACE": "Arayüz",
            "E22LORA": "E22LoRa",
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

        self.moduleResponses = {
            "UAV": {
                "INITIATE": "İHA anamodülü başlatılıyor...",

                "READY": "İHA hazır.",
                "FAILED": "İHA hazırlanamadı.",
            },
            "INTERFACE": {
                "INITIATE": "Arayüz başlatılıyor...",

                "RESPONSE_SERVICE_READY": "Yanıt servisi hazır.",

                "UART_READY": lambda port: f"{port} arayüzü hazır.",
                "UART_FAILED": lambda port: f"{port} arayüzü başlatılamadı.",
            },
            "E22LORA": {
                "INITIATE": "E22LoRa modülü başlatılıyor...",

                "READY": "E22LoRa modülü hazır.",
                "FAILED": "E22LoRa modülü başlatılamadı.",
                "NO_INTERFACE": "E22LoRa modülü için arayüz bulunamadı.",
            }
        }

