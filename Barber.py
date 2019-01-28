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
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports
from modules.PyState import StateMachine
import WaitingRoom

"""
    @startuml

    [*] --> StartUp
    
    StartUp --> Cutting : EvStart [CustomerWaiting]
    StartUp --> Sleeping : EvStart [!CustomerWaiting]
    StartUp : enter : BarberStart

    Cutting --> Finish : EvFinishCutting [Stopping]
    Cutting --> Cutting : EvFinishCutting [CustomerWaiting && WaitingRoom] / GetWaitingCustomer()
    Cutting --> Sleeping : EvFinishCutting [!CustomerWaiting && WaitingRoom]
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

    def __init__(self, id=None):
        StateMachine.__init__(self, id=id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

    # =========================================================
    def CustomerWaiting(self):
        """
        @brief Guard processing for <i>CustomerWaiting</i>

        @details State machine guard processing for <i>CustomerWaiting</i>.
        This function is called whenever the guard <i>CustomerWaiting</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def CustomerWaiting_AND_WaitingRoom(self):
        """
        @brief Guard processing for <i>CustomerWaiting_AND_WaitingRoom</i>

        @details State machine guard processing for <i>CustomerWaiting_AND_WaitingRoom</i>.
        This function is called whenever the guard <i>CustomerWaiting_AND_WaitingRoom</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # ===========================================================================
    def Cutting_Cut(self):
        """
        @brief <i>Do</i> function processing for the <i>Cutting</i> state

        @details State machine <i>do</i> function processing for the <i>Cutting</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Cutting</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Cutting_StartCutting(self):
        """
        @brief Enter function processing for <i>Cutting</i> state.

        @details State machine enter function processing for the <i>Cutting</i> state.
        This function is called when the <i>Cutting</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Cutting_StopCutting(self):
        """
        @brief <i>Exit</i> function processing for the <i>Cutting</i> state.

        @details State machine <i>exit</i> function processing for the <i>Cutting</i> state.
        This function is called when the <i>Cutting</i> state is exited.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Finish_BarberDone(self):
        """
        @brief Enter function processing for <i>Finish</i> state.

        @details State machine enter function processing for the <i>Finish</i> state.
        This function is called when the <i>Finish</i> state is entered.

        @todo FIXME
        """
        return

    # =========================================================
    def GetWaitingCustomer(self):
        """
        @brief State transition processing for <i>GetWaitingCustomer</i>

        @details State machine state transition processing for <i>GetWaitingCustomer</i>.
        This function is called whenever the state transition <i>GetWaitingCustomer</i> is taken.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Sleeping_Sleep(self):
        """
        @brief <i>Do</i> function processing for the <i>Sleeping</i> state

        @details State machine <i>do</i> function processing for the <i>Sleeping</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Sleeping</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Sleeping_StartSleeping(self):
        """
        @brief Enter function processing for <i>Sleeping</i> state.

        @details State machine enter function processing for the <i>Sleeping</i> state.
        This function is called when the <i>Sleeping</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Sleeping_StopSleeping(self):
        """
        @brief <i>Exit</i> function processing for the <i>Sleeping</i> state.

        @details State machine <i>exit</i> function processing for the <i>Sleeping</i> state.
        This function is called when the <i>Sleeping</i> state is exited.

        @todo FIXME
        """
        return

    # ===========================================================================
    def StartUp_BarberStart(self):
        """
        @brief Enter function processing for <i>StartUp</i> state.

        @details State machine enter function processing for the <i>StartUp</i> state.
        This function is called when the <i>StartUp</i> state is entered.

        @todo FIXME
        """
        return

    # =========================================================
    def Stopping(self):
        """
        @brief Guard processing for <i>Stopping</i>

        @details State machine guard processing for <i>Stopping</i>.
        This function is called whenever the guard <i>Stopping</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def _NOT_CustomerWaiting(self):
        """
        @brief Guard processing for <i>_NOT_CustomerWaiting</i>

        @details State machine guard processing for <i>_NOT_CustomerWaiting</i>.
        This function is called whenever the guard <i>_NOT_CustomerWaiting</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def _NOT_CustomerWaiting_AND_WaitingRoom(self):
        """
        @brief Guard processing for <i>_NOT_CustomerWaiting_AND_WaitingRoom</i>

        @details State machine guard processing for <i>_NOT_CustomerWaiting_AND_WaitingRoom</i>.
        This function is called whenever the guard <i>_NOT_CustomerWaiting_AND_WaitingRoom</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================

StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: [
        {'state2': States.Cutting, 'guard': UserCode.CustomerWaiting, 'transition': None},
        {'state2': States.Sleeping, 'guard': UserCode._NOT_CustomerWaiting, 'transition': None},
    ],
}

StateTables.state_transition_table[States.Cutting] = {
    Events.EvFinishCutting: [
        {'state2': States.Finish, 'guard': UserCode.Stopping, 'transition': None},
        {'state2': States.Cutting, 'guard': UserCode.CustomerWaiting_AND_WaitingRoom, 'transition': UserCode.GetWaitingCustomer},
        {'state2': States.Sleeping, 'guard': UserCode._NOT_CustomerWaiting_AND_WaitingRoom, 'transition': None},
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
