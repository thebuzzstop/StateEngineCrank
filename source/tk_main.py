from tkinter import *
from tkinter import ttk


class MyTk():

    def __init__(self):
        self.root = Tk()
        self.root.title('MyTk Root')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ------------------------------------------------
        # main frame - lives inside TkRoot
        # row 0: mainframe label
        self.mainframe = ttk.Frame(self.root, padding="10 10 10 10")
        self.mainframe.grid(row=1, column=0, sticky=(N, W, E, S))
        self.mainframe.grid_rowconfigure(1, weight=1)
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe['borderwidth'] = 4
        self.mainframe['relief'] = 'raised'

        self.mainframe_label = Label(self.mainframe, text='MainFrame Label')
        self.mainframe_label.grid(row=0, column=0, sticky=(N, W, E, S))
        self.mainframe_label.grid_rowconfigure(0, weight=1)
        self.mainframe_label.grid_columnconfigure(0, weight=1)
        self.mainframe_label['borderwidth'] = 4
        self.mainframe_label['relief'] = 'sunken'

        # -----------------------------------------------
        # animation frame - lives inside mainframe
        # row 0: label
        # row 1: console
        self.ani_frame = ttk.Frame(self.mainframe, padding="10 10 10 10")
        self.ani_frame.grid(row=1, column=0, sticky=(N, W, E, S))
        self.ani_frame.grid_rowconfigure(1, weight=1)
        self.ani_frame.grid_columnconfigure(0, weight=1)
        self.ani_frame['borderwidth'] = 4
        self.ani_frame['relief'] = 'raised'

        self.ani_frame_label = Label(self.ani_frame, text='AniFrame Label')
        self.ani_frame_label.grid(row=0, column=0, sticky=(N, W, E, S))
        self.ani_frame_label['borderwidth'] = 4
        self.ani_frame_label['relief'] = 'sunken'

        self.ani_console = Text(self.ani_frame, name='ani_console')
        self.ani_console.grid(row=1, column=0, sticky=(N, W, E, S))
        self.ani_console.grid_rowconfigure(1, weight=1)
        self.ani_console.grid_columnconfigure(0, weight=1)
        self.ani_console['relief'] = 'raised'


myTk = MyTk()
myTk.root.mainloop()
