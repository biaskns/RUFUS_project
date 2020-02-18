import sys
import time
import threading
from threading import Event


import wificontroller

#make wificontroller
wificontroller = wificontroller.wificontroller()

#Main loop
while True:
    #Wait for a handshake, blocking
    wificontroller.handshaker()

    if wificontroller.connected == True:
        #Start thread for streaming video
        controlsThread = threading.Thread(target=wificontroller.getControls)
        streamThread = threading.Thread(target=wificontroller.sendStream)
        streamThread.start()
        controlsThread.start()

        while wificontroller.connected == True:
            time.sleep(0.5)

        #End thread for streaming video
        controlsThread.join()
        streamThread.join()
        wificontroller.cam.release()
