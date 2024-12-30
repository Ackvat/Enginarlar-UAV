import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
kit.address = 0x40
kit.frequency = 333

kit.servo[0].actuation_range = 180
kit.servo[0].set_pulse_width_range(500, 3500)

try:
    while True:
        kit.servo[0].angle = 0
        time.sleep(3)
        kit.servo[0].angle = 180
        time.sleep(3)
except KeyboardInterrupt:
    pass