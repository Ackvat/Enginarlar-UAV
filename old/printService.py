from datetime import datetime
from colorama import Fore, Style

def GetColor(color="WHITE"):
    try:
        colorCode = getattr(Fore, color.upper(), Fore.RESET)
    except AttributeError:
        colorCode = Fore.RESET

    return colorCode

def Print(text="PRINT", textColor="WHITE", name = "", nameColor = "WHITE", colored=False, padding=False):
    if padding: pad = "\n"
    else: pad = ""

    if colored:
        print(Style.BRIGHT + f'{"["}{Fore.WHITE + "CONSOLE"}{Fore.RESET + "] "}' + f'{"["}{GetColor(color=nameColor) + name}{Fore.RESET + "] "}' + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=textColor) + text + pad + Style.RESET_ALL)
    else:
        print(f'[CONSOLE] [{name}] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text}' + pad)

def Debug(text="DEBUG", textColor="WHITE", name = "", nameColor = "WHITE", colored=False, padding=False):
    if padding: pad = "\n"
    else: pad = ""
    
    if colored:
        print(Style.BRIGHT + f'{"["}{Fore.GREEN + "DEBUG"}{Fore.RESET + "] "}' + f'{"["}{GetColor(color=nameColor) + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=textColor) + text + pad + Style.RESET_ALL)
    else:
        print(f'[DEBUG] [{name}] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text}' + pad)

def Verbose(text="VERBOSE", textColor="WHITE", name = "", nameColor = "WHITE", colored= False, padding=False):
    if padding: pad = "\n"
    else: pad = ""

    if colored:
        print(Style.BRIGHT + f'{"["}{Fore.BLUE + "VERBOSE"}{Fore.RESET + "] "}' + f'{"["}{GetColor(color=nameColor) + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=textColor) + text + pad + Style.RESET_ALL)
    else:
        print(f'[VERBOSE] [{name}] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text}' + pad)

def Warn(text="WARN", textColor="YELLOW", name = "", nameColor = "WHITE", colored=False, padding=False):
    if padding: pad = "\n"
    else: pad = ""

    if colored:
        print(Style.BRIGHT + f'{"["}{Fore.YELLOW + "UYARI"}{Fore.RESET + "] "}' + f'{"["}{GetColor(color=nameColor) + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=textColor) + text + pad + Style.RESET_ALL)
    else:
        print(f'[WARN] [{name}] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text}' + pad)

def Error(text="ERROR", textColor="RED", name = "", nameColor = "WHITE", colored=False, padding=False):
    if padding: pad = "\n"
    else: pad = ""

    if colored:
        print(Style.BRIGHT + f'{"["}{Fore.RED + "HATA"}{Fore.RESET + "] "}' + f'{"["}{GetColor(color=nameColor) + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=textColor) + text + pad + Style.RESET_ALL)
    else:
        print(f'[ERROR] [{name}] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | {text}' + pad)


