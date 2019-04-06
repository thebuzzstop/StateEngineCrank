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

    def __init__(self, root=None, mainframe=None, config=None, common=None):
        super().__init__()
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
        self.ani_frame.grid(row=self.next_row(), column=config['column'], sticky=self.config['frame stick'])

        self.ani_label = Label(self.ani_frame, text=config['title'])
        self.ani_label.grid(row=self.next_row(), column=config['column'], sticky=self.config['label stick'])

        # Top level frame for this simulation animation
        self.ani_animation_frame = ttk.Frame(self.ani_frame, padding="3 3 12 12")
        self.ani_animation_frame.grid(row=self.next_row(), column=config['column'],
                                      sticky=self.config['animation stick'])
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
        self.ani_buttons_frame.grid(row=self.next_row(), column=config['column'], sticky=self.config['buttons stick'])
        self.ani_buttons_frame['borderwidth'] = 4
        self.ani_buttons_frame['relief'] = 'raised'

        self.ani_button_start = ttk.Button(self.ani_buttons_frame, text='Start')
        self.ani_button_start.grid(row=0, column=1)
        self.ani_button_step = ttk.Button(self.ani_buttons_frame, text='Step')
        self.ani_button_step.grid(row=0, column=2)
        self.ani_button_pause = ttk.Button(self.ani_buttons_frame, text='Pause')
        self.ani_button_pause.grid(row=0, column=3)
        self.ani_button_stop = ttk.Button(self.ani_buttons_frame, text='Stop')
        self.ani_button_stop.grid(row=0, column=4)

        # Console for text and logging output
        self.ani_console_label = Label(self.ani_frame, text='Console Log')
        self.ani_console_label.grid(row=self.next_row(),
                                    column=self.col,
                                    sticky=self.config['console label stick'])
        self.ani_console = Text(self.ani_frame,
                                height=self.common['console']['height'],
                                width=self.common['console']['width'])
        self.ani_console.grid(row=self.next_row(),
                              column=self.col,
                              sticky=self.config['console stick'])
        self.ani_console.insert('2.0', config['console text'])

        # Set frame weights
        self.root.grid_columnconfigure(self.col, weight=1)
        self.mainframe.grid_columnconfigure(self.col, weight=1)
        self.ani_animation_frame.grid_columnconfigure(self.col, weight=1)
        self.ani_frame.grid_columnconfigure(self.col, weight=1)
        self.ani_console.grid_columnconfigure(self.col, weight=1)

    def next_row(self):
        self.row = self.row + 1
        return self.row


class DiningPhilosophers(Animation):
    """ Logic to draw the Dining Philosophers Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None):
        super().__init__(root, mainframe, config, common)
        self.philosophers = self.config['philosophers']
        self.canvas_x_mid, self.canvas_y_mid = self.ani_center
        self.delta_angle_degrees = 360 / self.philosophers

        self.chair_radius = self.config['chair.radius']
        self.table_radius = self.config['table.radius']
        self.ani_width = self.common['animation']['width']
        self.ani_height = self.common['animation']['height']

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
        for chair in range(self.philosophers):
            radius = self.table_radius + self.gap + self.chair_radius
            angle = chair * self.delta_angle_degrees
            chair_x, chair_y = self.transform_2xy(radius, angle)
            self.circle_at(chair_x, chair_y, self.chair_radius, self.config['chair.color'])

    def add_forks(self):
        """ Add forks around the table """
        pass

    def add_philosophers(self):
        """ Add philosophers around the table """
        pass

    def add_waiter(self):
        """ Add the waiter graphic to the simulation """
        waiter_x = -(self.ani_width/2 - self.gap - self.config['waiter.radius'])
        waiter_y = self.ani_height/2 - self.gap - self.config['waiter.radius']
        #self.circle_at(waiter_x, waiter_y, self.config['waiter.radius'], self.config['waiter.color'])
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


class SleepingBarbers(Animation):
    """ Logic to draw the Dining Philosophers Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None):
        super().__init__(root, mainframe, config, common)

    def draw_barbershop(self):
        self.ani_canvas.grid()

    def add_barbers(self):
        pass

    def add_waiting_room(self):
        pass


class GuiView(mvc.View):
    """ StateEngineCrank GUI View """

    common_config = {
        'console': {'width': 40, 'height': 10},
        'animation': {'width': 300, 'height': 300}
    }

    philosophers = {
        'title': 'Dining Philosophers',
        'column': 1,
        'frame stick': (N, W),
        'label stick': (N, W),
        'animation stick': (W),
        'animation text': 'The Dining Room',
        'buttons': ['Start', 'Step', 'Stop', 'Pause'],
        'buttons stick': (N, W),
        'console text': 'Hello, Dining Philosophers',
        'console label stick': (W),
        'console stick': (S, W),

        'philosophers': 5,
        'table.radius': 75,
        'table.color': 'grey',
        'chair.radius': 20,
        'chair.color': 'grey',
        'waiter.radius': 25,
        'waiter.color': 'blue',
    }

    barbers = {
        'title': 'Sleeping Barber(s)',
        'column': 2,
        'frame stick': (N, W),
        'label stick': (N, W),
        'animation stick': (W),
        'animation text': 'The Barber Shop',
        'buttons': ['Start', 'Step', 'Stop', 'Pause'],
        'buttons stick': (N, W),
        'console text': 'Hello, Sleeping Barber(s)',
        'console label stick': (W),
        'console stick': (S, E),

        'barbers': 4,
        'chair.radius': 10,
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
        self.mainframe = ttk.Frame(self.root, padding="3 3 12 12", width=800, height=800)
        self.mainframe.grid(row=1, column=1, sticky=(N, W, E, S))

        # Instantiate DiningPhilosophers and create the animation graphics
        ani_dining = DiningPhilosophers(self.root, self.mainframe, config=self.philosophers, common=self.common_config)
        ani_dining.add_table()
        ani_dining.add_chairs()
        ani_dining.add_forks()
        ani_dining.add_waiter()

        # Instantiate SleepingBarbers and create the animation graphics
        ani_barbers = SleepingBarbers(self.root, self.mainframe, config=self.barbers, common=self.common_config)
        ani_barbers.draw_barbershop()
        ani_barbers.add_barbers()
        ani_barbers.add_waiting_room()

        # Hook up the buttons

        # all setup so run
        self.root.mainloop()
