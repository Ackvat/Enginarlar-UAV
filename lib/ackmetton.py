import os

from datetime import datetime
from colorama import Fore, Style

from dotenv import load_dotenv

load_dotenv()

def GetColor(color="WHITE"):
    try:
        # Dynamically get the color attribute
        colorCode = getattr(Fore, color.upper(), Fore.RESET)  # Defaults to Fore.RESET if color is invalid
    except AttributeError:
        colorCode = Fore.RESET

    return colorCode

def Print(text="PRINT", color="WHITE", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Debug(text="DEBUG", color="WHITE", padding=False):
    if padding: pad = "\n"
    else: pad = ""
    
    if os.environ.get("DEBUG", "FALSE") == "TRUE": print(Style.BRIGHT + f'{"["}{Fore.GREEN + "DEBUG"}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Verbose(text="VERBOSE", color="WHITE", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    if os.environ.get("VERBOSE", "FALSE") == "TRUE": print(Style.BRIGHT + f'{"["}{Fore.BLUE + "VERBOSE"}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Warn(text="WARN", color="YELLOW", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{"["}{Fore.YELLOW + "UYARI"}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)

def Error(text="ERROR", color="RED", padding=False):
    if padding: pad = "\n"
    else: pad = ""

    print(Style.BRIGHT + f'{"["}{Fore.RED + "HATA"}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + GetColor(color=color) + text + pad + Style.RESET_ALL)