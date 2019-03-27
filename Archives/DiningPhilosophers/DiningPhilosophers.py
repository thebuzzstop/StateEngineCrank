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

# =============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY ======
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
    EvHavePermission = 3
    EvFull = 4
    EvStop = 5


class StateTables(object):
    state_transition_table = {}
    state_function_table = {}

# =============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = END = DO NOT MODIFY ========
# =============================================================================


class Config(object):
    Eat_Min = 10            # minimum number of seconds to eat
    Eat_Max = 30            # maximum number of seconds to eat
    Think_Min = 10          # minimum number of seconds to think
    Think_Max = 30          # maximum number of seconds to think
    Philosophers = 4        # number of philosophers dining
    Dining_Loops = 100      # number of main loops for dining


class ForkStatus(Enum):
    Free = 0
    InUse = 1


class Waiter(object):

    def __init__(self):
        self.lock = Lock()

    def request(self, id, left_fork, right_fork):
        logging.debug('SM[%s] waiter[in]' % id)
        self.lock.acquire()
        while forks[left_fork] is ForkStatus.InUse:
            time.sleep(0.1)
        while forks[right_fork] is ForkStatus.InUse:
            time.sleep(0.1)
        logging.debug('SM[%s] waiter[out]' % id)

    def thankyou(self):
        logging.debug('SM[%s] waiter release' % id)
        self.lock.release()


# Initialize all forks to 'free' (1 for each philosopher)
forks = [ForkStatus.Free for _ in range(Config.Philosophers)]

# Array of philosophers, populated in __main__
philosophers = [None for _ in range(Config.Philosophers)]

# Waiter who grants requests for access to forks
waiter = Waiter()

# =============================================================================
# ===== USER STATE CODE = BEGIN ===============================================
# =============================================================================


class UserCode(StateMachine):

    def __init__(self, id=None):
        StateMachine.__init__(self, id=id, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

        self.id = id                # id used to identify forks and threads
        self.events_counter = 0     # counter for tracking events
        self.eating_seconds = 0     # number of seconds spent eating
        self.thinking_seconds = 0   # number of seconds spent thinking
        self.hungry_seconds = 0     # number of seconds spent hungry
        self.event_timer = 0        # timer used to time eating & thinking

        self.left_fork = id
        self.right_fork = (id + 1) % Config.Philosophers

    @staticmethod
    def seconds(minimum, maximum):
        return random.randint(minimum, maximum)

    def StartUp(self):
        self.event(Events.EvStart)

    def StartThinkingTimer(self):
        self.event_timer = UserCode.seconds(Config.Think_Min, Config.Think_Max)
        logging.info('SM[%s] Thinking (%s)' % (self.id, self.event_timer))

    def Think(self):
        time.sleep(1)
        self.thinking_seconds += 1
        self.event_timer -= 1
        if self.event_timer == 0:
            self.event(Events.EvHungry)

    def AskPermission(self):
        tstart = time.time()
        waiter.request(self.id, self.left_fork, self.right_fork)
        tend = time.time()
        thungry = tend-tstart
        self.hungry_seconds += thungry
        logging.info('SM[%s] Hungry (%s)' % (self.id, round(thungry)))
        self.event(Events.EvHavePermission)

    def PickUpForks(self):
        forks[self.left_fork] = ForkStatus.InUse
        forks[self.right_fork] = ForkStatus.InUse
        waiter.thankyou()

    def ThankWaiter(self):
        waiter.thankyou()

    def StartEatingTimer(self):
        self.event_timer = UserCode.seconds(Config.Eat_Min, Config.Eat_Max)
        logging.info('SM[%s] Eating (%s)' % (self.id, self.event_timer))

    def Eat(self):
        time.sleep(1)
        self.eating_seconds += 1
        self.event_timer -= 1
        if self.event_timer == 0:
            self.event(Events.EvFull)

    def PutDownForks(self):
        forks[self.left_fork] = ForkStatus.Free
        forks[self.right_fork] = ForkStatus.Free

    def Finish(self):
        logging.info('SM[%s] Finished' % self.id)
        self.running = False

# =============================================================================
# ===== USER STATE CODE = END =================================================
# =============================================================================

# =============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY ========================
# =============================================================================


StateTables.state_transition_table[States.StartUp] = { \
    Events.EvStart: {'state2': States.Thinking, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}}

StateTables.state_transition_table[States.Thinking] = { \
    Events.EvHungry: {'state2': States.Hungry, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}}

StateTables.state_transition_table[States.Hungry] = { \
    Events.EvHavePermission: {'state2': States.Eating, 'guard': None, 'transition': UserCode.PickUpForks},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': UserCode.ThankWaiter}}

StateTables.state_transition_table[States.Eating] = { \
    Events.EvFull: {'state2': States.Thinking, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None}}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp, 'do': None, 'exit': None}

StateTables.state_function_table[States.Thinking] = \
    {'enter': UserCode.StartThinkingTimer, 'do': UserCode.Think, 'exit': None}

StateTables.state_function_table[States.Hungry] = \
    {'enter': UserCode.AskPermission, 'do': None, 'exit': None}

StateTables.state_function_table[States.Eating] = \
    {'enter': UserCode.StartEatingTimer, 'do': UserCode.Eat, 'exit': UserCode.PutDownForks}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish, 'do': None, 'exit': None}

# =============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ==========================
# =============================================================================


class Philosopher(UserCode):

    def __init__(self, id=None):
        UserCode.__init__(self, id=id)       # must call super-class
        self.id = id
        self.exit_code = 0          # exit code returned by this philosopher
        self.running = False        # True, simulation is running
        self.has_forks = False      # True, philosopher has possession of both forks


if __name__ == '__main__':

    # Initialize all philosophers
    for id in range(Config.Philosophers):
        philosophers[id] = Philosopher(id=id)

    # Philosophers have been instantiated and threads created
    # Start the simulation, i.e. start all philosophers eating
    for id in range(Config.Philosophers):
        philosophers[id].running = True
        philosophers[id].event_code = Events.EvStart

    # Wait for the simulation to complete
    for loop in range(Config.Dining_Loops):
        time.sleep(1)
        loop += 1
        if loop % 10 is 0:
            logging.info('Iterations: %s' % loop)

    # Tell philosophers to stop
    for id in range(Config.Philosophers):
        philosophers[id].event_code = Events.EvStop

    # Joining threads
    for id in range(Config.Philosophers):
        philosophers[id].thread.join()
    logging.info('All philosophers stopped')

    # Print some statistics of the simulation
    for id in range(Config.Philosophers):
        t = philosophers[id].thinking_seconds
        e = philosophers[id].eating_seconds
        h = int(philosophers[id].hungry_seconds + 0.5)
        total = t + e + h
        print('Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (id, t, e, h, total))
