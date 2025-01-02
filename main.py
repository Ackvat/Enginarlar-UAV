import os
import time

from dotenv import load_dotenv

import lib.ackmetton as ack

load_dotenv()
os.environ["DEBUG"] = "TRUE"
os.environ["TEST"] = "TRUE"

if os.environ.get("TEST", "FALSE") == "FALSE":
    try:
        ack.Debug("Döngü testi yapılıyor.")
        while True:
            kit.servo[0].angle = 0
            time.sleep(3)
            kit.servo[0].angle = 190
            time.sleep(3)
    except KeyboardInterrupt:
        pass
else:
    ack.Debug("Tek açı testi yapılıyor.")
    kit.servo[0].angle = 190
