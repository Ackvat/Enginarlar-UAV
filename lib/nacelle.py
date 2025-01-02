import os
from dotenv import load_dotenv

from adafruit_servokit import ServoKit

import ackmetton as ack

load_dotenv()

def LoadNacelleServoDriver(adress=0x40, channels=16, freq=333, actuationRange=190, pwRange=[500, 2600]):
    kit = ServoKit(channels=16)
    kit.address = 0x40
    kit.frequency = 333

    kit.servo[0].actuation_range = 190
    kit.servo[0].set_pulse_width_range(500, 2600)