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

    #Function for getting coordinates from joystick
    def sendCoordinates(self, x, y):
        print("Send coordinates called")
        self.myspi.xfer2([x])
        #Distance comes on transmission of y
        distance = self.myspi.xfer2([y])
        #return distance
        return distance
