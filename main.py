#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import RPi.GPIO as GPIO
import time

from classes.modules.UAV import UAV

########################################
#             ANAYORDAM                #
########################################

if __name__ == "__main__":
    uav = UAV(name="Test UAV", responseLevel=6)
    
    uav.interface.UART1.close()

    
    BUZZER_PIN = 18  # GPIO pin for buzzer
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    pwm = GPIO.PWM(BUZZER_PIN, 1000)  # freq in Hz
    pwm.start(50)  # 50% duty cycle (can be lower if too loud)
    time.sleep(1)
    pwm.ChangeFrequency(2000)  # 2kHz
    time.sleep(0.5)

    # Stop it
    pwm.stop()
    GPIO.cleanup()
