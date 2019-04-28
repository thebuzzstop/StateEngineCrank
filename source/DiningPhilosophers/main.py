""" DiningPhilosophers

* DiningPhilosophers state machine UML, tables and user state functions
* Contains auto-generated and user created custom code.

* ToDo - Add support for 'FinalState'

**DiningPhilosophers UML**::

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
from threading import Lock
import time
from typing import List

# Project imports
from StateEngineCrank.modules.PyState import StateMachine
import mvc
import exceptions

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
    Eat_Min = 10            #: minimum number of seconds to eat
    Eat_Max = 30            #: maximum number of seconds to eat
    Think_Min = 10          #: minimum number of seconds to think
    Think_Max = 30          #: maximum number of seconds to think
    Philosophers = 9        #: number of philosophers dining
    Dining_Loops = 500      #: number of main loops for dining


class ForkStatus(Enum):
    Free = 0            #: Fork is free for use
    InUse = 1           #: Fork is currently in use by a philosopher


class ForkId(Enum):
    Left = 0
    Right = 1


class Waiter(mvc.Model):
    """ Waiter class used to provide synchronization between philosophers wanting to eat """

    class WaiterEvents(Enum):
        STARTING, RUNNING, IN, ACQUIRE, LEFTFORK, RIGHTFORK, OUT, RELEASE, STOPPING = range(9)

    def __init__(self):
        mvc.Model.__init__(self, name='Waiter')
        self.lock = Lock()          #: Lock to be acquired when accessing the *Waiter*
        self.id_ = None             #: last philosopher ID to make a request
        self.mvc = mvc.Event()      #: mvc Event registry
        self.mvc.register_class(class_name=self.name)
        self.mvc.register_event(self.name, Waiter.WaiterEvents.STARTING, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.RUNNING, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.IN, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.ACQUIRE, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.LEFTFORK, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.RIGHTFORK, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.OUT, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.RELEASE, 'Model')
        self.mvc.register_event(self.name, Waiter.WaiterEvents.STOPPING, 'Model')

        #: Forks - 1 for each philosophers, initialized 'free'
        self.forks = [ForkStatus.Free for _ in range(Config.Philosophers)]  # type: List[ForkStatus]

    def update(self, event):
        """ Called by views to alert us to an update - we ignore it """
        pass

    def run(self):
        # see if we are not running yet
        self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.STARTING])
        if not self.running:
            while not self.running:
                time.sleep(1)
        # run until we aren't then exit
        self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.RUNNING])
        while self.running:
            time.sleep(1)
        self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.STOPPING])

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
        self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.IN], data=philosopher_id)

        # loop until we successfully get both forks
        got_forks = False
        while not got_forks:
            # wait until both forks are free
            while self.forks[left_fork] is ForkStatus.InUse or self.forks[right_fork] is ForkStatus.InUse:
                time.sleep(1)
            # acquire the waiters lock
            if not self.lock.acquire(blocking=False):
                continue
            # we have the waiters lock, see if both forks are still free
            if self.forks[left_fork] is ForkStatus.Free or self.forks[right_fork] is ForkStatus.Free:
                # we have the waiters attention and both forks are free
                got_forks = True
                self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.LEFTFORK], data=philosopher_id)
                self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.RIGHTFORK], data=philosopher_id)
                self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.OUT], data=philosopher_id)
            else:
                # both forks are not free, release the lock and try again
                self.lock.release()
                continue
            time.sleep(1)

    def thank_you(self, philosopher_id):
        """ Philosopher thank you to the waiter

            We use this opportunity to release the Waiter lock
        """
        self.notify(self.mvc.events[self.name][Waiter.WaiterEvents.RELEASE], data=philosopher_id)
        self.lock.release()


#: Waiter who grants requests for access to forks
waiter = Waiter()


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


class UserCode(StateMachine, mvc.Model):

    def __init__(self, user_id=None):
        """ UserCode Constructor

            :param user_id: unique identifier for this User
        """
        name = 'philosopher%s' % user_id
        mvc.Model.__init__(self, name)
        StateMachine.__init__(self, sm_id=user_id, name=name, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)
        self.events_counter = 0     #: counter for tracking events
        self.eating_seconds = 0     #: number of seconds spent eating
        self.thinking_seconds = 0   #: number of seconds spent thinking
        self.hungry_seconds = 0     #: number of seconds spent hungry
        self.event_timer = 0        #: timer used to time eating & thinking

        self.initial_state = None   #: starting state for a philosopher
        if random.randint(0, 1) == 0:
            self.initial_state = States.Thinking
        else:
            self.initial_state = States.Hungry

        self.left_fork = self.id     #: left fork id for this philosopher
        self.right_fork = (self.id + 1) % Config.Philosophers    #: right fork id for this philosopher

    # ===========================================================================
    # noinspection PyPep8Naming
    def StartUp_StartUp(self):
        """ State machine enter function processing for the *StartUp* state.

            Called when the *StartUp* state is entered.
        """
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
        if self.event_timer == 0:
            self.event(Events.EvFull)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eating_PutDownForks(self):
        """ State machine *exit* function processing for the *Eating* state.

            Called when the *Eating* state is exited.
        """
        waiter.forks[self.left_fork] = ForkStatus.Free
        waiter.forks[self.right_fork] = ForkStatus.Free

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eating_StartEatingTimer(self):
        """ State machine enter function processing for the *Eating* state.

            Called when the *Eating* state is entered.
        """
        self.event_timer = seconds(Config.Eat_Min, Config.Eat_Max)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Hungry_AskPermission(self):
        """ State machine *Enter* function processing for the *Hungry* state.

            Called when the *Hungry* state is entered.
        """
        tstart = time.time()
        waiter.request(self.id, self.left_fork, self.right_fork)
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
        waiter.forks[self.left_fork] = ForkStatus.InUse
        waiter.forks[self.right_fork] = ForkStatus.InUse
        # thanking the waiter releases the Waiter's lock
        waiter.thank_you(self.id)

    # =========================================================
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def ThankWaiter(self):
        """ State machine state transition processing for *ThankWaiter*.

            Called when the state transition *ThankWaiter* is taken.
            Thanking the waiter releases the Waiter's lock.
        """
        waiter.thank_you(self.id)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Thinking_StartThinkingTimer(self):
        """ State machine *enter* function processing for the *Thinking* state.

            Called when the *Thinking* state is entered.
        """
        self.event_timer = seconds(Config.Think_Min, Config.Think_Max)

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
        if self.event_timer == 0:
            self.event(Events.EvHungry)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Think(self):
        """ Guard function used to determine if a Philosophers initial state is *Thinking*

            :returns: True : Philosopher's initial state is *Thinking*
            :returns: False : Philosopher's initial state is NOT *Thinking*
        """
        return self.initial_state is States.Thinking

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eat(self):
        """ Guard function used to determine if a Philosophers initial state is *Eating*

            :returns: True : Philosopher's initial state is *Eating*
            :returns: False : Philosopher's initial state is NOT *Eating*
        """
        return self.initial_state is States.Hungry

    # ===========================================================================
    # noinspection PyPep8Naming
    def Finish_NotRunning(self):
        """
        @brief Enter function processing for *Finish* state.

        @details State machine enter function processing for the *Finish* state.
        This function is called when the *Finish* state is entered.
        """
        self.running = False

    # ===========================================================================
    # noinspection PyPep8Naming
    def Finish_Wait(self):
        """
        @brief *Do* function processing for the *Finish* state

        @details State machine *do* function processing for the *Finish* state.
        This function is called once every state machine iteration to perform processing
        for the *Finish* state.
        """
        time.sleep(1)

    # =========================================================
    # noinspection PyPep8Naming
    def Restart(self):
        """
        @brief State transition processing for *Restart*

        @details State machine state transition processing for *Restart*.
        This function is called whenever the state transition *Restart* is taken.

        @todo Add any reset/initialization processes here prior to restarting
        """
        return

    # =========================================================
    # noinspection PyPep8Naming
    def Shutdown(self):
        """
        @brief State transition processing for *Shutdown*

        @details State machine state transition processing for *Shutdown*.
        This function is called whenever the state transition *Shutdown* is taken.

        @todo Add any processes here prior to exiting the program.
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

    def __init__(self, philosopher_id=None):
        """ Philosopher Constructor - Extends the UserCode base class

            :param philosopher_id: ID unique to this Philosopher
        """
        UserCode.__init__(self, user_id=philosopher_id)
        self.exit_code = 0          #: exit code returned by this philosopher
        self.running = False        #: True, simulation is running
        self.has_forks = False      #: True, philosopher has possession of both forks

    def update(self, event):
        """ Called by View to alert us to an event - we ignore """
        pass


class DiningPhilosophers(mvc.Model):
    """ Main DiningPhilosophers Class """

    def __init__(self, exit_when_done=None):
        super().__init__(name='philosophers', target=self.run)

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

        #: register philosopher statemachine events
        for e in Events:
            self.mvc_events.register_event(class_name=self.name, event=e, event_type='model',
                                           text='%s[%s][%s]' % (self.name, e.name, e.value), data=e.value)

        #: The dining philosophers
        self.philosophers = []  # type: List[Philosopher]

        # Instantiate and initialize all philosophers
        for id_ in range(Config.Philosophers):
            philosopher = Philosopher(philosopher_id=id_)
            self.philosophers.append(philosopher)
            self.mvc_events.register_actor(class_name=self.name, actor_name=philosopher.name)

    def register(self, view):
        self.views[view.name] = view
        for p in self.philosophers:
            p.register(view)
        waiter.register(view)

    def update(self, event):
        """ Called by Views and/or Controller to alert us to an event. """
        if event['class'] is not self.name:
            raise Exception('Dining: Unknown event type')

        # process event received
        if event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.START]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.running = True
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STEP]['event']:
            self.logger('[{}]: {} [unhandled]'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STOP]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
            self.running = False
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.PAUSE]['event']:
            self.logger('[{}]: {} [unhandled]'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.RESUME]['event']:
            self.logger('[{}]: {} [unhandled]'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.ALLSTOPPED]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.ITERATIONS]['event']:
            self.logger('[{}]: {}'.format(event['class'], event['text']))
        elif event['event'] is self.mvc_events.events[self.name][mvc.Event.Events.LOGGER]['event']:
            self.logger('Event: %s / %s' % (event['text'], event['data']))
        else:
            raise Exception('Unhandled event')

    def forks(self, philosopher_id):
        left = self.philosophers[philosopher_id].left_fork
        right = self.philosophers[philosopher_id].right_fork
        return left, right

    def run(self):
        """ DiningPhilosophers Main program

            Implemented as a function so as to be callable from an outside
            entity when running in concert with other applications.

            Also runnable as a standalone application.
        """
        done = False
        while not done:
            # Wait for simulation to start running
            while not self.running:
                time.sleep(1.0)

            # Philosophers have been instantiated and threads created
            # Start the simulation, i.e. start all philosophers eating
            for p in self.philosophers:
                p.running = True
                p.post_event(Events.EvStart)

            # Wait for the simulation to complete
            for loop in range(Config.Dining_Loops):
                time.sleep(1)
                loop += 1
                if loop % 10 is 0:
                    self.notify(self.mvc_events.events[self.name][mvc.Event.Events.ITERATIONS],
                                text='Iterations: %s' % loop)
                if self.running is False:
                    break

            # Tell philosophers to stop
            for p in self.philosophers:
                p.post_event(Events.EvStop)

            # Joining threads
            for p in self.philosophers:
                p.join()
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.ALLSTOPPED])

            # Print some statistics of the simulation
            text = 'Statistics:'
            for p in self.philosophers:
                t = p.thinking_seconds
                e = p.eating_seconds
                h = int(p.hungry_seconds + 0.5)
                total = t + e + h
                text = text + \
                       '\n   Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (p.id, t, e, h, total)
            self.notify(self.mvc_events.events[self.name][mvc.Event.Events.STATISTICS], text=text+'\n')

            # shutdown behavior
            if self.exit_when_done:
                self.set_stopping()
                done = True
            else:
                self.running = False


if __name__ == '__main__':
    """ Execute main code if run from the command line """

    dining_philosophers = DiningPhilosophers()
    dining_philosophers.start()
    dining_philosophers.set_running()
    while dining_philosophers.running:
        time.sleep(1)
    print('Done')
