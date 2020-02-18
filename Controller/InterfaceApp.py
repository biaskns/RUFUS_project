import tkinter as tk
from tkinter import font as tkfont
import wifiInterface
import PIL.Image, PIL.ImageTk

class InterfaceApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        #Tkinter configurations
        self.title_font = tkfont.Font(family='Consolas', size=15, weight="bold")
        self.info_font = tkfont.Font(family='Consolas', size=10, weight="bold")
        self.geometry("500x500")
        self.title('InterfaceApp')

        #Wifiinterface
        self.wifiinterface = wifiInterface.wifiInterface()

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for allframes in (AccessPoints, ConnectPage, Connected):
            page_name = allframes.__name__
            frame = allframes(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConnectPage")


    #Function to show a given tkinter page referenced by name
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class AccessPoints(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller=controller
        label = tk.Label(self, text="Select RUFUS' network to connect", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        label = tk.Label(self, text="Available Access points:", font=controller.info_font)
        label.pack(side="top", fill="x", pady=10)

        # List of AP's
        self.aplist = tk.Listbox(self, bg="#A0A0A0", width=30)

        self.aplist.pack(side="top")

        connectAPButton = tk.Button(self, text="Connect",
                            command=lambda: self.tryAP(controller))
        connectAPButton.pack(side="top")

        refreshButton = tk.Button(self, text="Refresh",
                            command=lambda: self.refreshAPS(controller))
        refreshButton.pack(side="top")

    def tryAP(self, controller):
        pass

    def refreshAPS(self, controller):


        self.aplist.insert(1, "Not implemented yet")

        controller.wifiinterface.getAPS()


#Class to handle connection
class ConnectPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Connect to RUFUS", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        label = tk.Label(self, text="Enter IP and port to connect:", font=controller.info_font)
        label.pack(side="top", fill="x", pady=10)

        backgroundColor = "#c0c0c0"
        self.configure(background=backgroundColor)

        #### entry stuff #####
        self.ip_v = tk.StringVar()
        self.port_v = tk.StringVar()

        IP_entry = tk.Entry(self, width=15, textvariable=self.ip_v)
        IP_entry.pack(side="top")
        self.ip_v.set("192.168.5.174")

        Port_entry = tk.Entry(self, width=10, textvariable=self.port_v)
        Port_entry.pack(side="top")
        self.port_v.set("10000")

        #### if button pressed, check for connection #####
        connectbutton = tk.Button(self, text="Connect",
                            command=lambda: controller.wifiinterface.CheckConnect(self.controller, self.ip_v, self.port_v))
        connectbutton.pack(side="bottom")



#Class to handle stream of data
class Connected(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
        	############# test med viktors kode ################
        	# Create label (area for showing video)
		self.VideoFeedLabel = tk.Label(self)
		self.VideoFeedLabel.pack()
       		# Add button Function
		def disconnect(parent, controller):
		      controller.wifiinterface.CloseConnection(controller)

		# Add Button
		disconnect_button = tk.Button(self, text="Disconnect", command=lambda: disconnect(parent,controller), bg="OrangeRed2", fg="white")

		disconnect_button.place(rely=0,relx=1,anchor=tk.NE)

		self.distance_var = tk.StringVar()
		self.distance_var.set("XXXXXXX")

		self.distance_label = tk.Label(self, textvariable=self.distance_var, font=("Helvetica", 12))
		self.distance_label.place(rely=0,relx=0,anchor=tk.NW)

	def display(self, frame_img):

		self.VideoFeedLabel.config(image=frame_img)
		self.VideoFeedLabel.image = frame_img
