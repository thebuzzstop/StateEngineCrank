#!/usr/bin/env python
"""
Created on November 12, 2018

@author:    Mark Sawyer
@date:      12-Nov-2018

@package:   DiningPhilosophers
@brief:     State machine definitions
@details:   State machine UML, tables and user state functions

@copyright: Mark B Sawyer, All Rights Reserved 2018
"""

# System imports
import sys
from enum import Enum
import random
from threading import (Lock, Thread)
import time

import logging
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

    Finish : do : Finish

    @enduml
"""

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    Thinking = 2
    Finish = 3
    Hungry = 4
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

# ==============================================================================
# ===== USER STATE CODE = BEGIN ================================================
# ==============================================================================
class UserCode(StateMachine):



    def __init__(self, id=None):
        StateMachine.__init__(self, id=id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

    # =========================================================
    """ Eating_Eat 
        @Todo FIXME
    """
    def Eating_Eat(id):
        return

    # =========================================================
    """ Eating_PutDownForks 
        @Todo FIXME
    """
    def Eating_PutDownForks(id):
        return

    # =========================================================
    """ Eating_StartEatingTimer 
        @Todo FIXME
    """
    def Eating_StartEatingTimer(id):
        return

    # =========================================================
    """ Finish_Finish 
        @Todo FIXME
    """
    def Finish_Finish(id):
        return

    # =========================================================
    """ Hungry_AskPermission 
        @Todo FIXME
    """
    def Hungry_AskPermission(id):
        return

    # =========================================================
    """ PickUpForks 
        @Todo FIXME
    """
    def PickUpForks(id):
        return

    # =========================================================
    """ StartUp_StartUp 
        @Todo FIXME
    """
    def StartUp_StartUp(id):
        return

    # =========================================================
    """ ThankWaiter 
        @Todo FIXME
    """
    def ThankWaiter(id):
        return

    # =========================================================
    """ Thinking_StartThinkingTimer 
        @Todo FIXME
    """
    def Thinking_StartThinkingTimer(id):
        return

    # =========================================================
    """ Thinking_Think 
        @Todo FIXME
    """
    def Thinking_Think(id):
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
    {'enter': None, 'do': UserCode.Finish_Finish, 'exit': None}

StateTables.state_function_table[States.Hungry] = \
    {'enter': UserCode.Hungry_AskPermission, 'do': None, 'exit': None}

StateTables.state_function_table[States.Eating] = \
    {'enter': UserCode.Eating_StartEatingTimer, 'do': UserCode.Eating_Eat, 'exit': UserCode.Eating_PutDownForks}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================
