""" StateEngineCrank Tkinter GUI View """

# System imports
from threading import Thread
from tkinter import *
from tkinter import ttk
import time

# 3rd party imports
import tkinter

# Project imports
import Defines
import mvc


class GuiView(mvc.View, Thread):
    """ StateEngineCrank GUI View """

    def __init__(self):
        mvc.View.__init__(self)
        self.running = False
        Thread.__init__(self, target=self.tkrun)
        self.root = None
        self.start()

    def update(self):
        pass

    def run(self):
        self.running = True

    def stop(self):
        self.running = False

    def tkrun(self):
        while not self.running:
            time.sleep(0.1)
        self.root = Tk()
        self.root.title(Defines.TITLE)
        self.root.mainloop()
