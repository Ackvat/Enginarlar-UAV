#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

import time

########################################
#              SINIFLAR                #
########################################

class TimeStamper():
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.unitMask = kwargs.get("unitMask", 1000.0)

        self.start = 0
        self.end = 0

        self.Start()
        self.End()
    
    def Start(self):
        self.start = time.time()*self.unitMask

    def End(self):
        self.end = time.time()*self.unitMask

    def GetDelta(self):
        self.End()
        return self.end - self.start

