""" DiningPhilosophers

* DiningPhilosophers state machine UML, tables and user state functions
* Contains auto-generated and user created custom code.

**DiningPhilosophers UML**::

    @startuml

    [*] --> StartUp

    StartUp --> Thinking : EvStart [Think]
    StartUp --> Hungry : EvStart [Eat]
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

    Finish : do : Finish

    @enduml
"""

# System imports
from enum import Enum
import random
from threading import Lock
import time
from typing import List

# Project imports
from modules.PyState import StateMachine
import mvc
import gui

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    Thinking = 2
    Hungry = 3
    Finish = 4
    Eating = 5


class Events(Enum):
    EvStart = 1
    EvStop = 2
    EvHungry = 3
    EvHavePermission = 4
    EvFull = 5


class StateTables(object):
    state_transition_table = {}
    state_function_table = {}

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = END = DO NOT MODIFY =========
# ==============================================================================


class Config(object):
    Eat_Min = 15            #: minimum number of seconds to eat
    Eat_Max = 45            #: maximum number of seconds to eat
    Think_Min = 15          #: minimum number of seconds to think
    Think_Max = 45          #: maximum number of seconds to think
    Philosophers = 4        #: number of philosophers dining
    Dining_Loops = 100      #: number of main loops for dining


class ForkStatus(Enum):
    Free = 0            #: Fork is free for use
    InUse = 1           #: Fork is currently in use by a philosopher


class Waiter(mvc.Model):
    """ Waiter class used to provide synchronization between philosophers wanting to eat """

    def __init__(self):
        mvc.Model.__init__(self, name='Waiter')
        self.lock = Lock()      #: Lock to be acquired when accessing the *Waiter*
        self.id_ = None         #: last philosopher ID to make a request

    def update(self, event):
        """ Called by views to alert us to an update - we ignore it """
        pass

    def run(self):
        # see if we are not running yet
        if not self.running:
            while not self.running:
                time.sleep(1)
        # run until we aren't then exit
        while self.running:
            time.sleep(1)

    def request(self, id_, left_fork, right_fork):
        """ Function called when a Philosopher wants to eat.

            * The request will block until the waiter is available,
              i.e. not engaged with another Philosopher.
            * The request will block until both Philosopher left and right
              forks are available, at which point the waiter grants permission.
            * The caller is assured that both left and right forks are available
              when this function returns.

            :param id_: ID of Philosopher making the request
            :param left_fork: ID of left fork required to eat
            :param right_fork: ID of right fork required to eat
        """
        self.id_ = id_
        self.logger('SM[%s] waiter[in]' % id_)
        self.lock.acquire()
        while forks[left_fork] is ForkStatus.InUse:
            time.sleep(0.1)
        while forks[right_fork] is ForkStatus.InUse:
            time.sleep(0.1)
        self.logger('SM[%s] waiter[out]' % id_)

    def thank_you(self):
        """ Philosopher thank you to the waiter

            We use this opportunity to release the Waiter lock
        """
        self.logger('SM[%s] waiter release' % self.id_)
        self.lock.release()


#: Forks - 1 for each philosophers, initialized 'free'
forks = [ForkStatus.Free for _ in range(Config.Philosophers)]  # type: List[ForkStatus]

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
        forks[self.left_fork] = ForkStatus.Free
        forks[self.right_fork] = ForkStatus.Free

    # ===========================================================================
    # noinspection PyPep8Naming
    def Eating_StartEatingTimer(self):
        """ State machine enter function processing for the *Eating* state.

            Called when the *Eating* state is entered.
        """
        self.event_timer = seconds(Config.Eat_Min, Config.Eat_Max)
        self.logger('SM[%s] Eating (%s)' % (self.id, self.event_timer))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Finish_Finish(self):
        """ State machine *do* function processing for the *Finish* state.

            Called once every state machine iteration to perform
            processing for the *Finish* state.
        """
        self.logger('SM[%s] Finished' % self.id)
        self.running = False

    # ===========================================================================
    # noinspection PyPep8Naming
    def Hungry_AskPermission(self):
        """ State machine *Enter* function processing for the *Hungry* state.

            Called when the *Hungry* state is entered.
        """
        self.logger('SM[%s] Hungry!' % self.id)
        tstart = time.time()
        waiter.request(self.id, self.left_fork, self.right_fork)
        tend = time.time()
        thungry = tend-tstart
        self.hungry_seconds += thungry
        self.logger('SM[%s] Hungry (%s)' % (self.id, round(thungry)))
        self.event(Events.EvHavePermission)

    # =========================================================
    # noinspection PyPep8Naming
    def PickUpForks(self):
        """ State machine state transition processing for *PickUpForks*.

            Called when the state transition *PickUpForks* is taken.
        """
        forks[self.left_fork] = ForkStatus.InUse
        forks[self.right_fork] = ForkStatus.InUse
        # thanking the waiter releases the Waiter's lock
        waiter.thank_you()

    # =========================================================
    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def ThankWaiter(self):
        """ State machine state transition processing for *ThankWaiter*.

            Called when the state transition *ThankWaiter* is taken.
            Thanking the waiter releases the Waiter's lock.
        """
        waiter.thank_you()

    # ===========================================================================
    # noinspection PyPep8Naming
    def Thinking_StartThinkingTimer(self):
        """ State machine *enter* function processing for the *Thinking* state.

            Called when the *Thinking* state is entered.
        """
        self.event_timer = seconds(Config.Think_Min, Config.Think_Max)
        self.logger('SM[%s] Thinking (%s)' % (self.id, self.event_timer))

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

    # noinspection PyPep8Naming
    def Think(self):
        """ Guard function used to determine if a Philosophers initial state is *Thinking*

            :returns: True : Philosopher's initial state is *Thinking*
            :returns: False : Philosopher's initial state is NOT *Thinking*
        """
        return self.initial_state is States.Thinking

    # noinspection PyPep8Naming
    def Eat(self):
        """ Guard function used to determine if a Philosophers initial state is *Eating*

            :returns: True : Philosopher's initial state is *Eating*
            :returns: False : Philosopher's initial state is NOT *Eating*
        """
        return self.initial_state is States.Hungry

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: [
        {'state2': States.Thinking, 'guard': UserCode.Think, 'transition': None},
        {'state2': States.Hungry, 'guard': UserCode.Eat, 'transition': None},
    ],
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Thinking] = {
    Events.EvHungry: {'state2': States.Hungry, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Hungry] = {
    Events.EvHavePermission: {'state2': States.Eating, 'guard': None, 'transition': UserCode.PickUpForks},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': UserCode.ThankWaiter},
}

StateTables.state_transition_table[States.Finish] = {
}

StateTables.state_transition_table[States.Eating] = {
    Events.EvFull: {'state2': States.Thinking, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_StartUp, 'do': None, 'exit': None}

StateTables.state_function_table[States.Thinking] = \
    {'enter': UserCode.Thinking_StartThinkingTimer, 'do': UserCode.Thinking_Think, 'exit': None}

StateTables.state_function_table[States.Hungry] = \
    {'enter': UserCode.Hungry_AskPermission, 'do': None, 'exit': None}

StateTables.state_function_table[States.Finish] = \
    {'enter': None, 'do': UserCode.Finish_Finish, 'exit': None}

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

    def __init__(self):
        super().__init__(name='philosophers', target=self.run)
        #: The dining philosophers
        self.philosophers = []  # type: List[Philosopher]
        # Instantiate and initialize all philosophers
        for id_ in range(Config.Philosophers):
            self.philosophers.append(Philosopher(philosopher_id=id_))

    def register(self, view):
        self.views[view.name] = view
        for p in self.philosophers:
            p.register(view)
        waiter.register(view)

    def update(self, event):
        """ Called by Views and/or Controller to alert us to an event.
            We ignore for now.
        """
        if isinstance(event, int):
            event = gui.DiningPhilosopherEvents(event)
        if isinstance(event, gui.DiningPhilosopherEvents):
            print('Dining: %s' % event)
        else:
            raise Exception('Dining: Unknown event type')

        # process event received
        if event.event is gui.DiningPhilosopherEvents.Start:
            self.running = True
        elif event.event is gui.DiningPhilosopherEvents.Stop:
            self.running = False
        elif event.event is gui.DiningPhilosopherEvents.Pause:
            print('Pause: unhandled')
        elif event.event is gui.DiningPhilosopherEvents.Resume:
            print('Resume: unhandled')
        elif event.event is gui.DiningPhilosopherEvents.Logger:
            print('Logger: Event: %s / %s' % (event.text, event.data))

    def run(self):
        """ DiningPhilosophers Main program

            Implemented as a function so as to be callable from an outside
            entity when running in concert with other applications.

            Also runnable as a standalone application.
        """

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
                self.logger('Iterations: %s' % loop)
            if self.running is False:
                break

        # Tell philosophers to stop
        for p in self.philosophers:
            p.post_event(Events.EvStop)

        # Joining threads
        for p in self.philosophers:
            p.join()
        self.logger('All philosophers stopped')

        # Print some statistics of the simulation
        for p in self.philosophers:
            t = p.thinking_seconds
            e = p.eating_seconds
            h = int(p.hungry_seconds + 0.5)
            total = t + e + h
            self.logger('Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (p.id, t, e, h, total))

        # Shutdown
        self.set_stopping()


if __name__ == '__main__':
    """ Execute main code if run from the command line """

    dining_philosophers = DiningPhilosophers()
    dining_philosophers.start()
    dining_philosophers.set_running()
    while dining_philosophers.running:
        time.sleep(1)
    print('Done')
