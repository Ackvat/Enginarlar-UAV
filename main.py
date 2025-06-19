#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from classes.modules.UAV import UAV

########################################
#             ANAYORDAM                #
########################################

if __name__ == "__main__":
    uav = UAV(name="Test UAV", responseLevel=6)
    
    uav.interface.UART1.close()
