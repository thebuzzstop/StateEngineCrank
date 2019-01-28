"""
Created on November 12, 2018

@author:    Mark Sawyer
@date:      12-Nov-2018

@package:   StateEngineCrank
@brief:     StateEngineCrank Python class definitions
@details:   State machine class definitions to define StateEngineCrank implementation components.
            Main state machine processing loop.

@copyright: Mark B Sawyer, All Rights Reserved 2018
"""

from threading import (Lock, Thread)
import time

import logging
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logging.debug('Loading modules: %s as %s' % (__file__, __name__))


class StateFunction(object):
    """ StateMachine function definitions """

    def __init__(self, state=None, enter=None, do=None, exit=None):
        self.state = state
        self.enter = enter
        self.do = do
        self.exit = exit
        return {self.state: {'enter': self.enter, 'do': self.do, 'exit': self.exit}}


class StateTransition(object):
    """ StateMachine state transition definitions """

    def __init__(self, event=None, state2=None, guard=None, transition=None):
        self.event = event
        self.state2 = state2
        self.guard = guard
        self.transition = transition
        return {self.event: {'state2': self.state2, 'guard': self.guard, 'transition': self.transition}}


class StateMachine(Thread):
    """ The StateMachine class is the main execution engine """

    def __init__(self, id=None, running=None, startup_state=None, function_table=None, transition_table=None):
        Thread.__init__(self, target=self.run)
        self.id = id
        self.startup_state = startup_state
        self.state_function_table = function_table
        self.state_transition_table = transition_table
        self.running = False
        self.event_code = None
        self.current_state = startup_state
        self.enter_func = function_table[startup_state]['enter']
        self.do_func = function_table[startup_state]['do']
        self.start()

    def run(self):
        logging.debug('SM[%s] StateMachine starting' % self.id)

        # wait until our state machine has been activated
        while not self.running:
            time.sleep(0.1)

        # check for an enter function
        if self.enter_func is not None:
            logging.debug('SM[%s] StateMachine Enter Function %s' % (self.id, self.enter_func))
            self.enter_func(self)

        logging.debug('SM[%s] StateMachine running' % self.id)
        while self.running:
            if self.event_code is not None:
                self.event(self.event_code)
                self.event_code = None
            else:
                self.do()

    def do(self):
        # execute current state 'do' function if it exists
        if self.do_func is not None:
            self.do_func(self)
        else:
            logging.debug('SM[%s] Empty do function in %s' % (self.id, self.current_state))

    def event(self, event):
        # lookup current state in transitions table and check for any transitions
        # associated with the newly received event
        transition_table = self.state_transition_table[self.current_state]
        if event not in transition_table:
            return
        transition = None

        # Event entries in the transition table can be either a single transition with a
        # guard function or a list of transitions, each with a guard function. The first
        # transition with a guard function that is 'None' or returns 'True' will be taken.

        # Test if event entry is a single transition
        if isinstance(transition_table[event], dict):
            # State guard function
            guard_func = transition_table[event]['guard']
            if guard_func is not None:
                if not guard_func(self):
                    return
            transition = transition_table[event]
        # Test if event entry is a list of transitions
        elif isinstance(transition_table[event], list):
            for trans in transition_table[event]:
                guard_func = trans['guard']
                if guard_func is not None:
                    if guard_func(self):
                        transition = trans
                        break
        # No entry in table for this event
        else:
            return

        # Just exit if we did not find a valid transition
        if transition is None:
            return

        # either no guard function or guard function is true
        logging.debug("SM[%s] Event %s" % (self.id, event))

        # Execute state exit function if it is not None
        exit_func = self.state_function_table[self.current_state]['exit']
        if exit_func is not None:
            exit_func(self)

        # Execute state transition function if it is not None
        if transition['transition'] is not None:
            transition['transition'](self)

        # Enter next state
        self.current_state = transition['state2']

        # Execute state enter function if it is not None
        enter_func = self.state_function_table[self.current_state]['enter']
        if enter_func is not None:
            enter_func(self)

        # Setup do function
        self.do_func = self.state_function_table[self.current_state]['do']
