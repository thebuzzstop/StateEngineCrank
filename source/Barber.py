##
# @package  SleepingBarber.Barber
# @brief:   State machine implementation
# @details: State machine UML, tables and user state functions.
#           Contains auto-generated and user created custom code.
# @author:  Mark Sawyer
# @date:    25-Jan-2019

# System imports
import sys
import time
from enum import Enum
import logging

# Project imports
from modules.PyState import StateMachine    # noqa
import WaitingRoom                          # noqa
from Common import Config as Config         # noqa
from Common import Statistics as Statistics # noqa
import Customer                             # noqa

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

"""
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


class UserCode(StateMachine):
    """ User code unique to the Barber state implementation of the SleepingBarber
        simulation """
    def __init__(self, id=None):
        ## Barber class constructor
        #    @param id - barber ID unique to this barber

        StateMachine.__init__(self, sm_id=id, name='Barber%d' % id,
                              startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)
        logging.debug('Barber[%s] INIT' % id)
        self.id = id
        self.customers = 0
        self.cut_timer = 0
        self.cutting_time = 0
        self.sleeping_time = 0
        self.waiting_room = WaitingRoom.WaitingRoom()
        self.current_customer = None

    # ===========================================================================
    def Cutting_Cut(self):
        """
        @brief <i>Do</i> function processing for the <i>Cutting</i> state

        @details State machine <i>do</i> function processing for the <i>Cutting</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Cutting</i> state.
        """
        time.sleep(1)
        # track total time cutting hair
        self.cutting_time += 1

        # process timer for current haircut
        if self.cut_timer:
            self.cut_timer -= 1
        if self.cut_timer == 0:
            logging.debug('Barber[%s] Finish cutting %s' % (self.id, self.customers))
            self.post_event(Events.EvFinishCutting)
            self.current_customer.post_event(Customer.Events.EvFinishCutting)

    # ===========================================================================
    def Cutting_StartCutting(self):
        """
        @brief Enter function processing for <i>Cutting</i> state.

        @details State machine enter function processing for the <i>Cutting</i> state.
        This function is called when the <i>Cutting</i> state is entered.
        """
        # track total customers
        self.customers += 1
        # start haircut timer
        self.cut_timer = Config.cutting_time()
        logging.debug('Barber[%s] StartCutting %s [%s]' % (self.id, self.customers, self.cut_timer))

    # ===========================================================================
    def Finish_BarberDone(self):
        """
        @brief Enter function processing for <i>Finish</i> state.

        @details State machine enter function processing for the <i>Finish</i> state.
        This function is called when the <i>Finish</i> state is entered at the
        end of the SleepinBarber simulation.
        """
        logging.debug('Barber[%s] BarberDone' % self.id)
        stats = Statistics()
        with stats.lock:
            stats.barbers.append(self)
        self.running = False

    # ===========================================================================
    def Sleeping_Sleep(self):
        """
        @brief <i>Do</i> function processing for the <i>Sleeping</i> state

        @details State machine <i>do</i> function processing for the <i>Sleeping</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Sleeping</i> state.
        """
        time.sleep(1)
        self.sleeping_time += 1

    # ===========================================================================
    def Sleeping_StartSleeping(self):
        """
        @brief Enter function processing for <i>Sleeping</i> state.

        @details State machine enter function processing for the <i>Sleeping</i> state.
        This function is called when the <i>Sleeping</i> state is entered.
        """
        logging.debug('Barber[%s] StartSleeping' % self.id)

    # ===========================================================================
    def Sleeping_StopSleeping(self):
        """
        @brief <i>Exit</i> function processing for the <i>Sleeping</i> state.

        @details State machine <i>exit</i> function processing for the <i>Sleeping</i> state.
        This function is called when the <i>Sleeping</i> state is exited.
        """
        logging.debug('Barber[%s] StopSleeping' % self.id)

    # ===========================================================================
    def StartUp_BarberStart(self):
        """
        @brief Enter function processing for <i>StartUp</i> state.

        @details State machine enter function processing for the <i>StartUp</i> state.
        This function is called when the <i>StartUp</i> state is entered.
        """
        logging.debug('Barber[%s] Starting' % self.id)

    # =========================================================
    def GetCustomer(self):
        """
        @brief State transition processing for <i>GetCustomer</i>

        @details State machine state transition processing for <i>GetCustomer</i>.
        This function is called whenever the state transition <i>GetCustomer</i> is taken.

        A customer is obtained from the waiting room and the customer
        event EvBarberReady is delivered.
        """
        with self.waiting_room.lock:
            self.current_customer = self.waiting_room.get_customer()
        self.current_customer.post_event(Customer.Events.EvBarberReady)

    # =========================================================
    def NOT_WaitingCustomer(self):
        """
        @brief Guard processing for <i>NOT_WaitingCustomer</i>

        @details State machine guard processing for <i>NOT_WaitingCustomer</i>.
        This function is called whenever the guard <i>NOT_WaitingCustomer</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid
        """
        with self.waiting_room.lock:
            return not self.waiting_room.customer_waiting()

    # =========================================================
    def WaitingCustomer(self):
        """
        @brief Guard processing for <i>GetWaitingCustomer</i>

        @details State machine guard processing for <i>GetWaitingCustomer</i>.
        This function is called whenever the guard <i>GetWaitingCustomer</i> is tested.

        @retval True - Customer waiting [Guard is active/valid]
        @retval False - Customer NOT waiting [Guard is inactive/invalid]
        """
        with self.waiting_room.lock:
            return self.waiting_room.customer_waiting()

    # ===========================================================================
    def Stopping_Cut(self):
        """
        @brief <i>Do</i> function processing for the <i>Stopping</i> state

        @details State machine <i>do</i> function processing for the <i>Stopping</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Stopping</i> state.

        Basically we are performing the same function as the <i>Cutting_Cut</i> function
        since we are still cutting a customers hair. The main difference is that when we
        are in this state and the <i>EvFinishCutting</i> event is thrown we will transition
        to the <i>Finish</i> state.
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
