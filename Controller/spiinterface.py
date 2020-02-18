import spidev #Spi library

class SpiInterface():
    def __init__(self):
        self.bus = 0;
        self.device = 0;
        self.myspi = spidev.SpiDev()
        self.myspi.open(self.bus, self.device)
        self.myspi.bits_per_word = 8
        self.myspi.max_speed_hz = 5000
        self.myspi.mode = 0

    def getCoordinates(self):
        x = self.myspi.xfer([0])
        y = self.myspi.xfer([0])
        #return tuble with x and y
        return x, y
