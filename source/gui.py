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
        self.root.mainloop()
