#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import datetime

########################################
#              DÖNÜTLER                #
########################################

reasons = {
    "CONSOLE": {"reasonName": "KONSOL",
                "level": 4},
    "INFO": {"reasonName": "BİLGİ",
             "level": 4},
    "ANSWER": {"reasonName": "YANIT",
              "level": 1},

    "DEBUG": {"reasonName": "DEBUG",
              "level": 5},
    "VERBOSE": {"reasonName": "VERBOSE",
                "level": 6},
    
    "SUCCESS": {"reasonName": "BAŞARILI",
                "level": 4},
    "FAIL": {"reasonName": "**BAŞARISIZ**", 
             "level": 2},
    
    "WARN": {"reasonName": "*UYARI*",
             "level": 3},
    "ERROR": {"reasonName": "***HATA***", 
              "level": 1}
}

########################################
#            FONKSİYONLAR              #
########################################

def Format(text="", reason=reasons["CONSOLE"], name="", padding=False):
    if padding:
        pad = "\n"
    else:
        pad = ""

    return f'[{reason["reasonName"]}] [{name}] {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text} {pad}'