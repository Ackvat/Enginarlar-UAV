#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import datetime

from services import langService
lang = langService.GetLanguage('tr_tr')

########################################
#              DÖNÜTLER                #
########################################

colors = {
    "RESET": "\033[0m",        # Sıfırla
    "BOLD": "\033[1m",         # Kalın
    "UNDERLINE": "\033[4m",    # Altı çizili
    "REVERSE": "\033[7m",      # Ters renk

    "CONSOLE": "\033[0;37m",  # Gri
    "INFO": "\033[0;37m",     # Gri
    "ANSWER": "\033[0;37m",   # Gri
    "DEBUG": "\033[0;34m",    # Mavi
    "VERBOSE": "\033[0;36m",  # Camgöbeği
    "SUCCESS": "\033[0;32m",  # Yeşil
    "FAIL": "\033[0;31m",     # Kırmızı
    "WARN": "\033[0;33m",     # Sarı
    "ERROR": "\033[0;31m"     # Kırmızı
}

reasons = {
    "CONSOLE": {"reasonName": lang.responseReasons["CONSOLE"],
                "level": 4,
                "color": colors["CONSOLE"]},
    "INFO": {"reasonName": lang.responseReasons["INFO"],
             "level": 4,
             "color": colors["INFO"]},
    "ANSWER": {"reasonName": lang.responseReasons["ANSWER"],
              "level": 1,
              "color": colors["ANSWER"]},

    "DEBUG": {"reasonName": lang.responseReasons["DEBUG"],
              "level": 5,
              "color": colors["DEBUG"]},
    "VERBOSE": {"reasonName": lang.responseReasons["VERBOSE"],
                "level": 6,
                "color": colors["VERBOSE"]},
    
    "SUCCESS": {"reasonName": lang.responseReasons["SUCCESS"],
                "level": 4,
                "color": colors["SUCCESS"]},
    "FAIL": {"reasonName": f'{lang.responseReasons["FAIL"]}', 
             "level": 2,
             "color": colors["FAIL"]},
    
    "WARN": {"reasonName": f'{lang.responseReasons["WARN"]}',
             "level": 3,
             "color": colors["WARN"]},
    "ERROR": {"reasonName": f'{lang.responseReasons["ERROR"]}',
              "level": 1,
              "color": colors["ERROR"]}
}

########################################
#            FONKSİYONLAR              #
########################################

# H sınıf fonksiyon.
def Format(text=lang.strings["EMPTY"], reason=reasons["CONSOLE"], name=lang.strings["NONAME"], padding=False):
    if padding:
        pad = "\n"
    else:
        pad = ""

    return f'[{reason["color"]}{reason["reasonName"]}{colors["RESET"]}] [{name}] {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text} {pad}'

