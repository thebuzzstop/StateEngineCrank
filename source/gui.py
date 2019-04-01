""" StateEngineCrank Tkinter GUI View """

# System imports
import threading
from tkinter import *
from tkinter import ttk
import time

# Project imports
import Defines
import mvc


class GuiView(mvc.View):
    """ StateEngineCrank GUI View """

    def __init__(self):
        super().__init__('gui')
        self.root = None
        self.mainframe = None
        self.gui_thread = None

    def update(self):
        raise Exception

    def register(self, model):
        self.models[model.name] = model

    def run(self):
        """ GUI view running """
        # wait until we are running:
        while not self.running:
            time.sleep(Defines.Times.Waiting)
        # start the GUI thread
        self.gui_thread = threading.Thread(target=self.tk_run, name='tk_gui')
        self.gui_thread.start()
        # loop until no longer running
        while self.running:
            time.sleep(Defines.Times.Running)
        # stop the GUI
        self.gui_thread.join(timeout=Defines.Times.Stopping)

    def tk_run(self):
        """ Main routine for Tkinter GUI """
        self.root = Tk()
        self.root.title(Defines.TITLE)
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Dining Philosophers
        dining_frame = ttk.Frame(self.mainframe, padding="3 3 12 12")
        dining_frame.grid(row=1, column=0, sticky=(N, W))
        dining_label = Label(dining_frame, text='Dining Philosophers')
        dining_label.grid()

        # Sleeping Barbers
        barber_frame = ttk.Frame(self.mainframe, padding="3 3 12 12")
        barber_frame.grid(row=1, column=1, sticky=(N, E))
        barber_label = Label(barber_frame, text='Sleeping Barber(s)')
        barber_label.grid()

        # all setup so run
        self.root.mainloop()
