import os
import time

from dotenv import load_dotenv

from adafruit_servokit import ServoKit

import lib.ackmetton as ack

load_dotenv()

kit = ServoKit(channels=16)
kit.address = 0x40
kit.frequency = 333

kit.servo[0].actuation_range = 190
kit.servo[0].set_pulse_width_range(500, 2600)
print(os.environ.get("DEBUG", "FALSE"))
Test = os.environ.get("TEST", "FALSE")

if Test == "FALSE":
    try:
        ack.Debug("Döngü testi yapılıyor.")
        while True:
            kit.servo[0].angle = 0
            time.sleep(3)
            kit.servo[0].angle = 180
            time.sleep(3)
    except KeyboardInterrupt:
        pass
else:
    ack.Debug("Tek açı testi yapılıyor.")
    kit.servo[0].angle = 190
