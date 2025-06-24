#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import logging
from classes.Base import Base, UARTBase

########################################
#             ANAYORDAM                #
########################################

if __name__ == "__main__":
    UARTModule = UARTBase(name="UART Test Module", baudrate=9600)
    
    try:
        while True:
            UARTModule.Write("test")
            response = UARTModule.Read()
            if response:
                print("[DÖNÜT]: ", response)
                UARTModule.Log(f"Received: {response}", level=logging.INFO)
    except KeyboardInterrupt:
        UARTModule.Log("Exiting UART test module.", level=logging.INFO)
        UARTModule.Close()
