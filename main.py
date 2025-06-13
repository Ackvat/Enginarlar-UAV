#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from lib.UAV import UAV

########################################
#              ANAYORDAM               #
########################################

if __name__ == "__main__":
	uav = UAV()
	uav.responseLevel = 0

	print(uav.extended.Read())

	try:
		while True:
			uav.mainCycle()
	except KeyboardInterrupt:
		uav.bodyIMU.SuspendSensor()
		uav.receiver.Close()
		uav.i2c.close()
