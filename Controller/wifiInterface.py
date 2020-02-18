import socket
import threading
from threading import Event
import time
from tkinter import messagebox
import cv2
import struct
import pickle
import PIL.Image, PIL.ImageTk

#Import SpiInterface
import spiinterface

class wifiInterface():
    def __init__(self):
        #Variables for web-interfacing
        self.myIP = '192.168.5.1'
        self.clientIP = None
        self.clientPort = None
        self.client_address = None
        self.streamsock = None
        self.controlsock = None

        #Thread stop event
        self.stop_threads = Event()
        self.stop_threads.clear()

        #Spi device to communicate with PSoC
        self.myspidev = spiinterface.SpiInterface()

    #Helper and debugging function to get local address
    def get_ip(self):
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            mySocket.connect(('10.255.255.255', 1))
            IP = mySocket.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            mySocket.close()
        return IP

    #Function to get access points
    def getAPS(self):
        pass

    #Function to logically check the ip and port
    def CheckConnect(self, app, ip, port):
        print(ip.get())
        print(port.get())

        try:
            socket.inet_aton(ip.get())
        except socket.error:
            messagebox.showerror("Error", "Invalid IP")
            return

        if port.get().isdigit():
            self.clientIP = ip.get()
            self.clientPort = port.get()
            self.TryConnect(app)
        else:
            messagebox.showerror("Error", "Invalid port")

    #Function to check if given address is RUFUS by transmitting
    #message "RUFUS" and listen for an echo
    def TryConnect(self, app):
        #Message to check if RUFUS
        message = "RUFUS"
        self.client_address = (self.clientIP, int(self.clientPort))
        print(self.client_address)
        # Setting up udp socket
        self.controlsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.controlsock.settimeout(3)

        #Send message and wait for response
        try:
            self.controlsock.sendto(message.encode(), self.client_address)
        except:
            messagebox.showerror("Error", "Connection failed with invalid ip")
            app.show_frame("ConnectPage")
            return

        try:
            data, response_address = self.controlsock.recvfrom(128)
        except:
            messagebox.showerror("Error", "Connection failed with a timeout")
            app.show_frame("ConnectPage")
            return
        #Print data recieved
        print(data.decode())
        #Start a thread for streaming and controls and clear stop threads event
        app.show_frame("Connected")
        self.controlThreadinit(app)
        self.streamThreadinit(app)

    #Thread for streaming video
    def streamThreadinit(self, app):
        #Program to be executed in the thread
        def GetStream():

            self.streamsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.streamsock.bind((self.myIP, 8000))
            self.streamsock.listen(10)
            print('Socket now listening')

            print('Accepting connection')
            connection, addr = self.streamsock.accept()
            print('Connection accepted')
            data = b""
            payload_size = struct.calcsize(">L")
            print("payload_size: {}".format(payload_size))

            while not self.stop_threads.is_set():
                while len(data) < payload_size:
                    #print("Recv: {}".format(len(data)))
                    data += connection.recv(4096)

                #print("Done Recv: {}".format(len(data)))
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack(">L", packed_msg_size)[0]
                #print("msg_size: {}".format(msg_size))
                while len(data) < msg_size:
                    data += connection.recv(4096)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
                frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                #Convert to image
                frame_img = PIL.Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
                #frame_resized = frame_img.resize((480,360), PIL.Image.NEAREST)
                frame = PIL.ImageTk.PhotoImage(frame_img)
                # Add a PhotoImage to the Canvas with display
                app.frames["Connected"].display(frame)


        #Start a thread running GetStream()
        self.stop_threads.clear()
        self.streamThread = threading.Thread(target=GetStream)
        self.streamThread.start()

    #Thread for streaming controls
    def controlThreadinit(self, app):
        def SendControls():
            #Adjust timeout on socket
            self.controlsock.settimeout(1)
            #time.sleep(1)
            #Keep sending controls untill thread is stopped
            while not self.stop_threads.is_set():

                #Message to confirm
                ack = "ack"
                nack = "nack"

                #Get coordinates from PSoC controller
                x, y = self.myspidev.getCoordinates()

                #Convert to string, eperate with "," and split
                controls = str(x) + "," + str(y)
                controls.split(",")

                try:
                    #Transmit controls
                    print("Transmitting controls to " + str(self.client_address))
                    self.controlsock.sendto(controls.encode(), self.client_address)
                    #Recieve to check if correct
                    print("Wating for controls response")
                    reply, response_address = self.controlsock.recvfrom(128)
                    #Check if client recieved correct controls
                    if reply.decode() == controls:
                        self.controlsock.sendto(ack.encode(), self.client_address)
                    else:
                        self.controlsock.sendto(nack.encode(), self.client_address)

                    distance, response_address = self.controlsock.recvfrom(128)
                    print("Distance is: " + str(distance.decode()))
                    app.frames["Connected"].distance_var.set(distance.decode())

                except:
                    pass
                #    print("controlsock trans failed, trying again")

                time.sleep(0.1)
                print("Send controls:" + controls + "\n")

        #Start a thread running SendControls()
        self.stop_threads.clear()
        self.controlsThread = threading.Thread(target=SendControls)
        self.controlsThread.start()

    #Function for closing connection and closing
    def CloseConnection(self, app):
        print("CloseConnection called")
        self.streamsock.close()
        self.controlsock.close()
        self.stopThreads()
        app.show_frame("ConnectPage")

    def stopThreads(self):
        print("stopThreads called")
        self.stop_threads.set()
        self.streamThread.join()
        self.controlsThread.join()
