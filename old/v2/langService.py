#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################



########################################
#            FONKSİYONLAR              #
########################################

def GetLanguage(langName):
    try:
        langLib = __import__(f'lib.lang.{langName}', fromlist=['LanguageLibrary'])
        return getattr(langLib, 'LanguageLibrary')()
    except ImportError:
        print(f"Language '{langName}' not found, falling back to default 'tr_tr'.")
        try:
            langLib = __import__(f'lib.lang.tr_tr', fromlist=['LanguageLibrary'])
            return getattr(langLib, 'LanguageLibrary')()
        except ImportError:
            raise ImportError(f"Language '{langName}' not found and default language 'tr_tr' also not found.")