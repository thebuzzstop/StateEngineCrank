"""
The Barber Module provides the state machine execution logic to
implement a Sleeping Barber Simulation *Barber*.

The Barber Module contains:

* State machine UML, tables and user state functions.
* Auto-generated and user created custom code.

.. code-block:: rest
    :caption: **SleepingBarberUml**
    :name: SleepingBarberUml

    @startuml

    [*] --> StartUp

    StartUp --> Finish : EvStop
    StartUp --> Cutting : EvStart [WaitingCustomer] / GetCustomer()
    StartUp --> Sleeping : EvStart [!WaitingCustomer]
    StartUp : enter : BarberStart

    Sleeping --> Cutting : EvCustomerEnter
    Sleeping --> Finish : EvStop
    Sleeping : enter : StartSleeping
    Sleeping : do    : Sleep
    Sleeping : exit  : StopSleeping

    Cutting --> Cutting : EvFinishCutting [WaitingCustomer] / GetCustomer()
    Cutting --> Sleeping : EvFinishCutting [!WaitingCustomer]
    Cutting --> Stopping : EvStop
    Cutting : enter : StartCutting
    Cutting : do    : Cut

    Stopping --> Finish : EvFinishCutting
    Stopping : do : Cut

    Finish : enter : BarberDone

    @enduml
"""
# System imports
import time
from enum import Enum

# Project imports
import mvc

from StateEngineCrank.modules.PyState import StateMachine
from SleepingBarber.Common import Config as Config
from SleepingBarber.Common import ConfigData as ConfigData
from SleepingBarber.Common import Statistics as Statistics
from SleepingBarber.Customer import Events as CustomerEvents
from SleepingBarber.WaitingRoom import WaitingRoom as WaitingRoom

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    Finish = 2
    Cutting = 3
    Sleeping = 4
    Stopping = 5


class Events(Enum):
    EvStop = 1
    EvStart = 2
    EvCustomerEnter = 3
    EvFinishCutting = 4


class StateTables(object):
    state_transition_table = {}
    state_function_table = {}

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = END = DO NOT MODIFY =========
# ==============================================================================

# ==============================================================================
# ===== USER STATE CODE = BEGIN ================================================
# ==============================================================================


    def __init__(self, id=None):
        StateMachine.__init__(self, id=id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

class UserCode(StateMachine):
    """ User code unique to the Barber state implementation of the SleepingBarber simulation """

    def cleanup(self):
        self.mvc_events.unregister_actor(self.name)
        StateMachine.cleanup(self)

    def __init__(self, user_id=None, **kwargs):
        """ Barber class constructor

            :param user_id: barber ID unique to this barber
        """
        self.config = ConfigData()  #: simulation configuration data
        name = '{}{}'.format(self.config.actor_base_name, user_id)
        StateMachine.__init__(self, sm_id=user_id, name=name,
                              startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table,
                              **kwargs)

        self.customers = 0                  #: customers served
        self.cut_timer = 0                  #: cut timer, used to time the length of a haircut
        self.cutting_time = 0               #: total time spent cutting
        self.sleep_timer = 0                #: sleep timer, used to time the length of a barber sleeping
        self.sleeping_time = 0              #: total time spent sleeping
        self.current_customer = None        #: current customer being served
        self.waiting_room = WaitingRoom()   #: waiting room instantiation
        self.mvc_events = mvc.Event()       #: for event registration
        self.mvc_events.register_actor(class_name=self.config.class_name, actor_name=self.name)

    def update(self, event):
        """ Called by view to alert us to a change - we ignore for now """
        pass

    # ===========================================================================
    # noinspection PyPep8Naming
    def Cutting_Cut(self):
        """ State machine *do* function processing for the *Cutting* state.

            This function is called once every state machine iteration to perform
            processing for the *Cutting* state.
        """
        time.sleep(1)
        # track total time cutting hair
        self.cutting_time += 1

        # process timer for current haircut
        if self.cut_timer:
            self.cut_timer -= 1
        # post event for view handling
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.cut_timer, self.current_state, self.current_customer]))
        if self.cut_timer == 0:
            self.logger('Barber[%s] Finish cutting %s' % (self.id, self.customers))
            self.post_event(Events.EvFinishCutting)
            self.current_customer.post_event(CustomerEvents.EvFinishCutting)

    # ===========================================================================
    # noinspection PyPep8Naming
    def Cutting_StartCutting(self):
        """ State machine *enter* function processing for the *Cutting* state.

            This function is called when the *Cutting* state is entered.
        """
        # track total customers
        self.customers += 1
        # start haircut timer
        self.cut_timer = Config.cutting_time()
        self.logger('Barber[%s] StartCutting %s [%s]' % (self.id, self.customers, self.cut_timer))
        # post event for view handling
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.cut_timer, self.current_state, self.current_customer]))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Finish_BarberDone(self):
        """ State machine *enter* function processing for the *Finish* state.

            This function is called when the *Finish* state is entered at the
            end of the SleepingBarber simulation.
        """
        self.logger('Barber[%s] BarberDone' % self.id)
        stats = Statistics()
        with stats.lock:
            stats.barbers.append(self)
        self.running = False

    # ===========================================================================
    # noinspection PyPep8Naming
    def Sleeping_Sleep(self):
        """ State machine *do* function processing for the *Sleeping* state.

            This function is called once every state machine iteration to perform
            processing for the *Sleeping* state.
        """
        time.sleep(1)
        self.sleeping_time += 1     # total time sleeping
        self.sleep_timer += 1       # current time sleeping
        # post event for view handling
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.sleep_timer, self.current_state]))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Sleeping_StartSleeping(self):
        """ State machine *enter* function processing for the *Sleeping* state.

            This function is called when the *Sleeping* state is entered.
        """
        self.logger('Barber[%s] StartSleeping' % self.id)
        self.sleep_timer = 0
        # post event for view handling
        self.notify(self.sm_events.events.post(class_name='mvc', actor_name=self.name, user_id=self.id,
                                               event=mvc.Event.Events.TIMER,
                                               data=[self.sleep_timer, self.current_state]))

    # ===========================================================================
    # noinspection PyPep8Naming
    def Sleeping_StopSleeping(self):
        """ State machine *exit* function processing for the *Sleeping* state.

            This function is called when the *Sleeping* state is exited.
        """
        self.logger('Barber[%s] StopSleeping' % self.id)

    # ===========================================================================
    # noinspection PyPep8Naming
    def StartUp_BarberStart(self):
        """ State machine *enter* function processing for the *StartUp* state.

            This function is called when the *StartUp* state is entered.
        """
        self.logger('Barber[%s] Starting' % self.id)

    # =========================================================
    # noinspection PyPep8Naming
    def GetCustomer(self):
        """ State machine state transition processing for *GetCustomer*.

            This function is called whenever the state transition *GetCustomer*
            is taken.

            A customer is obtained from the waiting room and the customer
            event EvBarberReady is delivered.
        """
        with self.waiting_room.lock:
            self.current_customer = self.waiting_room.get_customer()
        self.logger('Barber[%s] GetCustomer %s' % (self.id, self.current_customer.id))
        self.current_customer.post_event(CustomerEvents.EvBarberReady)
        self.current_customer.set_barber(self)

    # =========================================================
    # noinspection PyPep8Naming
    def NOT_WaitingCustomer(self):
        """ State machine guard processing for *NOT_WaitingCustomer*.

            This function is called whenever the guard *NOT_WaitingCustomer*
            is tested.

            :returns: True : Guard is active/valid
            :returns: False : Guard is inactive/invalid
        """
        with self.waiting_room.lock:
            return not self.waiting_room.customer_waiting()

    # =========================================================
    # noinspection PyPep8Naming
    def WaitingCustomer(self):
        """ State machine guard processing for *GetWaitingCustomer*.

            This function is called whenever the guard *GetWaitingCustomer*
            is tested.

            :returns: True : Customer waiting [Guard is active/valid]
            :returns: False : Customer NOT waiting [Guard is inactive/invalid]
        """
        with self.waiting_room.lock:
            return self.waiting_room.customer_waiting()

    # ===========================================================================
    # noinspection PyPep8Naming
    def Stopping_Cut(self):
        """ State machine *do* function processing for the *Stopping* state.

            This function is called once every state machine iteration to perform
            processing for the *Stopping* state.

            Basically we are performing the same function as the *Cutting_Cut*
            function since we are still cutting a customers hair. The main
            difference is that when we are in this state and the *EvFinishCutting*
            event is thrown we will transition to the *Finish* state.
        """
        self.Cutting_Cut()

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================

StateTables.state_transition_table[States.StartUp] = {
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
    Events.EvStart: [
        {'state2': States.Cutting, 'guard': UserCode.WaitingCustomer, 'transition': UserCode.GetCustomer},
        {'state2': States.Sleeping, 'guard': UserCode.NOT_WaitingCustomer, 'transition': None},
    ],
}

StateTables.state_transition_table[States.Finish] = {
}

StateTables.state_transition_table[States.Cutting] = {
    Events.EvFinishCutting: [
        {'state2': States.Cutting, 'guard': UserCode.WaitingCustomer, 'transition': UserCode.GetCustomer},
        {'state2': States.Sleeping, 'guard': UserCode.NOT_WaitingCustomer, 'transition': None},
    ],
    Events.EvStop: {'state2': States.Stopping, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Sleeping] = {
    Events.EvCustomerEnter: {'state2': States.Cutting, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Stopping] = {
    Events.EvFinishCutting: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_BarberStart, 'do': None, 'exit': None}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_BarberDone, 'do': None, 'exit': None}

StateTables.state_function_table[States.Cutting] = \
    {'enter': UserCode.Cutting_StartCutting, 'do': UserCode.Cutting_Cut, 'exit': None}

StateTables.state_function_table[States.Sleeping] = \
    {'enter': UserCode.Sleeping_StartSleeping, 'do': UserCode.Sleeping_Sleep, 'exit': UserCode.Sleeping_StopSleeping}

StateTables.state_function_table[States.Stopping] = \
    {'enter': None, 'do': UserCode.Stopping_Cut, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================
