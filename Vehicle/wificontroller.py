import socket
import cv2
import io
import struct
import pickle
import time
import spiinterface

class wificontroller():
    def __init__(self):
        # Create a UDP socket for handskake and stream of controls
        self.controlsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # TCP socket for streaming video
        self.streamsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        #self.server_address = (socket.gethostbyname(socket.gethostname()), 10000)
        #print(self.server_address[0])
        #print(self.server_address[1])
        self.controlsock.bind(('192.168.5.174', 10000))
        self.connected = False;
        self.client_address = ('192.168.5.1', 10000)
        self.stream_address = ('192.168.5.1', 8000)
        #Spi object to communicate with PSoC
        self.myspidev = spiinterface.SpiInterface()

    #Function to establish right connection
    def handshaker(self):
        print('Awaiting connection')
        #Blocking recieve, wait for data
        self.controlsock.settimeout(None)
        data, address = self.controlsock.recvfrom(128)

        print(data)

        if(data.decode() == 'RUFUS'):
            sent = self.controlsock.sendto(data, address)
            self.client_address = address
            self.connected = True

        print('Recieved bytes:')
        print(len(data))
        print('From:')
        print(address)

    #Function to get controls
    def getControls(self):
        print("Hello from getControls")
        #Recieve controls but dont wait for more than 3 second
        self.controlsock.settimeout(3)
        while self.connected == True:
            try:
                print("Awating controls")
                controls, client = self.controlsock.recvfrom(128)
                print("Controls recieved" + controls.decode())
                print("From: " + str(client))
                #Echo back controls to see if correct
                print("Trying to echo back to: " + str(self.client_address))
                self.controlsock.sendto(controls, self.client_address)
                #Recieve ack or nack
                state, client = self.controlsock.recvfrom(128)
                if state.decode() == "ack":
                    print("Controls recieved:" + controls.decode())
                    xy = controls.decode()
                    x, y = xy.split(",")
                    print("x: " + x + " y: " + y)
                    self.myspidev.sendCoordinates(x, y)
                else:
                    print("Controls transmission failed")
            except:
                print("Get controls threw exception")
                self.connected = False

    def sendStream(self):
        print("Hello from sendStream")
        #Wait for controller to get ready
        time.sleep(1)
        #Setup connection and file-like object from connection
        self.streamsock.connect(self.stream_address)
        connection = self.streamsock.makefile('wb')

        #Setup camera
        self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 800);
        self.cam.set(4, 480);
        img_counter = 0
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        while True:
            ret, frame = self.cam.read()
            result, frame = cv2.imencode('.jpg', frame, encode_param)
            data = pickle.dumps(frame, 0)
            size = len(data)

            #print("{}: {}".format(img_counter, size))
            self.streamsock.sendall(struct.pack(">L", size) + data)
            img_counter += 1
