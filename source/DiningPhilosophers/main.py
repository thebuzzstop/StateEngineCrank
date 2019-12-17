""" DiningPhilosophers.main

The DiningPhilosophers main module implements the Dining Philosophers Simulation
state machine.

The main module contains:

* State machine UML, tables and user state functions
* Auto-generated and user created custom code.

* ToDo - Add support for 'FinalState'

.. code-block:: rest
    :caption: **Dining Philosophers UML**
    :name: DiningPhilosophersUml

    @startuml

    [*] --> StartUp

    StartUp --> Thinking : EvStart
    StartUp --> Finish : EvStop
    StartUp : enter : StartUp

    Thinking --> Hungry : EvHungry
    Thinking --> Finish : EvStop
    Thinking : enter : StartThinkingTimer
    Thinking : do    : Think

    Hungry --> Eating : EvHavePermission / PickUpForks
    Hungry --> Finish : EvStop / ThankWaiter
    Hungry : enter : AskPermission

    Eating --> Thinking : EvFull
    Eating --> Finish : EvStop
    Eating : enter : StartEatingTimer
    Eating : do    : Eat
    Eating : exit  : PutDownForks

    Finish --> StartUp : EvRestart / Restart
    Finish --> [*] : EvExit / Shutdown
    Finish : enter : NotRunning
    Finish : do : Wait

    @enduml
"""

# System imports
from enum import Enum
import random
import threading
import time
from typing import List

# Project imports
from StateEngineCrank.modules.PyState import StateMachine
import mvc
import exceptions
import Defines


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    Thinking = 2
    Finish = 3
    Hungry = 4
    Eating = 5
    FinalState = 6


class Events(Enum):
    EvStart = 1
    EvStop = 2
    EvHungry = 3
    EvHavePermission = 4
    EvFull = 5
    EvRestart = 6
    EvExit = 7


class StateTables(object):
    state_transition_table = {}
    state_function_table = {}

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = END = DO NOT MODIFY =========
# ==============================================================================


class Config(object):
    Eat_Min = 5                         #: minimum number of seconds to eat
    Eat_Max = 10                        #: maximum number of seconds to eat
    Think_Min = 5                       #: minimum number of seconds to think
    Think_Max = 10                      #: maximum number of seconds to think
    Philosophers = 7                    #: number of philosophers dining
    Dining_Loops = 100                  #: number of main loops for dining
    Class_Name = 'philosophers'         #: class name for Event registration
    Actor_Base_Name = 'philosopher'     #: used when identifying actors


class ConfigData(Borg):

    def __init__(self):
        Borg.__init__(self)
        if self._shared_state:
            return
        self.eat_max = Config.Eat_Max
        self.eat_min = Config.Eat_Min
        self.think_min = Config.Think_Min
        self.think_max = Config.Think_Max
        self.philosophers = Config.Philosophers
        self.dining_loops = Config.Dining_Loops
        self.class_name = Config.Class_Name
        self.actor_base_name = Config.Actor_Base_Name

    def set_eat_max(self, value):
        self.eat_max = value

    def set_eat_min(self, value):
        self.eat_min = value

    def set_think_max(self, value):
        self.think_max = value

    def set_think_min(self, value):
        self.think_min = value

    def set_philosophers(self, value):
        self.philosophers = value

    def set_dining_loops(self, value):
        self.dining_loops = value

    def get_philosophers(self):
        return self.philosophers


class ForkStatus(Enum):
    Free = 0            #: Fork is free for use
    InUse = 1           #: Fork is currently in use by a philosopher


class ForkId(Enum):
    Left = 0
    Right = 1


class WaiterEvents(Enum):
    STARTING, RUNNING, IN, ACQUIRE, LEFTFORK, RIGHTFORK, OUT, RELEASE, STOPPING = range(9)


class Waiter(mvc.Model, Borg):
    """ Waiter class used to provide synchronization between philosophers wanting to eat.
        Implemented as a Borg so all diners will be referencing the same waiter.
    """

    def __init__(self):
        Borg.__init__(self)
        # see if we have called mvc.Model.__init__()
        if hasattr(self, 'views'):
            return
        mvc.Model.__init__(self, name='Waiter')
        self.config = ConfigData()      #: simulation configuration data
        self.lock = threading.Lock()    #: Lock to be acquired when accessing the *Waiter*
        self.id_ = None                 #: last philosopher ID to make a request
        self.mvc = mvc.Event()          #: mvc Event registry
        self.mvc.register_class(class_name=self.name)
        self.mvc.register_actor(class_name='mvc', actor_name=self.name)
        self.mvc.register_event(self.name, mvc.Event.Events.TIMER, '*')
        self.mvc.register_event(self.name, WaiterEvents.STARTING, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.RUNNING, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.IN, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.ACQUIRE, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.LEFTFORK, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.RIGHTFORK, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.OUT, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.RELEASE, 'Model')
        self.mvc.register_event(self.name, WaiterEvents.STOPPING, 'Model')

        #: Forks - 1 for each philosophers, initialized 'free'
        self.forks = [ForkStatus.Free for _ in range(self.config.philosophers)]  # type: List[ForkStatus]
        self.hungry_timers = [0 for _ in range(self.config.philosophers)]

    def run(self):
        """ Dummy function to satisfy MVC.Model need for a run() function """
        pass

    def update(self, event):
        """ Called by views to alert us to an update - we ignore it """
        pass

    def request(self, philosopher_id, left_fork, right_fork):
        """ Function called when a Philosopher wants to eat.

            * The request will block until the waiter is available,
              i.e. not engaged with another Philosopher.
            * The request will block until both Philosopher left and right
              forks are available, at which point the waiter grants permission.
            * The caller is assured that both left and right forks are available
              when this function returns.

            :param philosopher_id: ID of Philosopher making the request
            :param left_fork: ID of left fork required to eat
            :param right_fork: ID of right fork required to eat
        """
        self.id_ = philosopher_id
        self.notify(self.mvc.events[self.name][WaiterEvents.IN], data=philosopher_id)

        # loop until we successfully get both forks
        got_forks = False
        self.hungry_timers[philosopher_id] = 0
        while not got_forks:
            if self.pause:
                time.sleep(Defines.Times.Pausing)
                if not self.step():
                    continue

            # wait until both forks are free
            while self.forks[left_fork] is ForkStatus.InUse or self.forks[right_fork] is ForkStatus.InUse:
                time.sleep(Defines.Times.LoopTime)
                self.hungry_timers[philosopher_id] += 1
                self.notify(self.mvc.post(class_name='mvc', actor_name=self.name, user_id=philosopher_id,
                                          event=mvc.Event.Events.TIMER,
                                          data=[self.hungry_timers[philosopher_id], None]))

            # check if we are paused
            if self.pause:
                continue

            # acquire the waiters lock
            if not self.lock.acquire(blocking=False):
                time.sleep(Defines.Times.LoopTime)
                self.hungry_timers[philosopher_id] += 1
                self.notify(self.mvc.post(class_name='mvc', actor_name=self.name, user_id=philosopher_id,
                                          event=mvc.Event.Events.TIMER,
                                          data=[self.hungry_timers[philosopher_id], None]))
                continue

            # we have the waiters lock, see if both forks are still free
            if self.forks[left_fork] is ForkStatus.Free or self.forks[right_fork] is ForkStatus.Free:
                # we have the waiters attention and both forks are free
                got_forks = True
                self.notify(self.mvc.events[self.name][WaiterEvents.LEFTFORK], data=philosopher_id)
                self.notify(self.mvc.events[self.name][WaiterEvents.RIGHTFORK], data=philosopher_id)
                self.notify(self.mvc.events[self.name][WaiterEvents.OUT], data=philosopher_id)
            else:
                # both forks are not free, release the lock and try again
                self.lock.release()
                time.sleep(Defines.Times.LoopTime)
                self.hungry_timers[philosopher_id] += 1
                self.notify(self.mvc.post(class_name='mvc', actor_name=self.name, user_id=philosopher_id,
                                          event=mvc.Event.Events.TIMER,
                                          data=[self.hungry_timers[philosopher_id], None]))

    def thank_you(self, philosopher_id):
        """ Philosopher thank you to the waiter

            We use this opportunity to release the Waiter lock

            :param philosopher_id: ID of philosopher saying thank you
        """
        self.notify(self.mvc.events[self.name][WaiterEvents.RELEASE], data=philosopher_id)
        self.lock.release()


def seconds(minimum, maximum):
    """ Function to return a random integer between 'minimum' and 'maximum'.

        Used as the number of seconds to either 'eat' or 'think'.

        :param minimum: number of seconds to either eat or think
        :param maximum: number of seconds to either eat or think
        :returns: random number between *minimum* and *maximum*
    """
    return random.randint(minimum, maximum)

# ==============================================================================
# ===== USER STATE CODE = BEGIN ================================================
# ==============================================================================


class UserCode(StateMachine):
    """ UserCode class implements the user specific state machine code.

        Skeletons for all user functions which are named in the state machine defining UML are automatically
        created by *The Crank*. User functions are state machine *enter(), do(), exit()* and *transition()* functions.
        The skeletons must be filled in with any custom code required to implement the desired functionality.
        The skeletons are only generated if they are determined to be missing. In other words, all user code is
        preserved over multiple runs of *The Crank*.
    """

    def cleanup(self):
        StateMachine.cleanup(self)

    def __init__(self, user_id=None, **kwargs):
        """ UserCode Class Constructor

            :param user_id: unique identifier for this User
        """
        self.config = ConfigData()  #: simulation configuration data
        name = '{}{}'.format(self.config.actor_base_name, user_id)
        StateMachine.__init__(self, sm_id=user_id, name=name,
                              startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table,
                              **kwargs)

        self.events_counter = 0     #: counter for tracking events
        self.eating_seconds = 0     #: number of seconds spent eating
        self.thinking_seconds = 0   #: number of seconds spent thinking
        self.hungry_seconds = 0     #: number of seconds spent hungry
        self.event_timer = 0        #: timer used to time eating & thinking

        self.waiter = Waiter()      #: the waiter
        self.left_fork = self.id    #: left fork id for this philosopher
        self.right_fork = (self.id + 1) % self.config.philosophers    #: right fork id for this philosopher

        self.mvc_events.register_actor(class_name=self.config.class_name, actor_name=self.name)

    # ===========================================================================
    # noinspection PyPep8Naming
    def StartUp_StartUp(self):
        """ State machine enter function processing for the *StartUp* state.

            Called when the *StartUp* state is entered.
        """
        self.logger('Startup')
        self.event(Events.EvStart)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eating_Eat(self):
        """ State machine *do* function processing for the *Eating* state.

            Called once every state machine iteration to perform processing
            for the *Eating* state.
        """
        time.sleep(1)
        self.eating_seconds += 1
        self.event_timer -= 1
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.event_timer, self.current_state]))
        if self.event_timer == 0:
            self.event(Events.EvFull)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eating_PutDownForks(self):
        """ State machine *exit* function processing for the *Eating* state.

            Called when the *Eating* state is exited.
        """
        self.logger('Done Eating')
        self.waiter.forks[self.left_fork] = ForkStatus.Free
        self.waiter.forks[self.right_fork] = ForkStatus.Free

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eating_StartEatingTimer(self):
        """ State machine enter function processing for the *Eating* state.

            Called when the *Eating* state is entered.
        """
        self.logger('Start Eating')
        self.event_timer = seconds(self.config.eat_min, self.config.eat_max)
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.event_timer, self.current_state]))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Hungry_AskPermission(self):
        """ State machine *Enter* function processing for the *Hungry* state.

            Called when the *Hungry* state is entered.
        """
        self.logger('Hungry/AskPermission')
        tstart = time.time()
        self.waiter.request(self.id, self.left_fork, self.right_fork)
        tend = time.time()
        thungry = tend-tstart
        self.hungry_seconds += thungry
        self.event(Events.EvHavePermission)

    # =========================================================
    # noinspection PyPep8Naming
    def PickUpForks(self):
        """ State machine state transition processing for *PickUpForks*.

            Called when the state transition *PickUpForks* is taken.
        """
        self.logger('Pickup Forks')
        self.waiter.forks[self.left_fork] = ForkStatus.InUse
        self.waiter.forks[self.right_fork] = ForkStatus.InUse
        # thanking the waiter releases the Waiter's lock
        self.waiter.thank_you(self.id)

    # =========================================================
    # noinspection PyPep8Naming
    def ThankWaiter(self):
        """ State machine state transition processing for *ThankWaiter*.

            Called when the state transition *ThankWaiter* is taken.
            Thanking the waiter releases the Waiter's lock.
        """
        self.logger('Thank Waiter')
        self.waiter.thank_you(self.id)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Thinking_StartThinkingTimer(self):
        """ State machine *enter* function processing for the *Thinking* state.

            Called when the *Thinking* state is entered.
        """
        self.event_timer = seconds(self.config.think_min, self.config.think_max)
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.event_timer, self.current_state]))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Thinking_Think(self):
        """ State machine *do* function processing for the *Thinking* state.

            Called once every state machine iteration to perform
            processing for the *Thinking* state.
        """
        time.sleep(1)
        self.thinking_seconds += 1
        self.event_timer -= 1
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.event_timer, self.current_state]))
        if self.event_timer == 0:
            self.event(Events.EvHungry)
            self.logger('Hungry')

    # ===========================================================================
    # noinspection PyPep8Naming
    def Finish_NotRunning(self):
        """ *Enter* function processing for *Finish* state.

        State machine *enter* function processing for the *Finish* state.
        This function is called when the *Finish* state is entered.
        """
        self.running = False

    # ===========================================================================
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def Finish_Wait(self):
        """ *Do* function processing for the *Finish* state

        State machine *do* function processing for the *Finish* state.
        This function is called once every state machine iteration to perform processing
        for the *Finish* state.
        """
        time.sleep(1)

    # =========================================================
    # noinspection PyPep8Naming
    def Restart(self):
        """ State transition processing for *Restart*

        State machine state transition processing for *Restart*.
        This function is called whenever the state transition *Restart* is taken.

        :todo: Add any reset/initialization processes here prior to restarting
        """
        return

    # =========================================================
    # noinspection PyPep8Naming
    def Shutdown(self):
        """ State transition processing for *Shutdown*

        State machine state transition processing for *Shutdown*.
        This function is called whenever the state transition *Shutdown* is taken.

        :todo: Add any processes here prior to exiting the program.
        """
        return

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: {'state2': States.Thinking, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Thinking] = {
    Events.EvHungry: {'state2': States.Hungry, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Finish] = {
    Events.EvRestart: {'state2': States.StartUp, 'guard': None, 'transition': UserCode.Restart},
    Events.EvExit: {'state2': States.FinalState, 'guard': None, 'transition': UserCode.Shutdown},
}

StateTables.state_transition_table[States.Hungry] = {
    Events.EvHavePermission: {'state2': States.Eating, 'guard': None, 'transition': UserCode.PickUpForks},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': UserCode.ThankWaiter},
}

StateTables.state_transition_table[States.Eating] = {
    Events.EvFull: {'state2': States.Thinking, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_StartUp, 'do': None, 'exit': None}

StateTables.state_function_table[States.Thinking] = \
    {'enter': UserCode.Thinking_StartThinkingTimer, 'do': UserCode.Thinking_Think, 'exit': None}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_NotRunning, 'do': UserCode.Finish_Wait, 'exit': None}

StateTables.state_function_table[States.Hungry] = \
    {'enter': UserCode.Hungry_AskPermission, 'do': None, 'exit': None}

StateTables.state_function_table[States.Eating] = \
    {'enter': UserCode.Eating_StartEatingTimer, 'do': UserCode.Eating_Eat, 'exit': UserCode.Eating_PutDownForks}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================


class Philosopher(UserCode):
    """ Philosophers extends the UserCode base class """

    def cleanup(self):
        UserCode.cleanup(self)

    def __init__(self, philosopher_id=None):
        """ Philosopher Class Constructor - Extends the UserCode base class

            :param philosopher_id: ID unique to this Philosopher
        """
        UserCode.__init__(self, user_id=philosopher_id, target=self.run)
        self.exit_code = 0          #: exit code returned by this philosopher
        self.has_forks = False      #: True, philosopher has possession of both forks

    def update(self, event):
        """ Called by View to alert us to an event - we ignore """
        pass


class DiningPhilosophers(mvc.Model):
    """ Main DiningPhilosophers Class """

    def __init__(self, exit_when_done=None):
        """ DiningPhilosophers Class Constructor

            :param exit_when_done: True, then exit when done. False, run until program exit requested.
        """
        super().__init__(name='Philosophers', thread=threading.Thread(name='Philosophers', target=self.run))

        #: simulation configuration data
        self.config = ConfigData()

        # determine our exit criteria
        if exit_when_done is not None:
            self.exit_when_done = exit_when_done
        else:
            self.exit_when_done = True

        #: event processing
        self.mvc_events = mvc.Event()
        try:
            self.mvc_events.register_class(self.name)
        except exceptions.ClassAlreadyRegistered:
            pass

        #: register mvc model events
        self.mvc_model_events = [
            mvc.Event.Events.LOOPS,
            mvc.Event.Events.STATISTICS,
            mvc.Event.Events.ALLSTOPPED,
            mvc.Event.Events.JOINING,
            mvc.Event.Events.LOGGER
        ]
        for event_ in self.mvc_model_events:
            self.mvc_events.register_event(self.name, event=event_, event_type='model', text=event_.name)

        #: register philosopher statemachine events
        for e in Events:
            self.mvc_events.register_event(class_name=self.name, event=e, event_type='model',
                                           text='%s[%s][%s]' % (self.name, e.name, e.value), data=e.value)
        #: The dining philosophers
        self.philosophers = []  # type: List[Philosopher]

        #: The waiter
        self.waiter = Waiter()

    def create_philosophers(self, first_time):
        """ Create philosophers

            Called to create the philosophers (actors).
            If this is not the first time then any existing philosophers will be unregistered
            so that they can be recreated.

            :todo: Revisit the **first_time** issue for a more structured solution.

            :param first_time: True if first time
        """
        if not first_time:
            # unregister philosopher actors so that they can be recreated
            for p in self.philosophers:
                self.mvc_events.unregister_actor(p.name)
            # now delete our instantiations
            del self.philosophers
            self.philosophers = []
            self.running = False

        for id_ in range(self.config.philosophers):
            philosopher = Philosopher(philosopher_id=id_)
            self.philosophers.append(philosopher)
            for vk in self.views.keys():
                philosopher.register(self.views[vk])

    def register(self, view):
        """ Register all simulation actors with the specified view.

            The View may be anything which can respond to view type events.
            [e.g. console, logger, GUI, etc.]

            :param view: View to register with.
        """
        self.views[view.name] = view
        for p in self.philosophers:
            p.register(view)
        self.waiter.register(view)

    def update(self, event):
        """ Called by Views and/or Controller to alert us to an event.

            We only know how to process which are in our *class*.
            Receipt of an event not in our *class* will raise an exception.

            :param event: Event to process
            :raises: Unknown event type, Unhandled event
        """
        if event['class'] != self.name:
            raise Exception('Dining: Unknown event type')

        # process event received
        if event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.START]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_running()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STEP]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_step()
            for p in self.philosophers:
                p.set_step()
            self.waiter.set_step()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STOP]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_stopping()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.PAUSE]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_pause()
            for p in self.philosophers:
                p.set_pause()
            self.waiter.set_pause()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.RESUME]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.set_resume()
            for p in self.philosophers:
                p.set_resume()
                self.waiter.set_resume()
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.ALLSTOPPED]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.LOOPS]['event']:
            if (event['data'] % 10) == 0:
                self.logger('[{}]: Iteration: {}'.format(event['class'], event['data']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.TIMER]['event']:
            pass
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.LOGGER]['event']:
            self.logger('Event: %s / %s' % (event['text'], event['data']))
        else:
            raise Exception('Unhandled event')

    def forks(self, philosopher_id):
        """ Returns the forks associated with a specific philosopher

            :param philosopher_id: Philosopher ID whose forks are being requested
            :returns: Tuple representing the *left* and *right* forks
        """
        left = self.philosophers[philosopher_id].left_fork
        right = self.philosophers[philosopher_id].right_fork
        return left, right

    def statistics(self):
        """ Calculate philosopher statistics """
        text = 'Statistics:'
        for p in self.philosophers:
            t = p.thinking_seconds
            e = p.eating_seconds
            h = int(p.hungry_seconds + 0.5)
            total = t + e + h
            text = text + \
                   '\n   Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (p.id, t, e, h, total)
        return text

    def run(self):
        """ DiningPhilosophers Main program

            Implemented as a function so as to be callable from an outside
            entity when running in concert with other applications.

            Also runnable as a standalone application.
        """
        done = False
        first_time = True
        while not done:

            # Instantiate and initialize all philosophers
            self.create_philosophers(first_time=first_time)
            first_time = False

            # Wait for simulation to start running
            while not self.running:
                time.sleep(Defines.Times.Starting)

            # Philosophers have been instantiated and threads created
            # Start the simulation, i.e. start all philosophers eating
            for p in self.philosophers:
                p.running = True
                p.post_event(Events.EvStart)

            # Wait for the simulation to complete
            for loop in range(self.config.dining_loops):
                # Sleep for 1 loop iteration time slot
                time.sleep(Defines.Times.LoopTime)
                # Bump loop count and notify
                loop += 1
                self.notify(self.mvc_events.events[self.name][mvc.Event.Events.LOOPS], data=loop)
                # Pause if requested, keep monitoring the running flag
                while self.pause and self.running:
                    time.sleep(Defines.Times.Pausing)
                # Break simulation if not running
                if self.running is False:
                    break

            # Tell philosophers to stop
            for p in self.philosophers:
                p.post_event(Events.EvStop)

            # Joining threads
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.JOINING])
            for p in self.philosophers:
                self.join_thread(p.thread)
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.ALLSTOPPED])

            # Generate some statistics of the simulation
            text = self.statistics()
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS], text=text+'\n')

            # shutdown behavior
            if self.exit_when_done:
                self.set_stopping()
                done = True


if __name__ == '__main__':
    """ Execute main code if run from the command line """

    dining_philosophers = DiningPhilosophers()
    dining_philosophers.start()
    dining_philosophers.set_running()
    while dining_philosophers.running:
        time.sleep(1)

    print('Dining Philosophers Simulation Done')
    print(dining_philosophers.statistics())
