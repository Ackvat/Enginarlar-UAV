#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################


########################################
#             TABAN SINIF              #
########################################

class Base:
    def __init__(self):
        self.responseLevel = 0
        

    def mainCycle(self):
        raise NotImplementedError("This method should be overridden in subclasses.")
    
    def close(self):
        if self.bodyIMU:
            self.bodyIMU.SuspendSensor()
        if self.receiver:
            self.receiver.Close()
        if self.i2c:
            self.i2c.close()