from tkinter import *
from tkinter import ttk


class MyTk():

    def __init__(self):
        self.root = Tk()
        self.root.title('MyTk Root')

        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe['relief'] = 'raised'
        self.mainframe['borderwidth'] = 4
        self.mainframe.grid(sticky=(N, W, E, S))
        self.mainframe_label = Label(self.mainframe, text='MainFrame Label')
        self.mainframe_label.grid(sticky=(N, W, E, S))
        self.mainframe_label['borderwidth'] = 4

        self.ani_frame = ttk.Frame(self.mainframe, padding="3 3 12 12")
        self.ani_frame.grid(sticky=(N, W, E, S))
        self.ani_frame.columnconfigure(0, weight=1)
        self.ani_frame.rowconfigure(0, weight=1)
        self.ani_frame['relief'] = 'raised'
        self.ani_frame['borderwidth'] = 4
        self.ani_frame_label = Label(self.mainframe, text='AniFrame Label')
        self.ani_frame_label.grid(sticky=(N, W, E, S))
        self.ani_frame_label['borderwidth'] = 4

myTk = MyTk()
myTk.root.mainloop()
