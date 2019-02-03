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
    
    StartUp --> HairCut : EvStart [BarberSleeping]
    StartUp --> Waiting : EvStart [BarberCutting && GetWaitingRoomChair]
    StartUp --> Finish : EvStart [BarberCutting && !GetWaitingRoomChair] / NoHairCut()
    StartUp : enter : CustomerStart
    
    HairCut --> Finish : EvFinishCutting [Stopping]
    HairCut : enter : StartHairCut
    HairCut : do    : GetHairCut
    HairCut : exit  : StopHairCut
    
    Waiting --> HairCut : EvBarberReady
    Waiting --> Finish : EvStop
    Waiting : enter : StartWaiting
    Waiting : do    : Wait
    Waiting : exit  : StopWaiting
    
    Finish : enter : CustomerDone

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

    def __init__(self, customer_id=None):
        StateMachine.__init__(self, sm_id=customer_id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)
        logging.debug('Customer[%d]: INIT' % customer_id)
        self.waiting_time = 0
        self.waiting_room = WaitingRoom.WaitingRoom()
        self.cutting_time = 0
        self.total_time = 0
        self.stats = Statistics()

    # ===========================================================================
    def Finish_CustomerDone(self):
        """
        @brief Enter function processing for <i>Finish</i> state.

        @details State machine enter function processing for the <i>Finish</i> state.
        This function is called when the <i>Finish</i> state is entered.
        """
        self.total_time = self.waiting_time + self.cutting_time
        logging.debug('Customer[%s]: Done (%d)' % (self.id, self.total_time))

    # ===========================================================================
    def HairCut_GetHairCut(self):
        """
        @brief <i>Do</i> function processing for the <i>HairCut</i> state

        @details State machine <i>do</i> function processing for the <i>HairCut</i> state.
        This function is called once every state machine iteration to perform processing
        for the <i>HairCut</i> state.
        """
        self.cutting_time += 1

    # ===========================================================================
    def HairCut_StartHairCut(self):
        """
        @brief Enter function processing for <i>HairCut</i> state.

        @details State machine enter function processing for the <i>HairCut</i> state.
        This function is called when the <i>HairCut</i> state is entered.
        """
        logging.debug('Customer[%s]: Start' % self.id)

    # ===========================================================================
    def HairCut_StopHairCut(self):
        """
        @brief <i>Exit</i> function processing for the <i>HairCut</i> state.

        @details State machine <i>exit</i> function processing for the <i>HairCut</i> state.
        This function is called when the <i>HairCut</i> state is exited.
        """
        logging.debug('Customer[%s]: Done (%s)' % (self.id, self.cutting_time))

    # =========================================================
    def NoHairCut(self):
        """
        @brief State transition processing for <i>NoHairCut</i>

        @details State machine state transition processing for <i>NoHairCut</i>.
        This function is called whenever the state transition <i>NoHairCut</i> is taken.
        """
        with self.stats.lock:
            self.stats.lost_customers += 1

    # ===========================================================================
    def StartUp_CustomerStart(self):
        """
        @brief Enter function processing for <i>StartUp</i> state.

        @details State machine enter function processing for the <i>StartUp</i> state.
        This function is called when the <i>StartUp</i> state is entered.

        @todo FIXME
        """
        return

    # ===========================================================================
    def Waiting_StartWaiting(self):
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
        """
        self.waiting_time += 1

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
    def BarberCutting_AND_GetWaitingRoomChair(self):
        """
        @brief Guard processing for <i>BarberCutting_AND_GetWaitingRoomChair</i>

        @details State machine guard processing for <i>BarberCutting_AND_GetWaitingRoomChair</i>.
        This function is called whenever the guard <i>BarberCutting_AND_GetWaitingRoomChair</i> is tested.

        @retval True if Barber is busy cutting hair and there is a waiting room
                    chair available [Guard is active/valid]
        @retval False if NOT Barber is cutting hair and there is a waiting room
                    chair available [Guard is inactive/invalid]
        """
        return


    # =========================================================
    def BarberCutting_AND__NOT_GetWaitingRoomChair(self):
        """
        @brief Guard processing for <i>BarberCutting_AND__NOT_GetWaitingRoomChair</i>

        @details State machine guard processing for <i>BarberCutting_AND__NOT_GetWaitingRoomChair</i>.
        This function is called whenever the guard <i>BarberCutting_AND__NOT_GetWaitingRoomChair</i> is tested.

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


# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================

StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: [
        {'state2': States.HairCut, 'guard': UserCode.BarberSleeping, 'transition': None},
        {'state2': States.Waiting, 'guard': UserCode.BarberCutting_AND_GetWaitingRoomChair, 'transition': None},
        {'state2': States.Finish, 'guard': UserCode.BarberCutting_AND__NOT_GetWaitingRoomChair, 'transition': UserCode.NoHairCut},
    ],
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
    {'enter': UserCode.StartUp_CustomerStart, 'do': None, 'exit': None}

StateTables.state_function_table[States.HairCut] = \
    {'enter': UserCode.HairCut_StartHairCut, 'do': UserCode.HairCut_GetHairCut, 'exit': UserCode.HairCut_StopHairCut}

StateTables.state_function_table[States.Waiting] = \
    {'enter': UserCode.Waiting_StartWaiting, 'do': UserCode.Waiting_Wait, 'exit': UserCode.Waiting_StopWaiting}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_CustomerDone, 'do': None, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================
