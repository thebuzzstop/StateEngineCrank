#!/usr/bin/env python
"""
Created on January 25, 2019

@author:    Mark Sawyer
@date:      25-Jan-2019

@package:   SleepingBarber(s)
@module:    Customer
@brief:     Customer - State machine definitions
@details:   Customer - State machine UML, tables and user state functions

@copyright: Mark B Sawyer, All Rights Reserved 2019
"""

# System imports
import sys
from enum import Enum
import random
from threading import (Lock, Thread)
import time

import logging
from typing import List

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports

logging.debug("Importing modules.PyState")
from modules.PyState import StateMachine
logging.debug("Back from modules.PyState")

"""
    @startuml

    [*] --> StartUp
    
    StartUp --> HairCut : EvStart [BarberSleeping]
    StartUp --> Waiting : EvStart [BarberCutting && WaitingRoom]
    StartUp --> Finish : EvStart [BarberCutting && !WaitingRoom]
    
    HairCut --> Finish : EvFinishCutting [Stopping]
    HairCut : enter : StartHairCut
    HairCut : do    : GetCut
    HairCut : exit  : StopHairCut
    
    Waiting --> HairCut : EvBarberReady
    Waiting --> Finish : EvStop
    Waiting : enter : StartLock
    Waiting : do    : Wait
    Waiting : exit  : StopWaiting
    
    Finish : do : Finish
        
    @enduml
"""

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    HairCut = 2
    Waiting = 3
    Finish = 4


class Events(Enum):
    EvStart = 1
    EvFinishCutting = 2
    EvBarberReady = 3
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
    def BarberCutting_AND_WaitingRoom(self):
        """
        @brief Guard processing for <i>BarberCutting_AND_WaitingRoom</i>

        @details State machine guard processing for <i>BarberCutting_AND_WaitingRoom</i>.
        This function is called whenever the guard <i>BarberCutting_AND_WaitingRoom</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def BarberCutting_AND__NOT_WaitingRoom(self):
        """
        @brief Guard processing for <i>BarberCutting_AND__NOT_WaitingRoom</i>

        @details State machine guard processing for <i>BarberCutting_AND__NOT_WaitingRoom</i>.
        This function is called whenever the guard <i>BarberCutting_AND__NOT_WaitingRoom</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # =========================================================
    def BarberSleeping(self):
        """
        @brief Guard processing for <i>BarberSleeping</i>

        @details State machine guard processing for <i>BarberSleeping</i>.
        This function is called whenever the guard <i>BarberSleeping</i> is tested.

        @retval True Guard is active/valid
        @retval False Guard is inactive/invalid

        @todo FIXME
        """
        return False

    # ===========================================================================
    def Finish_Finish(self):
        """
        @brief <i>Do</i> function processing for the <i>Finish</i> state

        @details State machine <i>do</i> function processing for the <i>Finish</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Finish</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def HairCut_GetCut(self):
        """
        @brief <i>Do</i> function processing for the <i>HairCut</i> state

        @details State machine <i>do</i> function processing for the <i>HairCut</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>HairCut</i> state.

        @todo FIXME
        """
        return

    # ===========================================================================
    def HairCut_StartHairCut(self):
        """
        @brief Enter function processing for <i>HairCut</i> state.

        @details State machine enter function processing for the <i>HairCut</i> state.
        This function is called when the <i>HairCut</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def HairCut_StopHairCut(self):
        """
        @brief <i>Exit</i> function processing for the <i>HairCut</i> state.

        @details State machine <i>exit</i> function processing for the <i>HairCut</i> state.
        This function is called when the <i>HairCut</i> state is exited.

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

    # ===========================================================================
    def Waiting_StartLock(self):
        """
        @brief Enter function processing for <i>Waiting</i> state.

        @details State machine enter function processing for the <i>Waiting</i> state.
        This function is called when the <i>Waiting</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Waiting_StopWaiting(self):
        """
        @brief <i>Exit</i> function processing for the <i>Waiting</i> state.

        @details State machine <i>exit</i> function processing for the <i>Waiting</i> state.
        This function is called when the <i>Waiting</i> state is exited.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Waiting_Wait(self):
        """
        @brief <i>Do</i> function processing for the <i>Waiting</i> state

        @details State machine <i>do</i> function processing for the <i>Waiting</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>Waiting</i> state.

        @todo FIXME
        """
        return

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================

StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: {'state2': States.HairCut, 'guard': UserCode.BarberSleeping, 'transition': None},
    Events.EvStart: {'state2': States.Waiting, 'guard': UserCode.BarberCutting_AND_WaitingRoom, 'transition': None},
    Events.EvStart: {'state2': States.Finish, 'guard': UserCode.BarberCutting_AND__NOT_WaitingRoom, 'transition': None},
}

StateTables.state_transition_table[States.HairCut] = {
    Events.EvFinishCutting: {'state2': States.Finish, 'guard': UserCode.Stopping, 'transition': None},
}

StateTables.state_transition_table[States.Waiting] = {
    Events.EvBarberReady: {'state2': States.HairCut, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Finish] = {
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.HairCut] = \
    {'enter': UserCode.HairCut_StartHairCut, 'do': UserCode.HairCut_GetCut, 'exit': UserCode.HairCut_StopHairCut}

StateTables.state_function_table[States.Waiting] = \
    {'enter': UserCode.Waiting_StartLock, 'do': UserCode.Waiting_Wait, 'exit': UserCode.Waiting_StopWaiting}

StateTables.state_function_table[States.Finish] = \
    {'enter': None, 'do': UserCode.Finish_Finish, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================
