#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import json

########################################
#            FONKSİYONLAR              #
########################################

def MergeJSON(base, override):
    merged = base.copy()
    for response, lang in override.items():
        if response not in merged:
            merged[response] = {}
        merged[response].update(lang)
    return merged