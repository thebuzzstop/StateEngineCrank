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

        # Establish the rows of our animation layout
        # Row: 0 - the only row of the top-level frame
        self.ani_frame_row_ = -1
        self.ani_frame_row = self._next_ani_frame_row()

        # Top level frame for this simulation
        self.ani_frame = ttk.Frame(self.mainframe, padding='4 4 4 4', name=self.name_rc('ani_frame'))
        self.ani_frame['relief'] = 'raised'
        self.ani_frame['borderwidth'] = 4
        # row=0, top-most row of the animation frame
        self.ani_frame.grid(row=self.ani_frame_row, column=self.ani_frame_column, sticky=self.common['ani.frame.stick'])
        self.ani_frame.grid_columnconfigure(0, weight=1)

        self.ani_frame_label = Label(self.ani_frame, text=config['title'], name=self.name_rc('ani_frame_label'))
        self.ani_frame_label_row = self._next_ani_frame_row()   # first row of ani_frame
        self.ani_frame_label.grid(row=self.ani_frame_label_row, sticky=self.common['label.stick'])

        # Top level frame for this simulation animation
        self.ani_graphics_frame = ttk.Frame(self.ani_frame, padding='4 4 4 4',
                                            name=self.name_rc('ani_graphics_frame'))
        self.ani_graphics_frame['borderwidth'] = 4
        self.ani_graphics_frame['relief'] = 'sunken'
        self.ani_graphics_frame_row = self._next_ani_frame_row()
        self.ani_graphics_frame.grid(row=self.ani_graphics_frame_row, sticky=self.common['animation.stick'])
        self.ani_graphics_frame.grid_rowconfigure(self.ani_graphics_frame_row, weight=1)

        self.ani_animation_title = Label(self.ani_graphics_frame, text=self.config['animation.text'],
                                         name=self.name_rc('ani_animation_text'))
        self.ani_animation_title.grid(sticky='n')

        # Define a canvas where animation graphics can be drawn
        self.ani_canvas = Canvas(self.ani_graphics_frame,
                                 width=self.common['animation']['width'],
                                 height=self.common['animation']['height'],
                                 name=self.name_rc('ani_canvas'))
        self.ani_canvas.grid(sticky='n')

        # Calculate the center of the animation canvas
        self.ani_center = (self.common['animation']['width']/2, self.common['animation']['height']/2)

        # Buttons and controls start a new frame
        self.ani_buttons_frame = ttk.Frame(self.ani_frame, padding="4 4 4 4", name=self.name_rc('ani_buttons_frame'))
        self.ani_buttons_frame['borderwidth'] = 4
        self.ani_buttons_frame['relief'] = 'raised'
        self.ani_buttons_frame_row = self._next_ani_frame_row()
        self.ani_buttons_frame.grid(row=self.ani_buttons_frame_row, sticky=self.common['buttons.stick'])

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
            self.ani_buttons[b[0]].grid(row=0, column=column)

        # Console for text and logging output starts a new frame
        self.ani_console_frame = ttk.Frame(self.ani_frame, padding="4 4 4 4", name=self.name_rc('ani_console_frame'))
        self.ani_console_frame_row = self._next_ani_frame_row()
        self.ani_console_frame.grid(row=self.ani_console_frame_row, sticky=self.common['console.frame.stick'])
        self.ani_console_frame.grid_rowconfigure(self.ani_console_frame_row, weight=1)
        self.ani_console_frame.grid_columnconfigure(0, weight=1)
        self.ani_console_frame['borderwidth'] = 4
        self.ani_console_frame['relief'] = 'raised'
        self.ani_console_label_row = 0
        self.ani_console_text_row = 1
        self.ani_console_label = Label(self.ani_console_frame, text='Console Log',
                                       name=self.name_rc('ani_console_label'))
        self.ani_console_label.grid(row=self.ani_console_label_row, sticky=self.common['console.label.stick'])
        self.ani_console_text = Text(self.ani_console_frame,
                                     height=self.common['console']['height'],
                                     width=self.common['console']['width'],
                                     name=self.name_rc('ani_console_text'))
        self.ani_console_text.grid(row=self.ani_console_text_row, sticky=self.common['console.stick'])
        self.ani_console_text.grid_rowconfigure(self.ani_console_text_row, weight=1)
        self.ani_console_text.insert('2.0', config['console.text'])
        self.ani_console_text.insert(END, '\n\n')

        # Animation Button Events
        self.mvc_events = mvc.Event()
        self.mvc_events.register_class(config['event.class'])
        self.mvc_events.register_event(config['event.class'], 'Start', event_type='view', text='Start')
        self.mvc_events.register_event(config['event.class'], 'Step', event_type='view', text='Step')
        self.mvc_events.register_event(config['event.class'], 'Stop', event_type='view', text='Stop')
        self.mvc_events.register_event(config['event.class'], 'Pause', event_type='view', text='Pause')
        self.mvc_events.register_event(config['event.class'], 'Resume', event_type='view', text='Resume')
        self.mvc_events.register_event(config['event.class'], 'Logger', event_type='view', text='Logger')

    def name_rc(self, base):
        return '%s-%s-%s' % (base, self.ani_frame_row_, self.ani_frame_column)

    def run(self):
        """ Satisfy base class requirements """
        pass

    def update(self, event):
        """ Satisfy base class requirements """
        pass

    def _next_ani_frame_row(self):
        self.ani_frame_row_ += 1
        return self.ani_frame_row_

    def _button_start(self):
        self.parent.update(self.mvc_events.events[self.config['event.class']]['Start'])

    def _button_step(self):
        self.parent.update(self.mvc_events.events[self.config['event.class']]['Step'])

    def _button_stop(self):
        self.parent.update(self.mvc_events.events[self.config['event.class']]['Stop'])

    def _button_pause(self):
        self.parent.update(self.mvc_events.events[self.config['event.class']]['Pause'])

    def _button_resume(self):
        self.parent.update(self.mvc_events.events[self.config['event.class']]['Resume'])


class DiningPhilosophers(Animation):
    """ Logic to Manage Dining Philosophers Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None, parent=None):
        super().__init__(root=root, mainframe=mainframe, config=config, common=common, parent=self)
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
        self.ani_canvas.grid()

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
        msg = '%s [%s] %s\n' % (ts, event['class'], event['text'])
        self.widget.ani_console.insert(END, msg)

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
        'title': 'Dining Philosophers',
        'model': 'philosophers',
        'column': 0,
        'animation.text': 'The Dining Room',
        'console.text': 'Hello, Dining Philosophers',
        'event.class': 'philosophers',

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
        print('==========================================================================================')
        self.dump_tkinfo(1, self.root)

        print('---------------------------------')
        for tkobj in self.tkobj_dictionary.keys():
            if tkobj in self.tkobj_dictionary2.keys():
                print('{}\n{}\n{}\n'.format(tkobj, self.tkobj_dictionary[tkobj], self.tkobj_dictionary2[tkobj]))

    def update_gui(self, gui, event):
        # print('%s[%s] %s -> %s' % (event.sm_name, event.sm_event, event.sim_event, event.sim_state))
        if gui is 'waiter':
            self.update_dining_console(event)

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

    def dump_tkinfo(self, level, tkobj):

        parent = 'unknown'
        name = 'noname'
        height = 'unknown'
        width = 'unknown'
        sticky = '-'
        row = '-'
        col = '-'
        grid_size = '(c, r)'

        if hasattr(tkobj, 'winfo_width'):
            width = tkobj.winfo_width()
        if hasattr(tkobj, 'winfo_height'):
            height = tkobj.winfo_height()

        if hasattr(tkobj, 'grid_info'):
            grid_info = tkobj.grid_info()
            row = grid_info['row']
            col = grid_info['column']
            sticky = grid_info['sticky']
            grid_size = tkobj.grid_size()
        if hasattr(tkobj, 'master'):
            if hasattr(tkobj.master, '_name'):
                parent = tkobj.master._name

        if hasattr(tkobj, '_name'):
            name = tkobj._name
            if name not in self.tkobj_dictionary:
                self.tkobj_dictionary[name] = {'width': width, 'height': height}
            else:
                if width != self.tkobj_dictionary[name]['width'] or height != self.tkobj_dictionary[name]['height']:
                    self.tkobj_dictionary2[name] = {'width': width, 'height': height}

        level_ = '+'*level
        level_ = level_ + ' '*(6-level)

        print('Level{}{} wininfo [{:4}/{:4}] row/column: {}/{} sticky: {:4} grid: {} name: {:24} parent: {:24}'
              .format(level, level_, width, height, row, col, sticky, grid_size, name, parent))

        # recurse through all children
        for child in tkobj.children.keys():
            self.dump_tkinfo(level + 1, tkobj.children[child])

    def dict_info(self, dict_):
        for key in dict(dict_).keys():
            value_ = dict_[key]
            type_ = str(type(value_))
            print('{:20} : {:10} {}'.format(key, type_, value_))

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
        self.mainframe = ttk.Frame(self.root, relief='sunken', padding="10 10 10 10", name='mainframe')
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

        print('==========================================================================================')
        self.dict_info(self.root)
        print('=========================================')
        self.dict_info(self.mainframe)
        print('=========================================')
        self.dict_info(self.mainframe.children['ani_frame-0-0'])

        # all setup so run
        self.root.mainloop()
