""" StateEngineCrank.PyState

State machine class definitions to define StateEngineCrank implementation components.
Main state machine processing loop.
"""
import enum
import time
import queue
import mvc
import Defines


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class StateMachineEvent(Borg):
    """ Events that are posted as notifications to anyone
        that wants to know what we are doing """

    class SmEvents(enum.Enum):
        START_EXECUTION, STOP_EXECUTION, \
            POST_EVENT, VALID_EVENT, EVENT_NOT_FOUND, \
            GUARD_FUNCTION, GUARD_TRUE, GUARD_FALSE, \
            STATE_TRANSITION, TRANSITION_FUNCTION, NO_TRANSITION, \
            ENTER_FUNCTION, DO_FUNCTION, EXIT_FUNCTION \
            = range(14)

    def __init__(self):
        Borg.__init__(self)
        if len(self._shared_state) > 0:
            return
        self.class_name = 'SM'
        self.events = mvc.Event()
        self.events.register_class(self.class_name)
        for sme in StateMachineEvent.SmEvents:
            self.events.register_event(class_name=self.class_name, actor_name=None, event=sme,
                                       event_type='model', text=str(sme.name))


# call the StateMachineEvent constructor to register SM events
StateMachineEvent()


class StateFunction(object):
    """ StateMachine function definitions """

    def __init__(self, state=None, enter=None, do=None, exit_=None):
        """ Constructor

            :param state: state to create
            :param enter: enter function for the state
            :param do: do function for the state
            :param exit_: exit function for the state
        """
        self.state = state
        self.enter = enter
        self.do = do
        self.exit = exit_


class StateTransition(object):
    """ StateMachine state transition definitions """

    def __init__(self, event=None, state2=None, guard=None, transition=None):
        """ Constructor

            :param event: transition event trigger
            :param state2: transition destination state
            :param guard: function to test if transition can be taken
            :param transition: function to be executed when the transition is taken
        """
        self.event = event              #: transition event trigger
        self.state2 = state2            #: transition destination state
        self.guard = guard              #: transition guard function
        self.transition = transition    #: transition function


class StateMachine(mvc.Model):
    """ The StateMachine class is the main execution engine """

    def cleanup(self):
        """ Do some cleanup """
        self.sm_events.events.unregister_actor(actor_name=self.name)
        self.mvc_events.unregister_actor(actor_name=self.name)

    def __init__(self, sm_id=None, name=None, running=False, startup_state=None,
                 function_table=None, transition_table=None):
        """ Constructor

            :param sm_id: state machine ID
            :param name: state machine name
            :param running: flag indicates state machine is running
            :param startup_state: state machine starting state
            :param function_table: state machine function table
            :param transition_table: state machine transition table
        """
        mvc.Model.__init__(self, name=name, running=running, target=self.run)
        self.id = sm_id
        self.name = name
        self.sm_events = StateMachineEvent()
        self.sm_events.events.register_actor(class_name=self.sm_events.class_name, actor_name=self.name)
        self.mvc_events = mvc.Event()
        self.mvc_events.register_actor(class_name='mvc', actor_name=self.name)
        self.startup_state = startup_state
        self.state_function_table = function_table
        self.state_transition_table = transition_table
        self.event_queue = queue.Queue()
        self.current_state = startup_state
        self.enter_func = function_table[startup_state]['enter']
        self.do_func = function_table[startup_state]['do']
        self.logger('%s StateMachine thread start' % self.name)
        self.thread.start()

    def run(self):
        """ Function to run the state machine.

            * Starts running when the **running** boolean is True
            * Stops running when the **running** boolean is False
        """
        # wait until our state machine has been activated
        self.logger('%s StateMachine activating [%s]' % (self.name, self.current_state))
        while not self.running:
            time.sleep(Defines.Times.Starting)
        self.logger('%s StateMachine activated [%s]' % (self.name, self.current_state))

        # check for an enter function
        if self.enter_func is not None:
            self.logger('%s StateMachine Enter Function [%s]' % (self.name, self.current_state))
            self.enter_func(self)
            # self.logger('%s StateMachine Enter+ Function [%s]' % (self.name, self.current_state))

        self.logger('%s StateMachine running [%s]' % (self.name, self.current_state))
        while self.running:
            if self.pause:
                time.sleep(Defines.Times.Pausing)
                if not self.step():
                    continue
            if not self.event_queue.empty():
                self.event(self.event_queue.get_nowait())
            else:
                self.do()
        self.logger('%s StateMachine exiting [%s]' % (self.name, self.current_state))

    def do(self):
        """ Execute current state **do** function if it exists """
        if self.do_func is not None:
            self.do_func(self)
        time.sleep(Defines.Times.Do)

    def post_event(self, event):
        """ Posts **event** to the state machine event queue

            :param event: event to post
        """
        self.event_queue.put_nowait(event)

    def event(self, event):
        """ Perform state machine **event** processing

            Handles:
                * execution of state transitions
                * transition guard function tests
                * transition function execution
                * state exit function execution
                * state enter function execution
                * sets up do function for next state

            :param event : event to process
        """
        if event is None:
            return

        # notify any who are registered with us for events
        text = '%s %s [%s]' % (self.name, event, self.current_state)
        self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                               event=StateMachineEvent.SmEvents.POST_EVENT, text=text, data=event))

        # lookup current state in transitions table and check for any transitions
        # associated with the newly received event
        transition_table = self.state_transition_table[self.current_state]
        if event not in transition_table:
            return
        transition = None
        # text = '%s-SM Event+ %s' % (self.name, event)
        # self.logger(text)

        # Event entries in the transition table can be either a single transition with a
        # guard function or a list of transitions, each with a guard function. The first
        # transition with a guard function that is 'None' or returns 'True' will be taken.

        # Test if event entry is a single transition
        if isinstance(transition_table[event], dict):
            # State guard function
            guard_func = transition_table[event]['guard']
            if guard_func is not None:
                text = '%s %s [%s]' % (self.name, event, self.current_state)
                self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                       event=StateMachineEvent.SmEvents.GUARD_FUNCTION, text=text))
                if not guard_func(self):
                    self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                           event=StateMachineEvent.SmEvents.GUARD_FALSE, text=text))
                    return
            self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                   event=StateMachineEvent.SmEvents.GUARD_TRUE, text=text))
            transition = transition_table[event]

        # Test if event entry is a list of transitions
        elif isinstance(transition_table[event], list):
            for trans in transition_table[event]:
                guard_func = trans['guard']
                text = '%s %s [%s]' % (self.name, event, self.current_state)
                if guard_func is not None:
                    self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                           event=StateMachineEvent.SmEvents.GUARD_FUNCTION, text=text))
                    if guard_func(self):
                        transition = trans
                        self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                               event=StateMachineEvent.SmEvents.GUARD_TRUE, text=text))
                        break
                    self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                           event=StateMachineEvent.SmEvents.GUARD_FALSE, text=text))

        # No entry in table for this event
        else:
            text = '%s %s [%s]' % (self.name, event, self.current_state)
            self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                   event=StateMachineEvent.SmEvents.EVENT_NOT_FOUND, text=text))
            return

        # Just exit if we did not find a valid transition
        if transition is None:
            text = '%s %s [%s]' % (self.name, event, self.current_state)
            self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                   event=StateMachineEvent.SmEvents.NO_TRANSITION, text=text))
            return

        # Execute state exit function if it is not None
        exit_func = self.state_function_table[self.current_state]['exit']
        if exit_func is not None:
            text = '%s %s [%s]' % (self.name, event, self.current_state)
            self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                   event=StateMachineEvent.SmEvents.EXIT_FUNCTION, text=text))
            exit_func(self)

        # Execute state transition function if it is not None
        if transition['transition'] is not None:
            text = '%s %s [%s]' % (self.name, event, self.current_state)
            self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                   event=StateMachineEvent.SmEvents.TRANSITION_FUNCTION, text=text))
            transition['transition'](self)

        # Enter next state
        self.current_state = transition['state2']
        text = '%s %s [%s]' % (self.name, event, self.current_state)
        self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                               event=StateMachineEvent.SmEvents.STATE_TRANSITION, text=text,
                                               data=transition['state2']))

        # Execute state enter function if it is not None
        enter_func = self.state_function_table[self.current_state]['enter']
        if enter_func is not None:
            text = '%s %s [%s]' % (self.name, event, self.current_state)
            self.notify(self.sm_events.events.post(class_name='SM', actor_name=self.name, user_id=self.id,
                                                   event=StateMachineEvent.SmEvents.ENTER_FUNCTION, text=text))
            enter_func(self)

        # Setup do function
        self.do_func = self.state_function_table[self.current_state]['do']

    def update(self, event):
        """ Called by View/Controller to tell us to update
            We currently have nothing to do.

            :param event: View/Controller event to be processed
        """
        pass
