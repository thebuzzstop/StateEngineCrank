from tkinter import *
from tkinter import ttk


class MyTk():

    def draw_mainframe(self, column):
        # ------------------------------------------------
        # main frame - lives inside TkRoot
        # row 0: mainframe label
        mainframe = ttk.Frame(self.root, padding="10 10 10 10",
                              name='mainframe%s' % column)
        mainframe.grid(row=0, column=column, sticky=(N, W, E, S))
        mainframe.grid_rowconfigure(1, weight=1)
        mainframe.grid_columnconfigure(column, weight=1)
        mainframe['borderwidth'] = 4
        mainframe['relief'] = 'raised'

        mainframe_label = Label(mainframe, text='MainFrame Label',
                                name='mainframe_label%s' % column)
        mainframe_label.grid(row=0, column=column, sticky=(N, W, E, S))
        mainframe_label.grid_rowconfigure(0, weight=1)
        mainframe_label.grid_columnconfigure(column, weight=1)
        mainframe_label['borderwidth'] = 4
        mainframe_label['relief'] = 'sunken'

        # -----------------------------------------------
        # animation frame - lives inside mainframe
        # row 0: label
        # row 1: console
        ani_frame = ttk.Frame(mainframe, padding="10 10 10 10",
                              name='ani_frame%s' % column)
        ani_frame.grid(row=1, column=column, sticky=(N, W, E, S))
        ani_frame.grid_rowconfigure(1, weight=1)
        ani_frame.grid_columnconfigure(column, weight=1)
        ani_frame['borderwidth'] = 4
        ani_frame['relief'] = 'raised'

        ani_frame_label = Label(ani_frame, text='AniFrame Label',
                                name='ani_frame_label%s' % column)
        ani_frame_label.grid(row=0, column=column, sticky=(N, W, E, S))
        ani_frame_label['borderwidth'] = 4
        ani_frame_label['relief'] = 'sunken'

        ani_console = Text(ani_frame, name='ani_console%s' % column)
        ani_console.grid(row=1, column=column, sticky=(N, W, E, S))
        ani_console.grid_rowconfigure(1, weight=1)
        ani_console.grid_columnconfigure(column, weight=1)
        ani_console['relief'] = 'raised'

    def __init__(self):
        self.root = Tk()
        self.root.title('MyTk Root')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.draw_mainframe(0)
        self.draw_mainframe(1)


myTk = MyTk()
myTk.root.mainloop()
