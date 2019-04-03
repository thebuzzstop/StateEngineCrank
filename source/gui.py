""" StateEngineCrank Tkinter GUI View """

# System imports
import threading
from tkinter import *
from tkinter import ttk
import time

# Project imports
import Defines
import mvc


class Animation(object):
    """ Common definition of a GUI Animation View """

    def __init__(self, root=None, mainframe=None, config=None):
        super().__init__()
        self.root = root
        self.mainframe = mainframe
        self.config = config
        self.row = 0
        self.col = self.config['column']

        # Top level frame for this simulation
        ani_frame = ttk.Frame(self.mainframe, padding="3 3 12 12")
        ani_frame.grid(row=self.next_row(), column=config['column'], sticky=self.config['frame stick'])
        ani_label = Label(ani_frame, text=config['title'])
        ani_label.grid(row=self.next_row(), column=config['column'], sticky=self.config['label stick'])

        # Top level frame for this simulation animation
        ani_animation_frame = ttk.Frame(ani_frame, padding="3 3 12 12")
        ani_animation_frame.grid(row=self.next_row(), column=config['column'], sticky=self.config['animation stick'])
        ani_animation_coming_soon = Label(ani_animation_frame, text='Coming soon to this space')
        ani_animation_coming_soon.grid(row=0, column=0)

        # Buttons and controls frame
        ani_buttons_frame = ttk.Frame(ani_frame)
        ani_buttons_frame.grid(row=self.next_row(), column=config['column'], sticky=self.config['buttons stick'])
        ani_button_start = ttk.Button(ani_buttons_frame, text='Start')
        ani_button_start.grid(row=0, column=1)
        ani_button_step = ttk.Button(ani_buttons_frame, text='Step')
        ani_button_step.grid(row=0, column=2)
        ani_button_pause = ttk.Button(ani_buttons_frame, text='Pause')
        ani_button_pause.grid(row=0, column=3)
        ani_button_stop = ttk.Button(ani_buttons_frame, text='Stop')
        ani_button_stop.grid(row=0, column=4)

        # Console for text and logging output
        ani_console_label = Label(ani_frame, text='Console Log')
        ani_console_label.grid(row=self.next_row(), column=self.col, sticky=self.config['console label stick'])
        ani_console = Text(ani_frame, height=10)
        ani_console.grid(row=self.next_row(), column=self.col, sticky=self.config['console stick'])
        ani_console.insert('2.0', config['console text'])

        # Set frame weights
        self.root.grid_columnconfigure(self.col, weight=1)
        self.mainframe.grid_columnconfigure(self.col, weight=1)
        ani_animation_frame.grid_columnconfigure(self.col, weight=1)
        ani_frame.grid_columnconfigure(self.col, weight=1)
        ani_console.grid_columnconfigure(self.col, weight=1)

    def next_row(self):
        self.row = self.row + 1
        return self.row


class GuiView(mvc.View):
    """ StateEngineCrank GUI View """

    philosophers = {
        'title': 'Dining Philosophers',
        'column': 1,
        'frame stick': (N, W),
        'label stick': (N, W),
        'animation stick': (W),
        'buttons': ['Start', 'Step', 'Stop', 'Pause'],
        'buttons stick': (N, W),
        'console text': 'Hello, Dining Philosophers',
        'console label stick': (W),
        'console stick': (S, W),
    }

    barbers = {
        'title': 'Sleeping Barber(s)',
        'column': 2,
        'frame stick': (N, W),
        'label stick': (N, W),
        'animation stick': (W),
        'buttons': ['Start', 'Step', 'Stop', 'Pause'],
        'buttons stick': (N, W),
        'console text': 'Hello, Sleeping Barber(s)',
        'console label stick': (W),
        'console stick': (S, E),
    }

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
        self.mainframe.grid(row=1, column=1, sticky=(N, W, E, S))

        # Instantiate the animation blocks
        ani_dining = Animation(self.root, self.mainframe, config=self.philosophers)
        ani_barbers = Animation(self.root, self.mainframe, config=self.barbers)

        # Hook up the buttons


        # all setup so run
        self.root.mainloop()
