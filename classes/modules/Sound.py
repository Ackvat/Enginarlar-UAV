#!/venv/bin/python3

########################################
#            BAĞLANTILAR               #
########################################

from classes.Base import Base

class Buzzer(Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.name = kwargs.get("name", "Buzzer")
        self.pin = kwargs.get("pin", 18)