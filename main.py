
########################################
#            BAĞLANTILAR               #
########################################

import lib.printService as printService

devName = "MAIN"

testType = 1

########################################
#             BAŞLANGIÇ                #
########################################

printService.Debug(f'ENGİNARLAR İHA ana sistem yordamı başlatılıyor...', color="CYAN")
# Sistem ana unsurlarını burada başlatıyoruz.

########################################
#                ANAYORDAM             #
########################################

if __name__ == "__main__":
	try:
		while True:
			pass
	except KeyboardInterrupt:
		printService.Warn(f'ENGİNARLAR İHA ana sistem yordamı durduruluyor...')
