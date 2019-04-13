""" StateEngineCrank Tkinter GUI View """

# System imports
import threading
from tkinter import *
from tkinter import ttk
import time
import math

# Project imports
import Defines
import mvc


class Animation(object):
    """ Common definition of a GUI Animation View """

    def __init__(self, parent=None, root=None, mainframe=None, config=None, common=None):
        super().__init__()
        self.parent=parent
        self.root = root
        self.mainframe = mainframe
        self.config = config
        self.common = common
        self.row = 0
        self.col = self.config['column']

        # Top level frame for this simulation
        self.ani_frame = ttk.Frame(self.mainframe, padding="3 3 12 12")
        self.ani_frame['borderwidth'] = 4
        self.ani_frame['relief'] = 'sunken'
        self.ani_frame.grid(row=self._next_row(), column=config['column'], sticky=self.common['frame stick'])

        self.ani_label = Label(self.ani_frame, text=config['title'])
        self.ani_label.grid(row=self._next_row(), column=config['column'], sticky=self.common['label stick'])

        # Top level frame for this simulation animation
        self.ani_animation_frame = ttk.Frame(self.ani_frame, padding="3 3 12 12")
        self.ani_animation_frame.grid(row=self._next_row(), column=config['column'],
                                      sticky=self.common['animation stick'])
        self.ani_animation_frame['borderwidth'] = 4
        self.ani_animation_frame['relief'] = 'sunken'

        self.ani_animation_text = Label(self.ani_animation_frame, text=self.config['animation text'])
        self.ani_animation_text.grid(row=0, column=0)

        # Define a canvas where animation graphics can be drawn
        self.ani_canvas = Canvas(self.ani_animation_frame,
                                 width=self.common['animation']['width'],
                                 height=self.common['animation']['height'])

        # Calculate the center of the animation canvas
        self.ani_center = (self.common['animation']['width']/2, self.common['animation']['height']/2)

        # Buttons and controls frame
        self.ani_buttons_frame = ttk.Frame(self.ani_frame)
        self.ani_buttons_frame.grid(row=self._next_row(), column=config['column'], sticky=self.common['buttons stick'])
        self.ani_buttons_frame['borderwidth'] = 4
        self.ani_buttons_frame['relief'] = 'raised'

        self.buttons = [
            ['Start', self._button_start],
            ['Stop', self._button_stop],
            ['Step', self._button_step],
            ['Pause', self._button_pause],
            ['Resume', self._button_resume],
        ]

        self.ani_buttons = {}
        column = -1
        button_row = self._next_row()
        for b in self.buttons:
            column += 1
            self.ani_buttons[b[0]] = ttk.Button(self.ani_buttons_frame, text=b[0], command=b[1])
            self.ani_buttons[b[0]].grid(row=button_row, column=column)

        # Console for text and logging output
        self.ani_console_label = Label(self.ani_frame, text='Console Log')
        self.ani_console_label.grid(row=self._next_row(),
                                    column=self.col,
                                    sticky=self.common['console label stick'])
        self.ani_console = Text(self.ani_frame,
                                height=self.common['console']['height'],
                                width=self.common['console']['width'])
        self.ani_console.grid(row=self._next_row(),
                              column=self.col,
                              sticky=self.common['console stick'])
        self.ani_console.insert('2.0', config['console text'])

        # Set frame weights
        self.root.grid_columnconfigure(self.col, weight=1)
        self.mainframe.grid_columnconfigure(self.col, weight=1)
        self.ani_animation_frame.grid_columnconfigure(self.col, weight=1)
        self.ani_frame.grid_columnconfigure(self.col, weight=1)
        self.ani_console.grid_columnconfigure(self.col, weight=1)

    def _next_row(self):
        self.row = self.row + 1
        return self.row

    def _button_start(self):
        self.parent.update(self.config['event.class'](mvc.MVC.Event.Start))

    def _button_step(self):
        self.parent.update(self.config['event.class'](mvc.MVC.Event.Step))

    def _button_stop(self):
        self.parent.update(self.config['event.class'](mvc.MVC.Event.Stop))

    def _button_pause(self):
        self.parent.update(self.config['event.class'](mvc.MVC.Event.Pause))

    def _button_resume(self):
        self.parent.update(self.config['event.class'](mvc.MVC.Event.Resume))


class DiningPhilosopherEvents(mvc.MVC.Event):
    """ Define events in terms of base class events """

    def __init__(self, event, **kwargs):
        mvc.MVC.Event.__init__(self, event, **kwargs)


class SleepingBarberEvents(mvc.MVC.Event):
    """ Define events in terms of base class events """

    def __init__(self, event, **kwargs):
        mvc.MVC.Event.__init__(self, event, **kwargs)


class DiningPhilosophers(Animation):
    """ Logic to Manage Dining Philosophers Simulation Animation """

    def __init__(self, parent=None, root=None, mainframe=None, config=None, common=None):
        super().__init__(self, root, mainframe, config, common)
        self.my_parent = parent
        self.philosophers = self.config['philosophers']
        self.canvas_x_mid, self.canvas_y_mid = self.ani_center
        self.delta_angle_degrees = 360 / self.philosophers

        self.ani_width = self.common['animation']['width']
        self.ani_height = self.common['animation']['height']
        self.table_radius = self.config['table.radius']
        self.chair_radius = self.config['chair.radius']
        self.fork_radius = self.config['fork.radius']

        self.x_gap = (self.ani_width - 2 * self.table_radius - 4 * self.chair_radius) / 4
        self.y_gap = (self.ani_height - 2 * self.table_radius - 4 * self.chair_radius) / 4
        self.gap = min(self.x_gap, self.y_gap)

    def add_table(self):
        """ Add the main dining table """
        self.circle_at(0, 0, self.table_radius, self.config['table.color'])

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
        self.ani_canvas.grid()

    def add_chairs(self):
        """ Add chairs around the dining table """
        radius = self.table_radius + self.gap + self.chair_radius
        for chair in range(self.philosophers):
            angle = chair * self.delta_angle_degrees
            chair_x, chair_y = self.transform_2xy(radius, angle)
            self.circle_at(chair_x, chair_y, self.chair_radius, self.config['chair.color'])

    def add_forks(self):
        """ Add forks around the table """
        angle_offset = self.delta_angle_degrees/2
        radius = self.table_radius - self.fork_radius*2
        for fork in range(self.philosophers):
            angle = angle_offset + fork * self.delta_angle_degrees
            fork_x, fork_y = self.transform_2xy(radius, angle)
            self.circle_at(fork_x, fork_y, self.fork_radius, self.config['fork.color'])

    def add_philosophers(self):
        """ Add philosophers around the table """
        pass

    def add_waiter(self):
        """ Add the waiter graphic to the simulation """
        waiter_x = -(self.ani_width/2 - self.gap - self.config['waiter.radius'])
        waiter_y = self.ani_height/2 - self.gap - self.config['waiter.radius']
        self.circle_at(0, 0, self.config['waiter.radius'], self.config['waiter.color'])

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

    def update(self, event):
        """ Function to process all animation events

            :param event: Animation event (mvc.MVC.Event...)
        """
        if isinstance(event, int):
            event = self.config['event.class'](event)
        self.my_parent.update(event)


class SleepingBarbers(Animation):
    """ Logic to Manage Sleeping Barber(s) Simulation Animation """

    def __init__(self, parent=None, root=None, mainframe=None, config=None, common=None):
        super().__init__(self, root, mainframe, config, common)
        self.my_parent = parent

    def draw_barbershop(self):
        self.ani_canvas.grid()

    def add_barbers(self):
        pass

    def add_waiting_room(self):
        pass

    def update(self, event):
        """ Function to process all animation events

            :param event: Animation event (mvc.MVC.Event...)
        """
        if isinstance(event, int):
            event = self.config['event.class'](event)
        self.my_parent.update(event)


class GuiConsoleView(mvc.View):
    """ GUI Console View """

    def __init__(self, name, widget):
        super().__init__('%s_console' % name)
        self.widget = widget

    def update(self, event):
        pass

    def run(self):
        pass

    def logger(self, text):
        print(text)


class GuiView(mvc.View):
    """ StateEngineCrank GUI View """

    common_config = {
        'animation': {'width': 360, 'height': 360},
        'animation stick': (N, S, E, W),
        'buttons stick': (W),
        'console': {'width': 40, 'height': 10},
        'console stick': (N, S, E, W),
        'console label stick': (W),
        'frame stick': (N, S, E, W),
        'label stick': (N, W),
    }

    philosophers_config = {
        'title': 'Dining Philosophers',
        'model': 'philosophers',
        'column': 1,
        'animation text': 'The Dining Room',
        'console text': 'Hello, Dining Philosophers',
        'event.class': DiningPhilosopherEvents,

        'philosophers': 5,
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
        'title': 'Sleeping Barber(s)',
        'model': 'barbers',
        'column': 2,
        'animation text': 'The Barber Shop',
        'console text': 'Hello, Sleeping Barber(s)',
        'event.class': SleepingBarberEvents,

        'barbers': 4,
        'chair.radius': 10,
    }

    def __init__(self):
        super().__init__('gui')
        self.root = None
        self.mainframe = None
        self.gui_thread = None

    def update(self, event):
        """ Called to let us know of an event

            :param event: Event that occurred, we should do some kind of update
        """
        if isinstance(event, DiningPhilosopherEvents):
            self.models['philosophers'].update(event)
        elif isinstance(event, SleepingBarberEvents):
            self.models['barbers'].update(event)
        else:
            print(event)

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
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12")     # width=800, height=800)
        self.mainframe.grid(row=1, column=1, sticky=(N, W, E, S))

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
