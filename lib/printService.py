from datetime import datetime
from colorama import Fore, Style

def GetColor(color="WHITE"):
    try:
        colorCode = getattr(Fore, color.upper(), Fore.RESET)
    except AttributeError:
        colorCode = Fore.RESET

    return colorCode

def Print(name = "", text="PRINT", color="WHITE", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{"["}{Fore.WHITE + "CONSOLE"}{Fore.RESET + "] "}' + f'{"["}{color + name}{Fore.RESET + "] "}' + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Debug(name = "", text="DEBUG", color="WHITE", padding=False):
    if padding: pad = "\n"
    else: pad = ""
    
    print(Style.BRIGHT + f'{"["}{Fore.GREEN + "DEBUG"}{Fore.RESET + "] "}' + f'{"["}{color + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Verbose(name = "", text="VERBOSE", color="WHITE", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{"["}{Fore.BLUE + "VERBOSE"}{Fore.RESET + "] "}' + f'{"["}{color + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Warn(name = "", text="WARN", color="YELLOW", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{"["}{Fore.YELLOW + "UYARI"}{Fore.RESET + "] "}' + f'{"["}{color + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Error(name = "", text="ERROR", color="RED", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{"["}{Fore.RED + "HATA"}{Fore.RESET + "] "}' + f'{"["}{color + name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)