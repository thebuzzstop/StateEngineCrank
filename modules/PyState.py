"""
Created on November 12, 2018

@author:    Mark Sawyer
@date:      12-Nov-2018

@package:   StateEngineCrank
@brief:     StateEngineCrank Python class definitions
@details:   Class definitions to define StateEngineCrank implementation components

@copyright: Mark B Sawyer, All Rights Reserved 2018
"""

from enum import Enum


# state record definition
class State(object):
    def __init__(self):
        self._state = None
        self._enter = None
        self._do = None
        self._exit = None

    def state(self, state=None, enter_func=None, do_func=None, exit_func=None):
        self._state = state
        self._enter = enter_func
        self._do = do_func
        self._exit = exit_func


class Event(object):
    def __init__(self):
        self._event = None

    def event(self, event=None):
        self._event = event


class Guard(object):
    def __init__(self):
        self._guard = None

    def guard(self, guard=None):
        self._guard = guard


class Transition(object):
    def __init__(self):
        self._transition = None

    def transition(self, transition_func=None):
        self._transition = transition_func


class Enter(object):
    def __init__(self):
        self._enter = None

    def enter(self, enter_func=None):
        self._enter = enter_func


class Exit(object):
    def __init__(self):
        self._exit = None

    def exit(self, exit_func=None):
        self._exit = exit_func


class Do(object):
    def __init__(self):
        self._do = None

    def do(self, do_func=None):
        self._do = do_func


class StateRecord(object):

    def __init__(self):
        self.record = {
            'state1': None, 'state2': None, 'event': None,
            'enter': None, 'do': None, 'exit': None, 'transition': None
        }

    def state_record(self, state1=None, state2=None, event=None,
                     enter_func=None, do_func=None, exit_func=None, transition_func=None):

        self.record['state1'] = state1
        self.record['state2'] = state2
        self.record['event'] = event
        self.record['enter'] = enter_func
        self.record['do'] = do_func
        self.record['exit'] = exit_func
        self.record['transition'] = transition_func


class StateMachine(object):

    def __init__(self):
        pass

    def state_machine(self):
        pass
