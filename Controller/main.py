
print("Importing libraries")

import sys
import numpy
import string
import cv2
import pickle
import threading
from threading import Event

import InterfaceApp
import wifiInterface

#Main app, GUI-controller
app = InterfaceApp.InterfaceApp()
#app.attributes("-fullscreen", True)

print("Done importing, program starting")

def main():
    app.attributes("-fullscreen", True)
    app.bind("<Escape>", close)
    app.mainloop()

# Event on escape to close program
def close(event):
    try:
        app.Wifiinterface.CloseConnection(app)
        sys.exit()
    except:
        sys.exit()

if __name__ == "__main__":
    main()
