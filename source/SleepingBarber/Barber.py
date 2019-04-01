"""
* State machine UML, tables and user state functions.
* Contains auto-generated and user created custom code.

**SleepingBarber Barber UML**::

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
from mvc import Model
from modules.PyState import StateMachine
from Common import Config as Config
from Common import Statistics as Statistics
import Customer
import WaitingRoom

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


class UserCode(StateMachine, Model):
    """ User code unique to the Barber state implementation of the SleepingBarber simulation """

    def __init__(self, id_=None):
        """ Barber class constructor

            :param id_: barber ID unique to this barber
        """
        Model.__init__(self, name='Barber%d' % id_)
        StateMachine.__init__(self, sm_id=id_, name='Barber%d' % id_,
                              startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

        self.id = id_                   #: barber ID
        self.customers = 0              #: customers served
        self.cut_timer = 0              #: cut timer, used to time the length of a haircut
        self.cutting_time = 0           #: total time spent cutting
        self.sleeping_time = 0          #: total time spent sleeping
        self.current_customer = None    #: current customer being served
        self.waiting_room = WaitingRoom.WaitingRoom()   #: waiting room instantiation

    def register(self, view):
        self.views[view.name] = view

    def logger(self, text):
        self.views['console'].write(text)

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
        if self.cut_timer == 0:
            self.logger('Barber[%s] Finish cutting %s' % (self.id, self.customers))
            self.post_event(Events.EvFinishCutting)
            self.current_customer.post_event(Customer.Events.EvFinishCutting)

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
        self.sleeping_time += 1

    # ===========================================================================
    # noinspection PyPep8Naming
    def Sleeping_StartSleeping(self):
        """ State machine *enter* function processing for the *Sleeping* state.

            This function is called when the *Sleeping* state is entered.
        """
        self.logger('Barber[%s] StartSleeping' % self.id)

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
        self.current_customer.post_event(Customer.Events.EvBarberReady)

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
