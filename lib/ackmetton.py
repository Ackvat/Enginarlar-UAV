import os

from datetime import datetime
from colorama import Fore, Style

from dotenv import load_dotenv

load_dotenv()

class Ackmetton:
    def __init__(self, name=None, color="WHITE"):
        self.name = name
        self.color = self.GetColor(color=color)

    def GetColor(self, color="WHITE"):
        try:
            # Dynamically get the color attribute
            colorCode = getattr(Fore, color.upper(), Fore.RESET)  # Defaults to Fore.RESET if color is invalid
        except AttributeError:
            colorCode = Fore.RESET

        return colorCode

    def Print(self, text="PRINT", color="WHITE", padding=False):
        if padding: pad = "\n"
        else: pad = ""

        print(Style.BRIGHT + f'{"["}{Fore.WHITE + "CONSOLE"}{Fore.RESET + "] "}' + f'{"["}{self.color + self.name}{Fore.RESET + "] "}' + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + self.GetColor(color=color) + text + pad + Style.RESET_ALL)

    def Debug(self, text="DEBUG", color="WHITE", padding=False):
        if padding: pad = "\n"
        else: pad = ""
        
        if os.environ.get("DEBUG", "FALSE") == "TRUE": print(Style.BRIGHT + f'{"["}{Fore.GREEN + "DEBUG"}{Fore.RESET + "] "}' + f'{"["}{self.color + self.name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + self.GetColor(color=color) + text + pad + Style.RESET_ALL)

    def Verbose(self, text="VERBOSE", color="WHITE", padding=False):
        if padding: pad = "\n"
        else: pad = ""

        if os.environ.get("VERBOSE", "FALSE") == "TRUE": print(Style.BRIGHT + f'{"["}{Fore.BLUE + "VERBOSE"}{Fore.RESET + "] "}' + f'{"["}{self.color + self.name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + self.GetColor(color=color) + text + pad + Style.RESET_ALL)

    def Warn(self, text="WARN", color="YELLOW", padding=False):
        if padding: pad = "\n"
        else: pad = ""

        print(Style.BRIGHT + f'{"["}{Fore.YELLOW + "UYARI"}{Fore.RESET + "] "}' + f'{"["}{self.color + self.name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + self.GetColor(color=color) + text + pad + Style.RESET_ALL)

    def Error(self, text="ERROR", color="RED", padding=False):
        if padding: pad = "\n"
        else: pad = ""

        print(Style.BRIGHT + f'{"["}{Fore.RED + "HATA"}{Fore.RESET + "] "}' + f'{"["}{self.color + self.name}{Fore.RESET + "] "}' + Style.BRIGHT + f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' + Style.RESET_ALL + ' | ' + self.GetColor(color=color) + text + pad + Style.RESET_ALL)