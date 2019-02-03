#!/usr/bin/env python
"""
Created on January 25, 2019

@author:    Mark Sawyer
@date:      25-Jan-2019

@package:   SleepingBarber(s)
@module:    Barber(s)
@brief:     Barber - State machine definitions
@details:   Barber - State machine UML, tables and user state functions

@copyright: Mark B Sawyer, All Rights Reserved 2019
"""

# System imports
import sys
from enum import Enum
import logging

# Project imports
from modules.PyState import StateMachine    # noqa
import WaitingRoom                          # noqa
from Common import Config as Config         # noqa
from Common import Statistics as Statistics # noqa

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

"""
    @startuml

    [*] --> StartUp
    
    StartUp --> Cutting : EvStart [GetWaitingCustomer]
    StartUp --> Sleeping : EvStart [!GetWaitingCustomer]
    StartUp : enter : BarberStart

    Cutting --> Finish : EvFinishCutting [Stopping]
    Cutting --> Cutting : EvFinishCutting [GetWaitingCustomer]
    Cutting --> Sleeping : EvFinishCutting [!GetWaitingCustomer]
    Cutting : enter : StartCutting
    Cutting : do    : Cut
    Cutting : exit  : StopCutting
    
    Sleeping --> Cutting : EvCustomerEnter
    Sleeping --> Finish : EvStop
    Sleeping : enter : StartSleeping
    Sleeping : do    : Sleep
    Sleeping : exit  : StopSleeping
    
    Finish : enter : BarberDone
        
    @enduml
"""

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    Cutting = 2
    Sleeping = 3
    Finish = 4


class Events(Enum):
    EvStart = 1
    EvFinishCutting = 2
    EvCustomerEnter = 3
    EvStop = 4


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

    def __init__(self, barber_id=None):
        StateMachine.__init__(self, sm_id=barber_id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)
        logging.debug('Barber[%d]: INIT' % barber_id)
        self.customers = 0
        self.cut_timer = 0
        self.cutting_time = 0
        self.sleeping = False
        self.sleeping_time = 0
        self.waiting_room = WaitingRoom.WaitingRoom()
        self.stats = Statistics()

    # ===========================================================================
    def Cutting_Cut(self):
        """
        @brief <i>Do</i> function processing for the <i>Cutting</i> state

        @details State machine <i>do</i> function processing for the <i>Cutting</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Cutting</i> state.
        """
        # track total time cutting hair
        self.cutting_time += 1

        # process timer for current haircut
        if self.cut_timer:
            self.cut_timer -= 1
        if not self.cut_timer:
            logging.debug('Barber[%s]: Finish cutting %s' % (self.id, self.customers))
            self.event(Events.EvFinishCutting)

    # ===========================================================================
    def Cutting_StartCutting(self):
        """
        @brief Enter function processing for <i>Cutting</i> state.

        @details State machine enter function processing for the <i>Cutting</i> state.
        This function is called when the <i>Cutting</i> state is entered.
        """
        # track total customers
        self.customers += 1
        logging.debug('Barber[%s]: Start cutting %s' % (self.id, self.customers))

        # start haircut timer
        self.cut_timer = Config.cutting_time()

    # ===========================================================================
    def Cutting_StopCutting(self):
        """
        @brief <i>Exit</i> function processing for the <i>Cutting</i> state.

        @details State machine <i>exit</i> function processing for the <i>Cutting</i> state.
        This function is called when the <i>Cutting</i> state is exited.
        """
        logging.debug('Barber[%s]: Stop cutting %s' % (self.id, self.customers))

    # ===========================================================================
    def Finish_BarberDone(self):
        """
        @brief Enter function processing for <i>Finish</i> state.

        @details State machine enter function processing for the <i>Finish</i> state.
        This function is called when the <i>Finish</i> state is entered.
        """
        logging.debug('Barber[%s]: Done' % self.id)
        with self.stats.lock:
            self.stats.customers += self.customers
            self.stats.cutting_time += self.cutting_time
            self.stats.sleeping_time += self.sleeping_time

    # =========================================================
    def GetWaitingCustomer(self):
        """
        @brief Guard processing for <i>GetWaitingCustomer</i>

        @details State machine guard processing for <i>GetWaitingCustomer</i>.
        This function is called whenever the guard <i>GetWaitingCustomer</i> is tested.

        @retval True - Customer waiting [Guard is active/valid]
        @retval False - Customer NOT waiting [Guard is inactive/invalid]
        """
        return self.waiting_room.get_customer()

    # ===========================================================================
    def Sleeping_Sleep(self):
        """
        @brief <i>Do</i> function processing for the <i>Sleeping</i> state

        @details State machine <i>do</i> function processing for the <i>Sleeping</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Sleeping</i> state.
        """
        self.sleeping_time += 1

    # ===========================================================================
    def Sleeping_StartSleeping(self):
        """
        @brief Enter function processing for <i>Sleeping</i> state.

        @details State machine enter function processing for the <i>Sleeping</i> state.
        This function is called when the <i>Sleeping</i> state is entered.
        """
        logging.debug('Barber[%s]: Start sleeping' % self.id)
        self.sleeping = True

    # ===========================================================================
    def Sleeping_StopSleeping(self):
        """
        @brief <i>Exit</i> function processing for the <i>Sleeping</i> state.

        @details State machine <i>exit</i> function processing for the <i>Sleeping</i> state.
        This function is called when the <i>Sleeping</i> state is exited.
        """
        logging.debug('Barber[%s]: Stop sleeping' % self.id)
        self.sleeping = False

    # ===========================================================================
    def StartUp_BarberStart(self):
        """
        @brief Enter function processing for <i>StartUp</i> state.

        @details State machine enter function processing for the <i>StartUp</i> state.
        This function is called when the <i>StartUp</i> state is entered.
        """
        logging.debug('Barber[%s]: Starting' % self.id)

    # =========================================================
    def Stopping(self):
        """
        @brief Guard processing for <i>Stopping</i>

        @details State machine guard processing for <i>Stopping</i>.
        This function is called whenever the guard <i>Stopping</i> is tested.

        @retval True - Simulation Stopping [Guard is active/valid]
        @retval False - Simulation NOT Stopping [Guard is inactive/invalid]
        """
        logging.debug('Barber[%s]: Stopping' % self.id)

    # =========================================================
    def NOT_GetWaitingCustomer(self):
        """
        @brief Guard processing for <i>_NOT_GetWaitingCustomer</i>

        @details State machine guard processing for <i>_NOT_GetWaitingCustomer</i>.
        This function is called whenever the guard <i>_NOT_GetWaitingCustomer</i> is tested.

        @retval True - Customer NOT waiting [Guard is active/valid]
        @retval False - Customer waiting [Guard is inactive/invalid]
        """
        return not self.waiting_room.get_customer()

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: [
        {'state2': States.Cutting, 'guard': UserCode.GetWaitingCustomer, 'transition': None},
        {'state2': States.Sleeping, 'guard': UserCode.NOT_GetWaitingCustomer, 'transition': None},
    ],
}

StateTables.state_transition_table[States.Cutting] = {
    Events.EvFinishCutting: [
        {'state2': States.Finish, 'guard': UserCode.Stopping, 'transition': None},
        {'state2': States.Cutting, 'guard': UserCode.GetWaitingCustomer, 'transition': None},
        {'state2': States.Sleeping, 'guard': UserCode.NOT_GetWaitingCustomer, 'transition': None},
    ],
}

StateTables.state_transition_table[States.Sleeping] = {
    Events.EvCustomerEnter: {'state2': States.Cutting, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Finish] = {
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_BarberStart, 'do': None, 'exit': None}

StateTables.state_function_table[States.Cutting] = \
    {'enter': UserCode.Cutting_StartCutting, 'do': UserCode.Cutting_Cut, 'exit': UserCode.Cutting_StopCutting}

StateTables.state_function_table[States.Sleeping] = \
    {'enter': UserCode.Sleeping_StartSleeping, 'do': UserCode.Sleeping_Sleep, 'exit': UserCode.Sleeping_StopSleeping}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_BarberDone, 'do': None, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================
