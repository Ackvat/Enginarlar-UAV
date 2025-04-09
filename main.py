#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import lib.responseService as responseService

from lib.UAV import UAV

########################################
#              ANAYORDAM               #
########################################

if __name__ == "__main__":
	uav = UAV()
	uav.responseLevel = 5

	try:
		while True:
			uav.mainCycle()
	except KeyboardInterrupt:
		uav.bodyIMU.SuspendSensor()
		uav.i2c.close()
