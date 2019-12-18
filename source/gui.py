""" StateEngineCrank Tkinter GUI View """

# System imports
import copy
import threading
from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont

import enum
import time
import math

# Project imports
import Defines
import mvc
import exceptions
from StateEngineCrank.modules.PyState import StateMachineEvent as smEvent
from DiningPhilosophers.main import WaiterEvents as WaiterEvents
from DiningPhilosophers.main import Events as diningEvents
from DiningPhilosophers.main import States as diningStates
from DiningPhilosophers.main import ForkId

from SleepingBarber.Barber import Events as barberEvents
from SleepingBarber.Barber import States as barberStates
from SleepingBarber.Customer import Events as customerEvents
from SleepingBarber.Customer import States as customerStates
from SleepingBarber.WaitingRoom import WaitingRoom


class AniButtonType(enum.Enum):

    START, STOP, STEP, PAUSE, RESUME = range(5)


class AniButton(ttk.Button):

    def __init__(self, button_id, button_frame, button_text, button_handler):
        """ Animation Button Class

            :param button_id: Animation Button Type ID
            :param button_frame: Ttk parent frame
            :param button_text: Button text
            :param button_handler: Handler for button press events
        """
        self.button_id = button_id
        self.button_frame = button_frame
        self.button_text = button_text
        self.button_handler = button_handler
        ttk.Button.__init__(self, self.button_frame, text=self.button_text, command=self.button_handler)
        self.pack(expand=0, side=LEFT)
        self.disable()

    def enable(self):
        self.config(state=NORMAL)

    def disable(self):
        self.config(state=DISABLED)


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
        self.ani_graphics_frame['relief'] = 'raised'
        self.ani_graphics_frame['borderwidth'] = 4
        self.ani_graphics_frame.pack()

        # Define a canvas where animation graphics can be drawn
        self.ani_canvas = Canvas(self.ani_graphics_frame,
                                 width=self.common['animation']['width'],
                                 height=self.common['animation']['height'])
        self.ani_canvas.pack()

        # Draw outer walls
        self.draw_outer_walls(self.common['wall.thickness'], self.common['wall.color'])

        # Calculate the center of the animation canvas
        self.ani_center = (self.common['animation']['width']/2, self.common['animation']['height']/2)
        self.canvas_x_mid, self.canvas_y_mid = self.ani_center

        # Calculate the animation canvas iteration counter location
        self.counter_x = 40
        self.counter_y = self.common['animation']['height'] - 20
        self.counter_id = None
        self.draw_counter(0)

        # --------------------------------------------------------
        # Buttons and controls start a new frame
        # --------------------------------------------------------
        self.ani_buttons_frame = ttk.Frame(self.ani_graphics_frame, padding="4 4 4 4")
        self.ani_buttons_frame['relief'] = 'raised'
        self.ani_buttons_frame['borderwidth'] = 4
        self.ani_buttons_frame.pack(expand=0, fill=X, side=LEFT)
        self.ani_buttons = {
            AniButtonType.START: AniButton(AniButtonType.START, self.ani_buttons_frame, 'Start', self._button_start),
            AniButtonType.STOP: AniButton(AniButtonType.STOP, self.ani_buttons_frame, 'Stop', self._button_stop),
            AniButtonType.STEP: AniButton(AniButtonType.STEP, self.ani_buttons_frame, 'Step', self._button_step),
            AniButtonType.PAUSE: AniButton(AniButtonType.PAUSE, self.ani_buttons_frame, 'Pause', self._button_pause),
            AniButtonType.RESUME: AniButton(AniButtonType.RESUME, self.ani_buttons_frame, 'Resume', self._button_resume),
        }

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
        self.ani_console_frame['relief'] = 'raised'
        self.ani_console_frame['borderwidth'] = 4

        # --------------------------------------------------------
        # vframe to hold the textbox and the vertical scrollbar
        # --------------------------------------------------------
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
        # --------------------------------------------------------
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
        self.button_events = [
            mvc.Event.Events.START,
            mvc.Event.Events.STOP,
            mvc.Event.Events.STEP,
            mvc.Event.Events.PAUSE,
            mvc.Event.Events.RESUME
        ]
        for event_ in self.button_events:
            self.mvc_events.register_event(config['event.class'], event=event_, event_type='view', text=event_.name)

    def run(self):
        """ Satisfy base class requirements """
        pass

    def update(self, event):
        """ Satisfy base class requirements """
        pass

    def _disable_buttons(self):
        for b in self.ani_buttons.keys():
            self.ani_buttons[b].disable()

    def _button_start(self):
        self.parent.update(self.mvc_events.post(class_name=self.config['event.class'],
                                                event=mvc.Event.Events.START, actor_name=self.name))
        self.ani_buttons[AniButtonType.START].disable()
        self.ani_buttons[AniButtonType.PAUSE].enable()
        self.ani_buttons[AniButtonType.STOP].enable()

    def _button_step(self):
        self.parent.update(self.mvc_events.post(class_name=self.config['event.class'],
                                                event=mvc.Event.Events.STEP, actor_name=self.name))

    def _button_stop(self):
        self.parent.update(self.mvc_events.post(class_name=self.config['event.class'],
                                                event=mvc.Event.Events.STOP, actor_name=self.name))
        self._disable_buttons()
        self.ani_buttons[AniButtonType.START].enable()

    def _button_pause(self):
        self.parent.update(self.mvc_events.post(class_name=self.config['event.class'],
                                                event=mvc.Event.Events.PAUSE, actor_name=self.name))
        self.ani_buttons[AniButtonType.PAUSE].disable()
        self.ani_buttons[AniButtonType.RESUME].enable()
        self.ani_buttons[AniButtonType.STEP].enable()

    def _button_resume(self):
        self.parent.update(self.mvc_events.post(class_name=self.config['event.class'],
                                                event=mvc.Event.Events.RESUME, actor_name=self.name))
        self.ani_buttons[AniButtonType.PAUSE].enable()
        self.ani_buttons[AniButtonType.RESUME].disable()
        self.ani_buttons[AniButtonType.STEP].disable()

    def canvas_xy00(self, animation_x, animation_y):
        """ Convert an animation x-y coordinate to canvas x-y coordinate

            For the purpose of placing objects in the animation frame, the center of the frame
            is considered to be cartesian coordinate [0, 0]. This routine converts from an
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

    def circle_at00(self, x, y, r, c):
        """ Draw a circle at [x,y] coordinates, radius 'r'

            This version of 'circle_at' assumes an origin of [0, 0] at the center of the canvas.

            :param x: x-coordinate
            :param y: y-coordinate
            :param r: radius
            :param c: fill color
        """
        canvas_x1, canvas_y1 = self.canvas_xy00(x - r, y + r)
        canvas_x2, canvas_y2 = self.canvas_xy00(x + r, y - r)
        self.ani_canvas.create_oval(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill=c)
        self.ani_canvas.pack()

    def circle_at(self, x, y, r, c):
        """ Draw a circle at [x,y] coordinates, radius 'r'

            This version of 'circle_at' assumes an origin of [0, 0] at the top left of the canvas.
            There is no adjustment or translation of the [x, y] coordinates passed to us.

            :param x: x-coordinate
            :param y: y-coordinate
            :param r: radius
            :param c: fill color
        """
        self.ani_canvas.create_oval(x-r, y+r, x+r, y-r, fill=c)
        self.ani_canvas.pack()

    def draw_counter(self, count):
        text_ = 'Loops:{:5d}'.format(count)
        color = 'black'
        if self.counter_id is not None:
            self.ani_canvas.delete(self.counter_id)
        self.counter_id = self.ani_canvas.create_text(self.counter_x, self.counter_y, text=text_, fill=color)
        self.ani_canvas.pack()

    def text_at00(self, x, y, t, c):
        """ Draw text at [x, y] coordinates

            This version of 'text_at' assumes an origin of [0, 0] at the center of the canvas.

            :param x: x-coordinate
            :param y: y-coordinate
            :param t: text
            :param c: color
        """
        self.ani_canvas.create_text(self.canvas_xy00(x, y), text=t, fill=c)
        self.ani_canvas.pack()

    def text_at(self, x, y, t, c):
        """ Draw text at [x, y] coordinates

            This version of 'text_at' assumes an origin of [0, 0] at the top left of the canvas.
            There is no adjustment or translation of the [x, y] coordinates passed to us.

            :param x: x-coordinate
            :param y: y-coordinate
            :param t: text
            :param c: color
        """
        self.ani_canvas.create_text(x, y, text=t, fill=c)
        self.ani_canvas.pack()

    @staticmethod
    def transform_2xy(radius, angle):
        """ Perform transformation from radius, angle to [x, y] coordinates

            :param radius: length of the vector
            :param angle: angle in radians
            :returns: x, y coordinates
        """
        x = radius * math.sin(math.radians(angle))
        y = radius * math.cos(math.radians(angle))
        return x, y

    def wall_at(self, x, y, t, l, c):
        """ Draw a wall (rectangle)

            :param x: center line x-coordinate
            :param y: center line y-coordinate
            :param l: length
            :param t: thickness
            :param c: color (fill)
        """
        self.ani_canvas.create_rectangle(x, y+t/2, x+l, y-t/2, fill=c, width=0)

    def draw_outer_walls(self, t, c):
        """ Draw outer walls

            :param t: thickness
            :param c: color (fill)
        """
        # top wall
        self.ani_canvas.create_rectangle(0, 0,
                                         self.common['animation']['width'], t+1,
                                         fill=c, width=0)
        # bottom wall
        self.ani_canvas.create_rectangle(0, self.common['animation']['height']-t+1,
                                         self.common['animation']['width'],
                                         self.common['animation']['height']+1,
                                         fill=c, width=0)
        # left wall
        self.ani_canvas.create_rectangle(0, 0,
                                         t+1, self.common['animation']['height']+1,
                                         fill=c, width=0)
        # right wall
        self.ani_canvas.create_rectangle(self.common['animation']['width']-t, 0,
                                         self.common['animation']['width'], self.common['animation']['height'],
                                         fill=c, width=0)


class DiningPhilosophers(Animation):
    """ Logic to Manage Dining Philosophers Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None, parent=None):
        super().__init__(root=root, mainframe=mainframe, config=config, common=common, parent=self)
        self.my_parent = parent
        self.my_model = self.config['model']
        self.num_philosophers = self.config['philosophers']
        self.delta_angle_degrees = 360 / self.num_philosophers
        self.ani_width = self.common['animation']['width']
        self.ani_height = self.common['animation']['height']
        self.table_radius = self.config['table.radius']
        self.chair_radius = self.config['chair.radius']
        self.fork_radius = self.config['fork.radius']
        self.timer_radius = self.common['timer.radius']

        self.x_gap = (self.ani_width - 2 * self.table_radius - 4 * (self.chair_radius+self.timer_radius)) / 6
        self.y_gap = (self.ani_height - 2 * self.table_radius - 4 * (self.chair_radius+self.timer_radius)) / 6
        self.gap = min(self.x_gap, self.y_gap)

        #: radius of the circle which contains the chairs
        self.chair_circle_radius = self.table_radius + self.gap + self.chair_radius
        #: radius of the circle which contains the timers
        self.timer_circle_radius = self.chair_circle_radius + self.chair_radius + self.gap + self.timer_radius
        #: radius of the circle which contains the forks
        self.fork_circle_radius = self.table_radius - self.fork_radius*2
        #: angular offset for forks to position them between philosophers
        self.fork_angle_offset = -self.delta_angle_degrees/2

        self.philosopher_coords = []
        self.fork_coords = []
        self.chair_coords = []
        self.timer_coords = []
        self.waiter_coords = []

        # despatch table for waiter events
        self.waiter_event_dispatch = {
            WaiterEvents.IN: self.waiter_in,
            WaiterEvents.OUT: self.waiter_out,
            WaiterEvents.ACQUIRE: self.waiter_acquire,
            WaiterEvents.RELEASE: self.waiter_release,
            WaiterEvents.LEFTFORK: self.waiter_left_fork,
            WaiterEvents.RIGHTFORK: self.waiter_right_fork
        }

        # despatch table for SM events
        self.sm_dispatch = {
            diningEvents.EvStart: self.dining_start,
            diningEvents.EvStop: self.dining_stop,
            diningEvents.EvHungry: self.dining_hungry,
            diningEvents.EvHavePermission: self.dining_have_permission,
            diningEvents.EvFull: self.dining_full,

            diningStates.StartUp: self.dining_state_startup,
            diningStates.Thinking: self.dining_state_thinking,
            diningStates.Eating: self.dining_state_eating,
            diningStates.Hungry: self.dining_state_hungry,
            diningStates.Finish: self.dining_state_finish,
        }
        # ------------------------------------------------------
        # Populate DiningPhilosophers animation graphics
        # ------------------------------------------------------
        self.add_table()
        self.add_chairs()
        self.add_forks()
        self.add_waiter()
        self.add_philosophers()
        self.add_timers()
        # Only start button is enabled
        self.ani_buttons[AniButtonType.START].enable()

    def add_table(self):
        """ Add the main dining table """
        self.circle_at00(0, 0, self.table_radius, self.config['table.color'])

    def draw_chair(self, chair, color):
        angle = chair * self.delta_angle_degrees
        cx, cy = self.transform_2xy(self.chair_circle_radius, angle)
        self.circle_at00(cx, cy, self.chair_radius, color)
        return cx, cy

    def add_chairs(self):
        """ Add chairs around the dining table, one chair for each philosopher """
        for chair in range(self.num_philosophers):
            cx, cy = self.draw_chair(chair, self.common['init.color'][0])
            self.chair_coords.append([cx, cy])

    def draw_timer(self, timer, color, text=None):
        angle = timer * self.delta_angle_degrees
        tx, ty = self.transform_2xy(self.timer_circle_radius, angle)
        if text is None:
            text = '0'
        self.circle_at00(tx, ty, self.timer_radius, color[0])
        self.text_at00(tx, ty, '%s' % text, color[1])
        return tx, ty

    def add_timers(self):
        """ Add timers around the dining table, one timer for each philosopher """
        for timer in range(self.num_philosophers):
            tx, ty = self.draw_timer(timer, self.common['init.color'])
            self.timer_coords.append([tx, ty])

    def draw_philosopher(self, pid, color, text=None):
        angle = pid * self.delta_angle_degrees
        px, py = self.transform_2xy(self.chair_circle_radius, angle)
        if text is None:
            self.text_at00(px, py, 'P%s' % pid, color)
        else:
            self.text_at00(px, py, ('P%s-%s' % (pid, text)), color)
        return px, py

    def add_philosophers(self):
        """ Add philosophers around the table """
        for p in range(self.num_philosophers):
            px, py = self.draw_philosopher(p, self.common['init.color'][1])
            self.philosopher_coords.append([px, py])

    def draw_fork(self, fork):
        angle = self.fork_angle_offset + fork * self.delta_angle_degrees
        fx, fy = self.transform_2xy(self.fork_circle_radius, angle)
        self.circle_at00(fx, fy, self.fork_radius, self.config['fork.color'])
        self.text_at00(fx, fy, 'F', 'white')
        return fx, fy

    def add_forks(self):
        """ Add forks around the table, forks are situated between philosophers """
        for f in range(self.num_philosophers):
            fx, fy = self.draw_fork(f)
            self.fork_coords.append([fx, fy])

    def add_waiter(self):
        """ Add the waiter graphic to the simulation """
        self.circle_at00(0, 0, self.config['waiter.chair.radius'], self.config['waiter.color'])
        self.waiter_coords.append([0, 0])
        self.ani_canvas.create_text(self.ani_center, text='Waiter', fill='white')
        self.ani_canvas.pack()

    def update(self, event):
        """ Function to process all animation events

            :param event: Animation event (mvc.Event)
        """
        # MVC class events
        if event['class'].lower() == 'mvc':
            if event['event'] == mvc.Event.Events.TIMER:
                self.timer_handler(event)

        # SM class events
        elif event['class'].lower() == 'sm':
            if 'data' in event.keys() and event['data'] is not None:
                if event['data'] in self.sm_dispatch.keys():
                    self.sm_dispatch[event['data']](event)
                else:
                    self.logger('Unknown SM data: %s' % event['data'])

        # Waiter class events
        elif event['class'].lower() == 'waiter':
            self.waiter_event_dispatch[event['event']](event)

        # Actor events
        elif 'actor' in event.keys():
            if event['actor'] == self.name:
                if hasattr(self, 'parent'):
                    self.my_parent.update(event)
                self.notify(event)
            elif event['actor'].lower() == 'waiter':
                self.waiter_event_dispatch[event['event']](event)
        # process a non-actor event
        else:
            pass

    # ----------------------------------------------------
    # Event processing support functions
    # ----------------------------------------------------
    def timer_handler(self, event):
        time_ = event['data'][0]
        id_ = event['user.id']
        color = self.common['init.color']
        self.draw_timer(id_, color, text=time_)

    def dining_start(self, event):
        pass

    def dining_stop(self, event):
        pass

    def dining_hungry(self, event):
        pass

    def dining_have_permission(self, event):
        pass

    def dining_full(self, event):
        pass

    # ----------------------------------------------------
    # State transition support functions
    # ----------------------------------------------------
    def dining_state_startup(self, event):
        pass

    def dining_state_thinking(self, event):
        if event['event'] == smEvent.SmEvents.STATE_TRANSITION:
            self.draw_chair(event['user.id'], self.config['thinking.color'][0])
            self.draw_philosopher(event['user.id'], self.config['thinking.color'][1], text='T')
            left, right = self.models['Philosophers'].forks(event['user.id'])
            self.draw_fork(left)
            self.draw_fork(right)
        else:
            raise Exception('unexpected event handling')

    def dining_state_eating(self, event):
        if event['event'] == smEvent.SmEvents.STATE_TRANSITION:
            self.draw_chair(event['user.id'], self.config['eating.color'][0])
            self.draw_philosopher(event['user.id'], self.config['eating.color'][1], text='E')
        else:
            raise Exception('unexpected event handling')

    def dining_state_hungry(self, event):
        if event['event'] == smEvent.SmEvents.STATE_TRANSITION:
            self.draw_chair(event['user.id'], self.config['hungry.color'][0])
            self.draw_philosopher(event['user.id'], self.config['hungry.color'][1], text='H')
        else:
            raise Exception('unexpected event handling')

    def dining_state_finish(self, event):
        if event['event'] == smEvent.SmEvents.STATE_TRANSITION:
            self.draw_chair(event['user.id'], self.common['stop.color'][0])
            self.draw_philosopher(event['user.id'], self.common['stop.color'][1])
            left, right = self.models['Philosophers'].forks(event['user.id'])
            self.draw_fork(left)
            self.draw_fork(right)
        else:
            raise Exception('unexpected event handling')

    # ----------------------------------------------------
    # Waiter support functions
    # ----------------------------------------------------
    def waiter_in(self, event):
        pass

    def waiter_out(self, event):
        pass

    def waiter_acquire(self, event):
        philosopher_id = event['data']
        fx, fy = self.waiter_coords[0]
        self.circle_at00(fx, fy, self.config['waiter.chair.radius'], self.config['waiter.color'])
        self.text_at00(fx, fy, 'Wait[%s]' % philosopher_id, 'yellow')

    def waiter_release(self, event):
        fx, fy = self.waiter_coords[0]
        self.circle_at00(fx, fy, self.config['waiter.chair.radius'], self.config['waiter.color'])
        self.text_at00(fx, fy, 'Waiter', 'white')

    def waiter_left_fork(self, event):
        self.waiter_fork_(event, ForkId.Left)

    def waiter_right_fork(self, event):
        self.waiter_fork_(event, ForkId.Right)

    def waiter_fork_(self, event, fork):
        philosopher_id = event['data']
        model = self.models[self.my_model]
        left, right = model.forks(philosopher_id)
        if fork is ForkId.Left:
            fx, fy = self.fork_coords[left]
        else:
            fx, fy = self.fork_coords[right]
        self.circle_at00(fx, fy, self.fork_radius, self.config['fork.color'])
        self.text_at00(fx, fy, '%s' % philosopher_id, 'white')


class SleepingBarbers(Animation):
    """ Logic to Manage Sleeping Barber(s) Simulation Animation """

    def __init__(self, root=None, mainframe=None, config=None, common=None, parent=None):
        super().__init__(root=root, mainframe=mainframe, config=config, common=common, parent=self)
        self.my_parent = parent
        self.my_model = self.config['model']
        self.num_barbers = self.config['barbers']
        self.num_waiters = self.config['waiters']
        self.ani_width = self.common['animation']['width']
        self.ani_height = self.common['animation']['height']
        self.barber_chair_radius = self.config['barber.chair.radius']
        self.waiter_chair_radius = self.config['waiter.chair.radius']
        self.wall_thickness = self.common['wall.thickness']
        self.gap_multiplier = self.config['gap.multiplier']
        self.waiting_room = WaitingRoom()
        #: list of waiting room chairs, will contain the ID of a waiting customer
        self.waiting_chairs = [None for _ in range(self.num_waiters)]
        #: next waiting room chair to occupy
        self.next_waiting_chair_ = -1

        self.barber_chair_spacer = \
            (self.ani_width-(self.num_barbers*self.barber_chair_radius*2))/(self.num_barbers-1+2*self.gap_multiplier)
        self.barber_coords = []
        barber_y = self.ani_height/3
        for b in range(self.num_barbers):
            barber_x = self.gap_multiplier*self.barber_chair_spacer + self.barber_chair_radius + \
                       b*(2*self.barber_chair_radius + self.barber_chair_spacer)
            self.barber_coords.append([barber_x, barber_y])

        self.waiter_chair_spacer = \
            (self.ani_width-(self.num_waiters*self.waiter_chair_radius*2))/(self.num_waiters-1+2*self.gap_multiplier)
        self.waiter_coords = []
        waiter_y = self.ani_height - self.ani_height/3
        for w in range(self.num_waiters):
            waiter_x = self.gap_multiplier*self.waiter_chair_spacer + self.waiter_chair_radius + \
                       w*(2*self.waiter_chair_radius + self.waiter_chair_spacer)
            self.waiter_coords.append([waiter_x, waiter_y])

        self.wall_data = [
            (0, self.ani_height/2, self.common['wall.thickness'], self.ani_width, self.common['wall.color'])
        ]

        self.door_coords = []
        self.barber_door_coords = []
        self.waiter_door_coords = []
        self.timer_coords = {}
        self.sm_dispatch = {
            barberEvents.EvStart: self.barber_start,
            barberEvents.EvStop: self.barber_stop,
            barberEvents.EvCustomerEnter: self.customer_enter,
            barberEvents.EvFinishCutting: self.finish_cutting,

            barberStates.StartUp: self.barber_state_startup,
            barberStates.Cutting: self.barber_state_cutting,
            barberStates.Sleeping: self.barber_state_sleeping,
            barberStates.Finish: self.barber_state_finish,

            customerEvents.EvStart: self.customer_start,
            customerEvents.EvStop: self.customer_stop,
            customerEvents.EvBarberReady: self.customer_barber_ready,
            customerEvents.EvFinishCutting: self.customer_finish_cutting,

            customerStates.StartUp: self.customer_state_startup,
            customerStates.HairCut: self.customer_state_haircut,
            customerStates.Waiting: self.customer_state_waiting,
            customerStates.Finish: self.customer_state_finish
        }

        # ------------------------------------------------------
        # Populate SleepingBarbers animation graphics
        # ------------------------------------------------------
        self.add_walls()
        self.add_barbers()
        self.add_waiting_room()
        self.add_timers()

        # Only start button is enabled
        self.ani_buttons[AniButtonType.START].enable()

    def add_walls(self):
        for w in self.wall_data:
            (x, y, t, l, c) = w
            self.wall_at(x, y, t, l, c)

    def add_barbers(self):
        """ Add barbers and their chairs """
        for b in range(self.num_barbers):
            self.draw_barber(b, self.common['init.color'])

    def add_waiting_room_wall(self):
        pass

    def add_timers(self):
        """ Timers for the barbers and waiting room chairs """
        self.timer_coords['barber'] = []
        for b in range(self.num_barbers):
            bx, by = self.barber_coords[b]
            by -= self.barber_chair_radius + self.barber_chair_spacer + self.config['timer.radius']
            self.timer_coords['barber'].append([bx, by])
            self.draw_timer(self.timer_coords['barber'][b], self.common['init.color'], text='0')
        self.timer_coords['waiter'] = []
        for w in range(self.num_waiters):
            wx, wy = self.waiter_coords[w]
            wy += self.waiter_chair_radius + self.waiter_chair_spacer + self.config['timer.radius']
            self.timer_coords['waiter'].append([wx, wy])
            self.draw_timer(self.timer_coords['waiter'][w], self.common['init.color'], text='0')

    def draw_barber(self, bid, color, text=None):
        bx, by = self.barber_coords[bid]
        self.circle_at(bx, by, self.barber_chair_radius, color[0])
        if text is None:
            self.text_at(bx, by, 'B%s' % bid, color[1])
        else:
            text = text[-5:]
            if not text[0].isdigit():
                text = text[-4:]
            self.text_at(bx, by, ('B%s-%s' % (bid, text)), color[1])

    def add_waiting_room(self):
        """ Add waiting room chairs """
        for w in range(self.num_waiters):
            self.draw_waiter(w, self.common['init.color'])

    def draw_waiter(self, w, color, text=None):
        wx, wy = self.waiter_coords[w]
        self.circle_at(wx, wy, self.waiter_chair_radius, color[0])
        if text is None:
            self.text_at(wx, wy, 'Empty', color[1])
        else:
            self.text_at(wx, wy, ('%s' % text), color[1])

    def draw_timer(self, t, color, text=None):
        tx, ty = t
        self.circle_at(tx, ty, self.config['timer.radius'], color[0])
        if text is not None:
            self.text_at(tx, ty, ('%s' % text), color[1])

    def update(self, event):
        """ Function to process all animation events

            :param event: Animation event (mvc.Event)
        """
        # MVC class events
        if event['class'].lower() == 'mvc':
            if event['event'] == mvc.Event.Events.TIMER:
                self.timer_handler(event)

        # SM class events
        elif event['class'].lower() == 'sm':
            if 'data' in event.keys() and event['data'] is not None:
                if event['data'] in self.sm_dispatch.keys():
                    self.sm_dispatch[event['data']](event)
                else:
                    self.logger('Unknown SM data: %s' % event['data'])

        # Actor events
        elif 'actor' in event.keys():
            if event['actor'] == self.name:
                if hasattr(self, 'parent'):
                    self.my_parent.update(event)
                self.notify(event)
        # process a non-actor event
        else:
            pass

    # ----------------------------------------------------
    # Event processing routines
    # ----------------------------------------------------
    def timer_handler(self, event):
        time_ = event['data'][0]
        id_ = event['user.id']
        if event['data'][1] == barberStates.Sleeping:
            color = self.config['sleeping.color']
            self.draw_timer(self.timer_coords['barber'][id_], color, text=time_)
        elif event['data'][1] == barberStates.Cutting:
            color = self.config['cutting.color']
            self.draw_timer(self.timer_coords['barber'][id_], color, text=time_)
            customer = event['data'][2]
            self.draw_barber(id_, color, text='%s' % event['data'][2].id)
        elif event['data'][1] == barberStates.Stopping:
            color = self.config['cutting.color']
            self.draw_timer(self.timer_coords['barber'][id_], color, text=time_)
        elif event['data'][1] == customerStates.Waiting:
            color = self.config['waiting.color']
            # get a copy of the waiting room list
            waiting_list = copy.copy(self.waiting_room.get_waiting_list())
            id_ = event['user.id']
            time_ = event['data'][0]

            # get the index of this customers chair
            chair = self.waiting_customer_chair(id_)
            # just return if the customer is no longer occupying a chair
            if chair is None:
                return
            self.draw_timer(self.timer_coords['waiter'][chair], color, text=time_)
            self.draw_waiter(chair, color, text=id_)
        else:
            print(event)

    def waiting_customer_chair(self, id_):
        """ Returns the index of the waiting room chair for a given customer id

            :param id_: Customer ID
            :returns: Waiting room chair for requested customer
            :returns: None if customer is not waiting
        """
        for w in range(self.num_waiters):
            if self.waiting_chairs[w] == id_:
                return w
        return None

    def next_waiting_chair(self):
        """ Function to return the next available waiting room chair.
            Will increment the current index modulo the total number of chairs.

            :returns: index of waiting room chair
        """
        self.next_waiting_chair_ = (self.next_waiting_chair_ + 1) % self.num_waiters
        return self.next_waiting_chair_

    def barber_start(self, event):
        pass

    def barber_stop(self, event):
        pass

    def customer_enter(self, event):
        pass

    def finish_cutting(self, event):
        pass

    def barber_state_startup(self, event):
        pass

    def barber_state_cutting(self, event):
        self.draw_barber(event['user.id'], self.config['cutting.color'])

    def barber_state_sleeping(self, event):
        self.draw_barber(event['user.id'], self.config['sleeping.color'])

    def barber_state_finish(self, event):
        self.draw_barber(event['user.id'], self.common['finish.color'])

    def customer_start(self, event):
        pass

    def customer_stop(self, event):
        pass

    def customer_barber_ready(self, event):
        pass

    def customer_finish_cutting(self, event):
        pass

    def customer_state_startup(self, event):
        pass

    def customer_state_haircut(self, event):
        chair = self.waiting_customer_chair(event['user.id'])
        if chair is not None:
            color = self.common['init.color']
            self.draw_timer(self.timer_coords['waiter'][chair], color, text=0)
            self.draw_waiter(chair, color, text=None)

    def customer_state_waiting(self, event):
        self.waiting_chairs[self.next_waiting_chair()] = event['user.id']

    def customer_state_finish(self, event):
        chair = self.waiting_customer_chair(event['user.id'])
        if chair is not None:
            color = self.common['finish.color']
            self.draw_timer(self.timer_coords['waiter'][chair], color, text=0)
            self.draw_waiter(chair, color, text=None)


class GuiConsoleView(mvc.View):
    """ GUI Console View

        Performs console logging as a scrolling text window.

        Logging is used to display MVC state machine events, state transitions and any other
        operational information relevant to the simulation.

        Example::

            [...]
            23:16:23:470859 [Waiter] 6 IN
            23:16:25:477872 [SM] philosopher2 Events.EvHungry [States.Thinking] Events.EvHungry
            23:16:25:478875 [SM] philosopher2 Events.EvHungry [States.Thinking]
            23:16:25:481884 [SM] philosopher2 Events.EvHungry [States.Hungry] States.Hungry
            23:16:25:496323 [SM] philosopher2 Events.EvHungry [States.Hungry]
            23:16:25:498651 [Waiter] 2 IN
            23:16:28:425131 [philosophers] 20 LOOPS
            [...]

    """

    def __init__(self, name, widget):
        super().__init__(name='%s_console' % name)
        self.widget = widget

    def update(self, event):
        # don't log timer tick events to the console
        if event['event'] == mvc.Event.Events.TIMER:
            return
        ts = event['datetime'].strftime('%H:%M:%S:%f')
        if event['class'].lower() == 'waiter':
            msg = '{} [{}] {} {}'.format(ts, event['class'], event['data'], event['event'].name)
        elif event['event'] == mvc.Event.Events.LOOPS:
            if event['data'] % 10 != 0:
                return
            msg = '{} [{}] {} {}'.format(ts, event['class'], event['data'], event['event'].name)
        else:
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
        'animation': {'width': 360, 'height': 360},
        'animation.stick': N,
        'buttons.stick': N,
        'console': {'width': 40, 'height': 10},
        'console.stick': (N, S, E, W),
        'console.label.stick': N,
        'console.frame.stick': (N, S, E, W),
        'ani.frame.stick': (N, S, E, W),
        'label.stick': N,
        'wall.thickness': 5,
        'wall.color': 'lightgray',

        'timer.radius': 15,

        'init.color': ['grey', 'white'],
        'start.color': ['lightgrey', 'yellow'],
        'stop.color': ['lightgrey', 'red'],
        'finish.color': ['lightgrey', 'white'],
        'timer.color': ['lightgrey', 'yellow'],
    }

    philosophers_config = {
        'title': 'Dining Philosophers Simulation',
        'model': 'Philosophers',
        'column': 0,
        'animation.text': 'The Dining Room',
        'console.text': 'Hello, Dining Philosophers',
        'event.class': 'Philosophers',
        'philosophers': None,

        'hungry.color': ['red', 'yellow'],
        'eating.color': ['green', 'white'],
        'thinking.color': ['blue', 'white'],

        'fork.radius': 10,
        'fork.color': 'green',
        'table.radius': 75,
        'table.color': 'grey',
        'chair.radius': 20,
        'waiter.chair.radius': 25,
        'waiter.color': 'blue',
    }

    barbers_config = {
        'title': 'Sleeping Barber(s) Simulation',
        'model': 'Barbers',
        'column': 1,
        'animation.text': 'The Barber Shop',
        'console.text': 'Hello, Sleeping Barber(s)',
        'event.class': 'Barbers',
        'barbers': None,
        'waiters': None,
        'barber.chair.radius': 20,
        'waiter.chair.radius': 20,
        'gap.multiplier': 5,
        'timer.radius': 15,

        'cutting.color': ['green', 'white'],
        'sleeping.color': ['blue', 'white'],
        'waiting.color': ['red', 'white'],
    }

    def __init__(self):
        super().__init__(name='gui', target=self.run)
        self.root = None
        self.mainframe = None
        self.gui_thread = None
        self.ani_barbers = None
        self.ani_dining = None
        self.model_config = None

        # create an event lookup table of all registered events
        # we will use this to lookup screen for events we want to process
        self.events = mvc.Event()

        # scan for StateMachine events
        self.sm_events = {}
        for sme_ in smEvent.SmEvents:
            event = self.events.lookup_event('SM', sme_)
            if event is None:
                raise Exception('SM Event not found : {}'.format(sme_))
            self.sm_events[sme_] = event

        # scan for Waiter events
        self.waiter_events = {}
        for class_ in self.events.events.keys():
            for event_ in self.events.events[class_].keys():
                event__ = self.events.events[class_][event_]
                if event__['class'].lower() == 'waiter':
                    self.waiter_events[event__['event']] = event__

    def update(self, event):
        """ Called to let us know of an event

            :param event: Event that occurred, we should do some kind of update
        """
        if event['class'].lower() == 'philosophers':
            self.update_philosophers(event)
        elif event['class'].lower() == 'barbers':
            self.update_barbers(event)
        elif event['class'].lower() == 'waiter':
            self.ani_dining.update(event)
        elif event['class'].lower() == 'mvc':
            self.update_gui('mvc', event)
        elif event['class'].lower() == 'sm':
            pass
        else:
            print(event)

    def update_philosophers(self, event):
        if event['type'] == 'view' or event['type'] == '*':
            self.models['Philosophers'].update(event)
        if event['type'] == 'model' or event['type'] == '*':
            if event['event'] == mvc.Event.Events.LOOPS:
                self.ani_dining.draw_counter(event['data'])
            elif event['event'] == mvc.Event.Events.ALLSTOPPED:
                pass
            elif event['event'] == mvc.Event.Events.STATISTICS:
                pass
            elif event['event'] == mvc.Event.Events.JOINING:
                pass
            else:
                print(event)

    def update_barbers(self, event):
        if event['type'] == 'view' or event['type'] == '*':
            self.models['Barbers'].update(event)
        if event['type'] == 'model' or event['type'] == '*':
            if event['event'] == mvc.Event.Events.LOOPS:
                self.ani_barbers.draw_counter(event['data'])
            elif event['event'] == mvc.Event.Events.ALLSTOPPED:
                pass
            elif event['event'] == mvc.Event.Events.STATISTICS:
                pass
            elif event['event'] == mvc.Event.Events.JOINING:
                pass
            else:
                print(event)

    @staticmethod
    def update_gui(gui, event):
        print(gui, event)

    def update_dining_console(self, event):
        pass

    def run(self):
        # wait for models to register with
        while len(self.models) is 0:
            time.sleep(0.010)

        # wait until we are running:
        while not self.running:
            time.sleep(Defines.Times.Starting)

        # start the GUI thread
        self.gui_thread = threading.Thread(target=self.tk_run, name='tk_gui')
        self.gui_thread.start()

        # loop until no longer running
        while self.running:
            time.sleep(Defines.Times.Running)

        # stop the GUI
        self.gui_thread.join(timeout=Defines.Times.Stopping)

    @staticmethod
    def write(text):
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

        # fill in some model configuration items
        self.model_config = {
            'philosophers': self.models['Philosophers'].config,
            'barbers': self.models['Barbers'].config
        }
        self.philosophers_config['philosophers'] = self.model_config['philosophers'].get_philosophers()
        self.barbers_config['barbers'] = self.model_config['barbers'].get_barbers()
        self.barbers_config['waiters'] = self.model_config['barbers'].get_waiters()

        # instantiate our GUI animation views
        self.ani_dining = DiningPhilosophers(parent=self, root=self.root, mainframe=self.mainframe,
                                             config=self.philosophers_config, common=self.common_config)
        dining_gui_console = GuiConsoleView('philosophers', self.ani_dining)

        self.ani_barbers = SleepingBarbers(parent=self, root=self.root, mainframe=self.mainframe,
                                           config=self.barbers_config, common=self.common_config)
        barbers_gui_console = GuiConsoleView('barbers', self.ani_barbers)

        # register our animation views
        if self.philosophers_config['model'] in self.models:
            self.models[self.philosophers_config['model']].register(self.ani_dining)
        if self.barbers_config['model'] in self.models:
            self.models[self.barbers_config['model']].register(self.ani_barbers)

        # register our console views
        if self.philosophers_config['model'] in self.models:
            self.models[self.philosophers_config['model']].register(dining_gui_console)
        if self.barbers_config['model'] in self.models:
            self.models[self.barbers_config['model']].register(barbers_gui_console)

        # register models with the animation views
        if self.philosophers_config['model'] in self.models:
            self.ani_dining.register(self.models[self.philosophers_config['model']])
        if self.barbers_config['model'] in self.models:
            self.ani_barbers.register(self.models[self.barbers_config['model']])

        # all setup so run
        self.root.mainloop()
