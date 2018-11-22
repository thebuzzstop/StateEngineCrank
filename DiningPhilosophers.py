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
import logging
from enum import Enum
import random
from threading import (Lock, Thread)
import time

# Project imports
from modules.PyState import StateMachine

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logging.debug('Loading modules: %s as %s' % (__file__, __name__))
logging.info('hello sailor')

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

    Hungry --> Eating : EvHaveForks
    Hungry --> Finish : EvStop
    Hungry : do   : AskPermission
    Hungry : exit : PickUpForks

    Eating --> Thinking : EvFull
    Eating --> Finish : EvStop
    Eating : enter : StartEatingTimer
    Eating : do    : Eat
    Eating : exit  : PutDownForks

    Finish : do : Finish

    @enduml
"""

# =============================================================================
# ========== MAIN STATE CODE = STATE DEFINES = START = DO NOT MODIFY ==========
# =============================================================================


class States(Enum):
    StartUp = 1
    Thinking = 2
    Hungry = 3
    Eating = 4
    Finish = 5


class Events(Enum):
    EvStart = 1
    EvHungry = 2
    EvHaveForks = 3
    EvFull = 4
    EvStop = 5

# =============================================================================
# ========== MAIN STATE CODE = STATE DEFINES = END = DO NOT MODIFY ============
# =============================================================================


# =============================================================================
# ========== USER STATE CODE = BEGIN ==========================================
# =============================================================================


class UserCode(object):

    def __init__(self):
        pass

    @staticmethod
    def seconds(minimum, maximum):
        return random.randint(minimum, maximum)

    def StartUp(self):
        pass

    def StartThinkingTimer(self):
        pass

    def Think(self):
        pass

    def AskPermission(self):
        pass

    def PickUpForks(self):
        pass

    def StartEatingTimer(self):
        pass

    def Eat(self):
        pass

    def PutDownForks(self):
        pass

    def Finish(self):
        pass

# =============================================================================
# ========== USER STATE CODE = END ============================================
# =============================================================================

# =============================================================================
# ========== MAIN STATE CODE EVENTS = START = DO NOT MODIFY ===================
# =============================================================================


class EventsCode(object):

    def EvStart(self, id):
        pass

    def EvHungry(self, id):
        pass

    def EvHaveForks(self, id):
        pass

    def EvFull(self, id):
        pass

    def EvStop(self, id):
        pass

# =============================================================================
# ========== MAIN STATE CODE EVENTS = END = DO NOT MODIFY =====================
# =============================================================================

# =============================================================================
# ========== MAIN STATE CODE TABLES = START = DO NOT MODIFY ===================
# =============================================================================


class StateTables(object):

    state_transition_table = {
        States.StartUp: {
            Events.EvStart: {'state2': States.Thinking, 'guard': None, 'transition': None},
            Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}
        },
        States.Thinking: {
            Events.EvHungry: {'state2': States.Hungry, 'guard': None, 'transition': None},
            Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}
        },
        States.Hungry: {
            Events.EvHaveForks: {'state2': States.Eating, 'guard': None, 'transition': None},
            Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}
        },
        States.Eating: {
            Events.EvFull: {'state2': States.Thinking, 'guard': None, 'transition': None},
            Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}
        }
    }

    state_function_table = {
        States.StartUp: {'enter': UserCode.StartUp, 'do': None, 'exit': None},
        States.Thinking: {'enter': UserCode.StartThinkingTimer, 'do': UserCode.Think, 'exit': None},
        States.Hungry: {'enter': None, 'do': UserCode.AskPermission, 'exit': UserCode.PickUpForks},
        States.Eating: {'enter': UserCode.StartEatingTimer, 'do': UserCode.Eat, 'exit': UserCode.PutDownForks},
        States.Finish: {'enter': UserCode.Finish, 'do': None, 'exit': None}
    }

    def __init__(self):
        self.current_state = States.Startup
        self.state_machine = StateMachine

# =============================================================================
# ========== MAIN STATE CODE TABLES = END = DO NOT MODIFY =====================
# =============================================================================


class Config(object):
    Eat_Min = 10            # minimum number of seconds to eat
    Eat_Max = 20            # maximum number of seconds to eat
    Think_Min = 10          # minimum number of seconds to think
    Think_Max = 20          # maximum number of seconds to think
    Philosophers = 4        # number of philosophers dining
    Dining_Loops = 500      # number of main loops for dining


class ForkStatus(Enum):
    Free = 0
    InUse = 1


class Logger(object):
    __instance = None

    def __new__(cls):
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            Logger.lock = Lock
        return Logger.__instance


class Waiter(object):
    __instance = None

    def __new__(cls):
        if Waiter.__instance is None:
            Waiter.__instance = object.__new__(cls)
            Waiter.lock = Lock
        return Waiter.__instance


class Philosopher(UserCode):

    id = None               # unique id for this philosopher
    current_state = None    # current state for this philosopher
    events = 0              # counter for tracking events
    eating_seconds = 0      # number of seconds spent eating
    thinking_seconds = 0    # number of seconds spent thinking
    hungry_seconds = 0      # number of seconds spent hungry
    event_timer = 0         # timer used to time eating & thinking
    exit_code = 0           # exit code returned by this philosopher
    waiter_busy = 0         # number of times the waiter was busy
    waiter = Waiter         # get an instance of the waiter
    running = False         # True, simulation is running
    has_forks = False       # True, philosopher has possession of both forks
    left_fork = None        # philosophers left fork (index)
    right_fork = None       # philosophers right fork (index)
    thread = None           # threading variable for this philosopher
    statemachine = None     # statemachine used to control philosopher execution

    def __init__(self, id):
        self.id = id
        self.state_machine = None
        self.left_fork = id
        self.right_fork = (id + 1) % Config.Philosophers
        thread = None

if __name__ == '__main__':

    # Create locks required for thread synchronization
    waiter = Waiter
    stdio = Logger

    # Initialize all forks to 'free' (1 for each philosopher)
    forks = [ForkStatus.Free for _ in range(Config.Philosophers)]

    # Initialize all philosophers
    philosophers = []
    for id in range(Config.Philosophers):
        philosophers.append(Philosopher(id=id))
        philosophers[id].statemachine = StateMachine()
        philosophers[id].statemachine.startup_state = States.StartUp
        philosophers[id].statemachine.state_function_table = StateTables.state_function_table
        philosophers[id].statemachine.state_transition_table = StateTables.state_transition_table
        philosophers[id].statemachine.thread = Thread(target=philosophers[id].statemachine.do)

    # Philosophers have been instantiated and threads created
    # Start the simulation, i.e. start all philosophers eating
    for id in range(Config.Philosophers):
        philosophers[id].running = True

    # Wait for the simulation to complete
    for loop in range(Config.Dining_Loops):
        time.sleep(1)
        loop += 1
        if loop % 10 is 0:
            print('Iterations: %s' % loop)
