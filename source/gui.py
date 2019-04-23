""" StateEngineCrank Tkinter GUI View """

# System imports
import threading
from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont

import time
import math

# Project imports
import Defines
import mvc
import exceptions
from StateEngineCrank.modules.PyState import StateMachineEvent as smEvent


class Animation(mvc.View):
    """ Common definition of a GUI Animation View """

    def __init__(self, root=None, mainframe=None, config=None, common=None, parent=None):
        mvc.View.__init__(self, name=('Animation[%s]' % config['model']), parent=parent)
        self.root = root
        self.mainframe = mainframe
        self.config = config
        self.common = common

        # Configure our column in mainframe
        self.ani_frame_column = self.config['column']
        self.mainframe.grid_columnconfigure(self.config['column'], weight=1)

        # --------------------------------------------------------
        # Top level frame for this simulation
        # ani_frame lives in a column of the mainframe
        # --------------------------------------------------------
        self.ani_frame = ttk.LabelFrame(self.mainframe, text=config['title'], padding='4 4 4 4')
        self.ani_frame['relief'] = 'raised'
        self.ani_frame['borderwidth'] = 4
        # row=0, top-most row of the animation frame
        self.ani_frame.grid(row=0, column=self.ani_frame_column, sticky=self.common['ani.frame.stick'])
        self.ani_frame.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------------
        # Top level frame for this simulation animation
        # --------------------------------------------------------
        self.ani_graphics_frame = ttk.LabelFrame(self.ani_frame, text=self.config['animation.text'], padding='4 4 4 4')
        self.ani_graphics_frame['borderwidth'] = 4
        self.ani_graphics_frame['relief'] = 'sunken'
        self.ani_graphics_frame.pack()

        # Define a canvas where animation graphics can be drawn
        self.ani_canvas = Canvas(self.ani_graphics_frame,
                                 width=self.common['animation']['width'],
                                 height=self.common['animation']['height'])
        self.ani_canvas.pack()

        # Calculate the center of the animation canvas
        self.ani_center = (self.common['animation']['width']/2, self.common['animation']['height']/2)
        self.canvas_x_mid, self.canvas_y_mid = self.ani_center

        # --------------------------------------------------------
        # Buttons and controls start a new frame
        # --------------------------------------------------------
        self.ani_buttons_frame = ttk.Frame(self.ani_graphics_frame, padding="4 4 4 4")
        self.ani_buttons_frame['borderwidth'] = 4
        self.ani_buttons_frame['relief'] = 'raised'
        self.ani_buttons_frame.pack(expand=0, fill=X)
        self.buttons = [
            ['Start', self._button_start],
            ['Stop', self._button_stop],
            ['Step', self._button_step],
            ['Pause', self._button_pause],
            ['Resume', self._button_resume],
        ]
        self.ani_buttons = {}
        column = -1
        for b in self.buttons:
            column += 1
            self.ani_buttons[b[0]] = ttk.Button(self.ani_buttons_frame, text=b[0], command=b[1])
            self.ani_buttons[b[0]].pack(expand=0, side=LEFT)

        # --------------------------------------------------------------------------------------
        # Console for text and logging output starts a new frame
        # Organized as a frame within a frame to properly position the textbox and scrollbars.
        #
        # Frame: ani_console_frame (outer frame, holds everything)
        # >> Frame: ani_console_vframe (parent: ani_console_frame)
        # >>>> Text: ani_console_text (parent: ani_console_vframe)
        # >>>> Scrollbar: ani_console_vscrollbar
        # >> Scrollbar: ani_console_hscrollbar (parent: ani_console_frame)
        # --------------------------------------------------------------------------------------
        self.ani_console_frame = ttk.LabelFrame(self.ani_frame,
                                                text='Console Log',
                                                padding="4 4 4 4")
        self.ani_console_frame.pack(expand=1, fill=BOTH)
        self.ani_console_frame['borderwidth'] = 4
        self.ani_console_frame['relief'] = 'raised'

        # vframe to hold the textbox and the vertical scrollbar
        # parent is ani_console_frame
        self.ani_console_vframe = ttk.Frame(self.ani_console_frame)
        self.ani_console_vframe.pack(expand=1, fill=BOTH)
        self.ani_console_font = tkFont.Font(family='Courier')
        self.ani_console_font.configure(size=8)
        self.ani_console_text = Text(self.ani_console_vframe,
                                     font=self.ani_console_font,
                                     wrap=NONE,
                                     height=self.common['console']['height'],
                                     width=self.common['console']['width'])
        self.ani_console_text.pack(side='left', expand=1, fill=BOTH)
        # parent is ani_console_vframe
        self.ani_console_vscrollbar = Scrollbar(self.ani_console_vframe, orient="vertical",
                                                command=self.ani_console_text.yview)
        self.ani_console_vscrollbar.pack(side='right', fill='y')
        # parent is ani_console_frame
        self.ani_console_hscrollbar = Scrollbar(self.ani_console_frame, orient="horizontal",
                                                command=self.ani_console_text.xview)
        self.ani_console_hscrollbar.pack(side='bottom', fill='x')

        self.ani_console_text.config(yscrollcommand=self.ani_console_vscrollbar.set)
        self.ani_console_text.config(xscrollcommand=self.ani_console_hscrollbar.set)

        # --------------------------------------------------------
        # Stuff some introductory text into the text display
        self.ani_console_text.insert('2.0', config['console.text'])
        self.ani_console_text.insert(END, '\n\n')

        # --------------------------------------------------------
        # Animation Button Events
        # --------------------------------------------------------
        self.mvc_events = mvc.Event()
        try:
            self.mvc_events.register_class(config['event.class'])
        except exceptions.ClassAlreadyRegistered:
            pass
        self.mvc_events.register_actor(config['event.class'], self.name)
        self.mvc_events.register_event(config['event.class'], 'Start', event_type='view', text='Start')
        self.mvc_events.register_event(config['event.class'], 'Step', event_type='view', text='Step')
        self.mvc_events.register_event(config['event.class'], 'Stop', event_type='view', text='Stop')
        self.mvc_events.register_event(config['event.class'], 'Pause', event_type='view', text='Pause')
        self.mvc_events.register_event(config['event.class'], 'Resume', event_type='view', text='Resume')
        self.mvc_events.register_event(config['event.class'], 'Logger', event_type='view', text='Logger')

    def run(self):
        """ Satisfy base class requirements """
        pass

    def update(self, event):
        """ Satisfy base class requirements """
        pass

    def _button_start(self):
        self.parent.update(self.mvc_events.post(self.config['event.class'], 'Start', self.name))

    def _button_step(self):
        self.parent.update(self.mvc_events.post(self.config['event.class'], 'Step', self.name))

    def _button_stop(self):
        self.parent.update(self.mvc_events.post(self.config['event.class'], 'Stop', self.name))

    def _button_pause(self):
        self.parent.update(self.mvc_events.post(self.config['event.class'], 'Pause', self.name))

    def _button_resume(self):
        self.parent.update(self.mvc_events.post(self.config['event.class'], 'Resume', self.name))

    def canvas_xy(self, animation_x, animation_y):
        """ Convert an animation x-y coordinate to canvas x-y coordinate

            For the purpose of placing objects in the animation frame, the center of the frame
            is considered to be cartesian coordinate (0, 0). This routine converts from an
            animation coordinate to an absolute Tk.Frame.Canvas coordinate.

            Example:
                * Frame.Canvas is created with width=300 and height=300
                * Frame.Canvas center is at [150, 150]
                * The corresponding Animation coordinate is [0, 0]

            :param animation_x: Animation x-coordinate
            :param animation_y: Animation y-coordinate
            :returns: (canvas_x, canvas_y)
        """
        return animation_x+self.canvas_x_mid, animation_y+self.canvas_y_mid

    def circle_at(self, x, y, r, c):
        """ Draw a circle at [x,y] coordinates, radius 'r'

            :param x: x-coordinate
            :param y: y-coordinate
            :param r: radius
            :param c: fill color
        """
        canvas_x1, canvas_y1 = self.canvas_xy(x-r, y+r)
        canvas_x2, canvas_y2 = self.canvas_xy(x+r, y-r)
        self.ani_canvas.create_oval(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill=c)
        self.ani_canvas.pack()

    def text_at(self, x, y, t, c):
        """ Draw text at [x,y] coordinates

            :param x: x-coordinate
            :param y: y-coordinate
            :param t: text
            :param c: color
        """
        self.ani_canvas.create_text(self.canvas_xy(x, y), text=t, fill=c)
        self.ani_canvas.pack()

    @staticmethod
    def transform_2xy(radius, angle):
        """ Perform transformation from radius, angle to x & y coordinates

            :param radius: length of the vector
            :param angle: angle in radians
            :returns: x, y coordinates
        """
        x = radius * math.sin(math.radians(angle))
        y = radius * math.cos(math.radians(angle))
        return x, y


class DiningPhilosophers(Animation):
    """ Logic to Manage Dining Philosophers Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None, parent=None):
        super().__init__(root=root, mainframe=mainframe, config=config, common=common, parent=self)
        self.my_parent = parent
        self.num_philosophers = self.config['philosophers']
        self.delta_angle_degrees = 360 / self.num_philosophers

        self.ani_width = self.common['animation']['width']
        self.ani_height = self.common['animation']['height']
        self.table_radius = self.config['table.radius']
        self.chair_radius = self.config['chair.radius']
        self.fork_radius = self.config['fork.radius']

        self.x_gap = (self.ani_width - 2 * self.table_radius - 4 * self.chair_radius) / 4
        self.y_gap = (self.ani_height - 2 * self.table_radius - 4 * self.chair_radius) / 4
        self.gap = min(self.x_gap, self.y_gap)

        self.philosopher_coords = []
        self.fork_coords = []
        self.chair_coords = []
        self.waiter_coords = []

    def add_table(self):
        """ Add the main dining table """
        self.circle_at(0, 0, self.table_radius, self.config['table.color'])

    def add_chairs(self):
        """ Add chairs around the dining table """
        radius = self.table_radius + self.gap + self.chair_radius
        for chair in range(self.num_philosophers):
            angle = chair * self.delta_angle_degrees
            cx, cy = self.transform_2xy(radius, angle)
            self.chair_coords.append([cx, cy])
            self.circle_at(cx, cy, self.chair_radius, self.config['chair.color'])

    def add_philosophers(self):
        """ Add philosophers around the table """
        radius = self.table_radius + self.gap + self.chair_radius
        for p in range(self.num_philosophers):
            angle = p * self.delta_angle_degrees
            px, py = self.transform_2xy(radius, angle)
            self.philosopher_coords.append([px, py])
            self.text_at(px, py, 'P%s' % p, 'white')

    def add_forks(self):
        """ Add forks around the table """
        angle_offset = self.delta_angle_degrees/2
        radius = self.table_radius - self.fork_radius*2
        for f in range(self.num_philosophers):
            angle = angle_offset + f * self.delta_angle_degrees
            fx, fy = self.transform_2xy(radius, angle)
            self.fork_coords.append([fx, fy])
            self.circle_at(fx, fy, self.fork_radius, self.config['fork.color'])
            self.text_at(fx, fy, 'F', 'white')

    def add_waiter(self):
        """ Add the waiter graphic to the simulation """
        waiter_x = -(self.ani_width/2 - self.gap - self.config['waiter.radius'])
        waiter_y = self.ani_height/2 - self.gap - self.config['waiter.radius']
        self.circle_at(0, 0, self.config['waiter.radius'], self.config['waiter.color'])
        self.waiter_coords.append([0, 0])
        self.ani_canvas.create_text(self.ani_center, text='Waiter', fill='white')
        self.ani_canvas.pack()

    def update(self, event):
        """ Function to process all animation events

            :param event: Animation event (mvc.Event)
        """
        if hasattr(self, 'parent'):
            self.my_parent.update(event)
        self.notify(event)


class SleepingBarbers(Animation):
    """ Logic to Manage Sleeping Barber(s) Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None, parent=None):
        super().__init__(root=root, mainframe=mainframe, config=config, common=common, parent=self)

    def draw_barbershop(self):
        self.ani_canvas.pack()

    def add_barbers(self):
        pass

    def add_waiting_room(self):
        pass

    def update(self, event):
        """ Function to process all animation events

            :param event: Animation event (mvc.Event)
        """
        if hasattr(self, 'parent'):
            self.parent.update(event)
        self.notify(event)


class GuiConsoleView(mvc.View):
    """ GUI Console View """

    def __init__(self, name, widget):
        super().__init__('%s_console' % name)
        self.widget = widget

    def update(self, event):
        ts = event['datetime'].strftime('%H:%M:%S:%f')
        msg = '{} [{}]'.format(ts, event['class'])
        if 'text' in event.keys() and event['text'] is not None:
            msg = '{} {}'.format(msg, event['text'])
        if 'data' in event.keys() and event['data'] is not None:
            msg = '{} {}'.format(msg, event['data'])
        self.widget.ani_console_text.insert(END, msg+'\n')
        self.widget.ani_console_text.see(END)

    def run(self):
        pass

    def logger(self, text):
        print(text)


class GuiView(mvc.View):
    """ StateEngineCrank GUI View """

    common_config = {
        'mainframe.stick': (N, S, E, W),
        'animation': {'width': 320, 'height': 320},
        'animation.stick': N,
        'buttons.stick': N,
        'console': {'width': 40, 'height': 10},
        'console.stick': (N, S, E, W),
        'console.label.stick': N,
        'console.frame.stick': (N, S, E, W),
        'ani.frame.stick': (N, S, E, W),
        'label.stick': N,
    }

    philosophers_config = {
        'title': 'Dining Philosophers Simulation',
        'model': 'philosophers',
        'column': 0,
        'animation.text': 'The Dining Room',
        'console.text': 'Hello, Dining Philosophers',
        'event.class': 'philosophers',

        'philosophers': 9,
        'fork.radius': 10,
        'fork.color': 'green',
        'table.radius': 75,
        'table.color': 'grey',
        'chair.radius': 20,
        'chair.color': 'grey',
        'waiter.radius': 25,
        'waiter.color': 'blue',
    }

    barbers_config = {
        'title': 'Sleeping Barber(s) Simulation',
        'model': 'barbers',
        'column': 1,
        'animation.text': 'The Barber Shop',
        'console.text': 'Hello, Sleeping Barber(s)',
        'event.class': 'barbers',

        'barbers': 4,
        'chair.radius': 10,
    }

    def __init__(self):
        super().__init__('gui')
        self.root = None
        self.mainframe = None
        self.gui_thread = None
        self.tkobj_dictionary = {}
        self.tkobj_dictionary2 = {}
        self.tkobj_deltas = []

        # create an event lookup table of all registered events
        # we will use this to lookup screen for events we want to process
        self.events = mvc.Event()

        # scan for StateMachine events
        self.sme = smEvent()
        self.sm_events = {}
        for sme_ in smEvent.SmEvents:
            sme_ = str(sme_)
            if sme_.startswith('SmEvents.'):
                sme_ = sme_[len('SmEvents.'):]
            event = self.events.lookup_event('SM', sme_)
            if event is None:
                raise 'SM Event not found : {}'.format(sme_)
            self.sm_events[event['event']] = event

        # scan for Waiter events
        self.waiter_events = {}
        for class_ in self.events.events.keys():
            for event_ in self.events.events[class_].keys():
                event__ = self.events.events[class_][event_]
                if event__['class'].lower() == 'waiter':
                    self.waiter_events[event__['event']] = event__
        print()

    def update(self, event):
        """ Called to let us know of an event

            :param event: Event that occurred, we should do some kind of update
        """
        if event['class'].lower() == 'philosophers':
            self.models['philosophers'].update(event)
        elif event['class'].lower() == 'waiter':
            self.update_gui('waiter', event)
        elif event['class'].lower() == 'barbers':
            self.models['barbers'].update(event)
        elif event['class'].lower() == 'mvc':
            self.update_gui('mvc', event)
        elif event['class'].lower() == 'sm':
            pass
        else:
            print(event)

    def update_gui(self, gui, event):
        if gui is 'waiter':
            self.update_gui_waiter(event)

    def update_gui_waiter(self, event):
        print('waiter: %s' % event)

    def update_dining_console(self, event):
        pass

    def run(self):
        # wait for models to register with
        while len(self.models) is 0:
            time.sleep(0.010)

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

    def write(self, text):
        print(text)

    def tk_run(self):
        """ GUI view running - setup basic framework """
        self.root = Tk()
        self.root.title(Defines.TITLE)
        self.root.config(bg='red')
        # root
        #   * an expanding box, i.e.
        #   * 1 row, weight=1
        #   * 1 column, weight=1
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # mainframe:
        #   * 1 row, weight=1
        #   * 'n' columns, weight=1
        #   * columns are configured by the animations that occupy them
        self.mainframe = ttk.Frame(self.root, relief='sunken', padding="8 8 8 8", name='mainframe')
        self.mainframe.grid(row=0, column=0, sticky=(N, W, E, S))
        self.mainframe.grid_rowconfigure(0, weight=1)

        # instantiate our GUI animation views
        ani_dining = DiningPhilosophers(parent=self, root=self.root, mainframe=self.mainframe,
                                        config=self.philosophers_config, common=self.common_config)
        dining_gui_console = GuiConsoleView('philosophers', ani_dining)

        ani_barbers = SleepingBarbers(parent=self, root=self.root, mainframe=self.mainframe,
                                      config=self.barbers_config, common=self.common_config)
        barbers_gui_console = GuiConsoleView('barbers', ani_barbers)

        # register our console views
        if self.philosophers_config['model'] in self.models:
            self.models[self.philosophers_config['model']].register(dining_gui_console)
        if self.barbers_config['model'] in self.models:
            self.models[self.barbers_config['model']].register(barbers_gui_console)

        # Populate DiningPhilosophers animation graphics
        ani_dining.add_table()
        ani_dining.add_chairs()
        ani_dining.add_forks()
        ani_dining.add_waiter()
        ani_dining.add_philosophers()

        # Populate SleepingBarbers animation graphics
        ani_barbers.draw_barbershop()
        ani_barbers.add_barbers()
        ani_barbers.add_waiting_room()
        for b in ani_barbers.ani_buttons.keys():
            ani_barbers.ani_buttons[b].state(['disabled'])

        # all setup so run
        self.root.mainloop()
