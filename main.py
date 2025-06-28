#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import time
import logging
from classes.Base import Base, UARTBase
from classes.Radio import E22LoRa

########################################
#             ANAYORDAM                #
########################################

if __name__ == "__main__":
    Transponder = E22LoRa(name="Transponder", port="/dev/ttyAMA0", baudrate=9600)
    Transponder.StartReading()

    try:
        while True:
            receivedMessage = Transponder.GetMessage()
            if receivedMessage:
                print(receivedMessage)
            time.sleep(0.01)
    except KeyboardInterrupt:
        Transponder.CloseModule()
