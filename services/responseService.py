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

reasons = {
    "CONSOLE": {"reasonName": lang.responseReasons["CONSOLE"],
                "level": 4},
    "INFO": {"reasonName": lang.responseReasons["INFO"],
             "level": 4},
    "ANSWER": {"reasonName": lang.responseReasons["ANSWER"],
              "level": 1},

    "DEBUG": {"reasonName": lang.responseReasons["DEBUG"],
              "level": 5},
    "VERBOSE": {"reasonName": lang.responseReasons["VERBOSE"],
                "level": 6},
    
    "SUCCESS": {"reasonName": lang.responseReasons["SUCCESS"],
                "level": 4},
    "FAIL": {"reasonName": f'**{lang.responseReasons["FAIL"]}**', 
             "level": 2},
    
    "WARN": {"reasonName": f'*{lang.responseReasons["WARN"]}*',
             "level": 3},
    "ERROR": {"reasonName": f'***{lang.responseReasons["ERROR"]}***',
              "level": 1}
}

########################################
#            FONKSİYONLAR              #
########################################

def Format(text=lang.strings["EMPTY"], reason=reasons["CONSOLE"], name=lang.strings["NONAME"], padding=False):
    if padding:
        pad = "\n"
    else:
        pad = ""

    return f'[{reason["reasonName"]}] [{name}] {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text} {pad}'