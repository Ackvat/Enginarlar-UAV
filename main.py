
########################################
#            BAĞLANTILAR               #
########################################

import os
import time
import argparse

from dotenv import load_dotenv

import lib.ackmetton as acklib

import lib.uav as uavlib

devName = "MAIN"
parser = argparse.ArgumentParser(description="Ana İHA sistem programı.")
ack = acklib.Ackmetton(name=devName, color="BLUE")

load_dotenv()
os.environ["DEBUG"] = "TRUE"
os.environ["VERBOSE"] = "TRUE"
os.environ["TEST"] = "TRUE"

testType = 1



########################################
#             BAŞLANGIÇ                #
########################################

ack.Debug(f'ENGİNARLAR İHA ana programı başlatılıyor...', color="CYAN")

uav = uavlib.UAV(freq=5)



########################################
#                TEST                  #
########################################

if os.environ.get("TEST", "FALSE") == "FALSE":
	try:
		while True:
			ack.Debug(f'Sistem döngüsü gerçekleştiriliyor...')
			time.sleep(uav.systemPeriod)
	except KeyboardInterrupt:
		pass
else:
	ack.Warn(f'Test modu aktif. Test tipi: {testType}')
	if testType == 0:
		# Motor testleri gelicek buraya.
		ack.Debug("Motor testi.")
	elif testType == 1:
		try:
			while True:
				uav.imu.GetGravity()
				uav.imu.GetEuler()
				uav.imu.GetTemperature()

				uav.imu.GetError()
				time.sleep(uav.systemPeriod)
		except KeyboardInterrupt:
			pass

