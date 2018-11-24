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
        self.id = id
        self.startup_state = startup_state
        self.state_function_table = function_table
        self.state_transition_table = transition_table
        self.running = False

        self.current_state = startup_state
        self.enter_func = function_table[startup_state]['enter']
        self.do_func = function_table[startup_state]['do']
        self.thread = Thread(target=self.run)
        self.thread.start()

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
        trans = self.state_transition_table[self.current_state]
        if event not in trans:
            return
        logging.debug("SM[%s] Event %s" % (self.id, event))

        # State exit function
        exit_func = self.state_function_table[self.current_state]['exit']
        if exit_func is not None:
            exit_func(self)

        # State transition function
        trans_func = trans[event]['transition']
        if trans_func is not None:
            trans_func(self)

        # Enter next state
        self.current_state = trans[event]['state2']

        # State enter function
        enter_func = self.state_function_table[self.current_state]['enter']
        if enter_func is not None:
            enter_func(self)

        # Setup do function
        self.do_func = self.state_function_table[self.current_state]['do']
