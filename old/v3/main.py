#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import time
import logging
from classes.UAV import UAV

########################################
#             ANAYORDAM                #
########################################

uav = UAV(name="İHA")

def Main():
    uav.Run()

if __name__ == "__main__":
    Main()
    
