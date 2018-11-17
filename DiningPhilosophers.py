#!/usr/bin/env python
"""
Created on November 12, 2018

@author:    Mark Sawyer
@date:      12-Nov-2018

@package:   DiningPhilosophers
@brief:     Main entry module
@details:   Main module for the modules utility

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
# System imports
import logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

from enum import Enum

# Project imports
import modules.PyState

"""
    @startuml

         [*] --> StartUp

    StartUp --> Thinking : EvStart
    StartUp --> Finish : EvStop
    StartUp : enter : StartUp()

    Thinking --> Hungry : EvHungry
    Thinking --> Finish : EvStop
    Thinking : enter : StartThinkingTimer()
    Thinking : do    : Think()

    Hungry --> Eating : EvHaveForks
    Hungry --> Finish : EvStop
    Hungry : do   : AskPermission()
    Hungry : exit : PickUpForks()

    Eating --> Thinking : EvFull
    Eating --> Finish : EvStop
    Eating : enter : StartEatingTimer()
    Eating : do    : Eat()
    Eating : exit  : PutDownForks()

    Finish : do : Finish()

    @enduml
"""


class States(Enum):
    StartUp = 1
    Thinking = 2
    Hungry = 3
    Eating = 4
    Finish = 5


class Events(Enum):
    EvStart = 1
    EvHungry = 2
    EvFull = 3
    EvStop = 4


def StartUp():
    pass


def StartThinkingTimer():
    pass


def Think():
    pass


def AskPermission():
    pass


def PickUpForks():
    pass


def StartEatingTimer():
    pass


def Eat():
    pass


def PutDownForks():
    pass


state_transition_table = [
    {'state1': States.StartUp, 'state2': States.Thinking, 'event': Events.EvStart, 'guard': None, 'transition': None},
    {'state1': States.StartUp, 'state2': States.Finish, 'event': Events.EvStop, 'guard': None, 'transition': None},
    {'state1': States.Thinking, 'state2': States.Hungry, 'event': Events.EvHungry, 'guard': None, 'transition': None},
    {'state1': States.Thinking, 'state2': States.Finish, 'event': Events.EvStop, 'guard': None, 'transition': None},
    {'state1': States.Hungry, 'state2': States.Eating, 'event': Events.EvHaveForks, 'guard': None, 'transition': None},
    {'state1': States.Hungry, 'state2': States.Finish, 'event': Events.EvStop, 'guard': None, 'transition': None},
    {'state1': States.Eating, 'state2': States.Thinking, 'event': Events.EvFull, 'guard': None, 'transition': None},
    {'state1': States.Eating, 'state2': States.Finish, 'event': Events.EvStop, 'guard': None, 'transition': None}
]


state_function_table = [
    {States.Startup: {'enter': StartUp, 'do': None, 'exit': None}},
    {States.Thinking: {'enter': StartThinkingTimer, 'do': Think, 'exit': None}},
    {States.Hungry: {'enter': None, 'do': AskPermission, 'exit': PickUpForks}},
    {States.Eating: {'enter': StartEatingTimer, 'do': Eat, 'exit': PutDownForks}}
]
