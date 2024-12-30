import os
import time

import lib.ackmetton as ack

from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)
kit.address = 0x40
kit.frequency = 333

kit.servo[0].actuation_range = 190
kit.servo[0].set_pulse_width_range(500, 2600)

Trial = True

if Trial == False:
    try:
        while True:
            kit.servo[0].angle = 0
            time.sleep(3)
            kit.servo[0].angle = 180
            time.sleep(3)
    except KeyboardInterrupt:
        pass
else:
    kit.servo[0].angle = 190
