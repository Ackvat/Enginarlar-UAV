
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

uav = uavlib.UAV()



########################################
#                TEST                  #
########################################

if os.environ.get("TEST", "FALSE") == "FALSE":
	try:
		while True:
			ack.Debug(f'Sistem döngüsü gerçekleştiriliyor...')
			time.sleep(1)
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
				if uav.imu.tempErrorCount > 0:
					tempErrorRatio = uav.imu.tempSuccessCount/uav.imu.tempErrorCount
					tempErrorRatioColor = "GREEN"
					if tempErrorRatio < 1: tempErrorRatioColor = "RED"
					ack.Debug(f'Sıcaklık hata ve başarı oranı: {tempErrorRatio:.2f}', color=tempErrorRatioColor)
				time.sleep(0.25)
		except KeyboardInterrupt:
			pass

