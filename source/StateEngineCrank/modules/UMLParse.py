""" StateEngineCrank UML Parsing Module

    Locates UML in source code and parses for states, transitions
    events, guards, transfer functions producing the UML data
    structures containing all of the information required for the
    rest of the modules for code generation.

    Example::

        Typical syntax for a state transition

        State1 --> State2 : Event [Guard] / Function

        [Guard] syntax rules:

            1) Guard may be a compound logic equation
                e.g. Foo && Goo || Moo
                Note: ()'s if specified will be removed
            2) &&'s, ||'s and !'s are replaced with '_AND_', '_OR_' and 'NOT_'
                respectively
                e.g. Foo && Goo || !Moo ==> Foo_AND_Goo_OR_NOT_Moo
            3) Spaces are replaced with '_' to concatenate logic expressions
                e.g. [FooGuard AND GooGuard] ==> [FooGuard_AND_GooGuard]
                This will allow for the creation of a hybrid guard function
                which will perform any required logical operations.

        @startuml

            [*] --> FindStartUML

            FindStartUML --> WrapUp : EOF
            FindStartUML --> Parse  : StartUML
            FindStartUML : entry : Enter
            FindStartUML : do    : Do
            FindStartUML : exit  : Exit

            Parse --> WrapUp     : EndUML || EOF
            Parse --> Transition : EvState_New
            Parse --> Transition : EvState_Self
            Parse --> Guard      : EvGuard
            Parse --> Event      : EvEvent
            Parse : entry : Enter
            Parse : do    : Do
            Parse : exit  : Exit

            Transition --> Parse  : EvContinue
            Transition --> WrapUp : EndUML || EOF
            Transition : enter : Enter
            Transition : do    : Do
            Transition : exit  : Exit

            Guard --> Parse  : EvContinue
            Guard --> WrapUp : EndUML || EOF
            Guard : entry : Enter
            Guard : do    : Do
            Guard : exit  : Exit

            Event --> Parse  : EvContinue
            Event --> WrapUp : EndUML || EOF
            Event : entry : Enter
            Event : do    : Do
            Event : exit  : Exit

            WrapUp --> Error : GotError
            WrapUp --> [*]   : NoErrors
            WrapUp : entry : Enter
            WrapUp : do    : Do
            WrapUp : exit  : Exit

            Error --> [*]
            Error : enter : Enter
            Error : do    : Do
            Error : exit  : Exit

        @enduml
"""

# System imports
import logging
import re
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports
import modules.ErrorHandling  # noqa 408
import modules.FileSupport  # noqa 408
import modules.Singleton  # noqa 408


class UML(modules.Singleton.Singleton):
    """
        **Overview**

        Locates UML in source code and parses for states, transitions
        events, guards, transfer functions producing the UML data
        structures containing all of the information required for the
        rest of the modules for code generation.

        **Regular expression string parsing**

        This module is responsible for parsing UML.
        There are two (2) basic tasks related to parsing the UML:

            1) Parse State transitions (e.g. State1 --> State2)
            2) Parse State functions (enter/do/exit)

        **Fully specified state transition**::

            State1 --> State2 : Event [Guard] / Function()

        Not all parts are necessary::

            State1 --> State2 : Event  # all state and event parts must be present
            [Guard]                    # optional, guards
            [Guard()]                  # optional, guards, ()'s may be present
            / Function                 # optional, transition function
            / Function()               # optional, transition function, ()'s may be present

        Regular expressions required to support all contingencies::

            [0] State1
            [1] -->
            [2] State2
            [3] :
            [4] Event
            [5] [Guard]
            [6] /
            [7] Function
            [5] [Guard]
            [5] /
            [6] Function

        **Fully specified Enter/Do/Exit functions**

        *Note: enter/do/exit functions are optional*::

            State1 : enter : Enter()
            State1 : do    : Do()
            State1 : exit  : Exit()
    """

    # Some string constants we either look for or use
    START_UML = '@startuml'
    """
        [*] --> DummyUML
    """
    END_UML = '@enduml'

    INITIAL_STATE = '[*]'
    INITIAL_STATE_LABEL = 'InitialState'

    FINAL_STATE = '[*]'
    FINAL_STATE_LABEL = 'FinalState'

    # =========================================================================
    def __init__(self):
        self.error = modules.ErrorHandling.Error()  #: establish error handling (errors)
        self.warn = modules.ErrorHandling.Warn()    #: establish error handling (warnings)
        self.file = modules.FileSupport.File()      #: establish file handling

        self.seqid = -1             #: used during debug as a sequence ID for UML lines read
        self.uml_start_index = -1   #: source file index of uml start
        self.uml_end_index = -1     #: source file index of uml end

        self.statemachine = []      #: all state machine records
        self.transitions = []       #: list of transitions (state changes)

        self.states1 = []           #: list of states, transition origin
        self.states2 = []           #: list of states, transition destination
        self.events = []            #: list of events, transition event functions
        self.guards = []            #: list of guards, transition guard functions
        self.trans = []             #: list of transitions, transition functions

        self.guard_funcs = []       #: list of function names, guards
        self.trans_funcs = []       #: list of function names, transitions

        self.states = []            #: list of states, associated with enter/do/exit
        self.enters = {}            #: list of functions, enter
        self.dos = {}               #: list of functions, do
        self.exits = {}             #: list of functions, exit

        # RE search/match result strings (state transitions)
        self.state1 = None
        self.state2 = None
        self.event = None
        self.guard = None
        self.tfunc = None

        # RE search/match result strings (enter/do/exit)
        self.state = None
        self.enter = None
        self.do = None
        self.exit = None

    # =========================================================================
    def init(self):
        """ Initialization function called prior to parsing. """
        self.seqid = -1             #: used during debug as a sequence ID for UML lines read
        self.uml_start_index = -1   #: source file index of uml start
        self.uml_end_index = -1     #: source file index of uml end

        self.statemachine = []      #: all state machine records
        self.transitions = []       #: list of transitions (state changes)

        self.states1 = []           #: list of states, transition origin
        self.states2 = []           #: list of states, transition destination
        self.guards = []            #: list of guards, transition guard functions
        self.trans = []             #: list of transitions, transition functions

        self.guard_funcs = []       #: list of function names, guards
        self.trans_funcs = []       #: list of function names, transitions
        self.do_funcs = []          #: list of function names, dos
        self.enter_funcs = []       #: list of function names, enters
        self.exit_funcs = []        #: list of function names, exits

        self.enter_func_states = {} #: dictionary of enter function states
        self.do_func_states = {}    #: dictionary of do function states
        self.exit_func_states = {}  #: dictionary of exit function states

        self.states = []            #: list of states, associated with enter/do/exit
        self.enters = {}            #: dictionary of functions, enter
        self.dos = {}               #: dictionary of functions, do
        self.exits = {}             #: dictionary of functions, exit

        # RE search/match result strings (state transitions)
        self.state1 = None
        self.state2 = None
        self.event = None
        self.guard = None
        self.tfunc = None

        # RE search/match result strings (enter/do/exit)
        self.state = None
        self.enter = None
        self.do = None
        self.exit = None

    # =========================================================================
    def is_guard_func(self, func):
        """ **Guard** function test

            Parameters:
                func : text to test

            Returns:
                True : 'func' is a Guard function
        """
        return func in self.guard_funcs

    # =========================================================================
    def is_enter_func(self, func):
        """ **Enter** function test

            Parameters:
                func : text to test

            Returns:
                True : 'func' is an Enter function
        """
        return func in self.enter_funcs

    # =========================================================================
    def is_do_func(self, func):
        """ **Do** function test

            Parameters:
                func : text to test

            Returns
                True : 'func' is a **Do** function
        """
        return func in self.do_funcs

    # =========================================================================
    def is_exit_func(self, func):
        """ **Exit** function test

            Parameters:
                func : text to test

            Returns:
                True : 'func' is an **Exit** function
        """
        return func in self.exit_funcs

    # =========================================================================
    def is_trans_func(self, func):
        """ **Transition** function test

            Parameters:
                func : text to test

            Returns:
                True : 'func' is a **Transition** function
        """
        return func in self.trans_funcs

    # =========================================================================
    def add_isuml(self):
        """ Informational only, no processing required. """
        pass    # info, no processing required

    def add_lineno(self):
        """ Informational only, no processing required. """
        pass    # info, no processing required

    def add_text(self):
        """ Informational only, no processing required. """
        pass    # info, no processing required

    # =========================================================================
    def add_state1(self, state):
        """ Add **state** to list of known origination states

            Parameters:
                 state : **state** to add to **state1[]**
        """
        if state not in self.states1:
            self.states1.append(state)
            self.add_state(state)

    # =========================================================================
    def add_state2(self, state):
        """ Add **state** to list of known destination states

            Parameters:
                state : **state** to add to **state2[]**
        """
        if state not in self.states2:
            self.states2.append(state)
            self.add_state(state)

    # =========================================================================
    def add_event(self, func):
        """ Add **func** to list of known **events**

            Parameters:
                func : **event** function to add to **events[]**
        """
        if func not in self.events:
            self.events.append(func)

    # =========================================================================
    def add_guard(self, state1, state2, event, func):
        """ Add **func** to list of known **guards**

            Parameters:
                state1 : starting state
                state2 : destination state
                event : trigger event
                func : **guard** function
        """
        self.guards.append({"state1": state1, "state2": state2, "event": event, "guard": func})
        if func not in self.guard_funcs:
            self.guard_funcs.append(func)

    # =========================================================================
    def add_trans(self, state1, state2, event, func):
        """ Add **func** to list of known **transitions**

            Parameters:
                state1 : starting state
                state2 : destination state
                event : trigger event
                func : **transition** function
        """
        self.trans.append({"state1": state1, "state2": state2, "event": event, "tfunc": func})
        if func not in self.trans_funcs:
            self.trans_funcs.append(func)

    # =========================================================================
    def add_state(self, state):
        """ Add **state** to list of known **states**

            Parameters:
                state : state to add
        """
        # don't add default state engine states
        if not (state == self.INITIAL_STATE or state == self.FINAL_STATE):
            if state not in self.states:
                self.states.append(state)

    # ==============================
    # state enter/do/exit functions
    # ==============================

    #: Regular Expression logic operation substitutions
    RE_SUBS_DICT = {
        r' && ':    r'_AND_',
        r' || ':    r'_OR_',
        r'!':       r'NOT_',
        r'()':      r'',
        r'( )':     r'',
        }

    # =========================================================================
    def mangle_guard(self, text):
        """ Mangle a guard string according to our rules.
            Dictionary replacement of text.

            Parameters:
                  text : guard text string to be processed
            Returns:
                  mangled guard text
        """
        for token in self.RE_SUBS_DICT:
            text = text.replace(token, self.RE_SUBS_DICT[token])
        return text

    # =========================================================================
    @staticmethod
    def mangle(string1, string2):
        """ Mangle two strings into a single string.

            Parameters:
                string1 : first string to be mangled
                string2 : second string to be mangled
            Returns:
                string1_string2
        """
        return string1 + '_' + string2

    # =========================================================================
    def add_enter(self, state, func):
        """ Add state **enter** function to list.

            Parameters:
                state : current state being processed
                func : current function being processed
        """
        _mangle = self.mangle(state, func)
        if _mangle not in self.enters:
            self.enters.update({state: _mangle})
            self.enter_funcs.append(_mangle)
            self.enter_func_states[_mangle] = state

    # =========================================================================
    def add_do(self, state, func):
        """ Add state **do** function to list.

            Parameters:
                state : current state being processed
                func : current function being processed
        """
        _mangle = self.mangle(state, func)
        if _mangle not in self.dos:
            self.dos.update({state: _mangle})
            self.do_funcs.append(_mangle)
            self.do_func_states[_mangle] = state

    # =========================================================================
    def add_exit(self, state, func):
        """ Add state **exit** function to list.

            Parameters:
                state : current state being processed
                func : current function being processed
        """
        _mangle = self.mangle(state, func)
        if _mangle not in self.exits:
            self.exits.update({state: _mangle})
            self.exit_funcs.append(_mangle)
            self.exit_func_states[_mangle] = state

    # =========================================================================
    #: Dictionary of strings used to invoke UML handlers while parsing
    UML_PARSE = {
        'isuml':    add_isuml,
        'lineno':   add_lineno,
        'text':     add_text,
        'state':    add_state,
        'state1':   add_state1,
        'state2':   add_state2,
        'event':    add_event,
        'guard':    add_guard,
        'trans':    add_trans,
        'enter':    add_enter,
        'do':       add_do,
        'exit':     add_exit
        }

    # =========================================================================
    def find_start_plant_uml(self):
        """ Find Plant UML start in source file.
            Note that not finding the UML start is not an error.
            A warning will be issued if enabled (verbosity).

            Returns:
                True - start plant-uml found
        """
        lineno = 0
        found_status = False
        while True:
            line = self.file.get_line(lineno)
            if line[0] == self.file.EOF:
                self.warn.uml_not_found(self.START_UML)
                break
            if line[1] == self.START_UML:
                self.uml_start_index = line[0]
                found_status = True
                break
            lineno += 1
        return found_status

    # =========================================================================
    def find_end_plant_uml(self):
        """ Find Plant UML end in source file.
            It is ASSuMEd that if we are searching for the UML END then
            we must have found the UML START.
            Unlike UML START, no UML END is therefore an ERROR.

            Returns:
                True - end plant-uml found
        """
        lineno = 0
        found_status = False
        while True:
            line = self.file.get_line(lineno)
            if line[0] == self.file.EOF:
                self.error.uml_not_found(self.END_UML)
                break
            if line[1] == self.END_UML:
                self.uml_end_index = line[0]
                found_status = True
                break
            lineno += 1

        # sanity check for start > end
        if self.uml_start_index < self.uml_end_index:
            logging.debug('UML start/end: %s/%s' % (self.uml_start_index, self.uml_end_index))
        else:
            self.error.invalid_start_end(self.uml_start_index, self.uml_end_index)
            exit()

        return found_status

    # =========================================================================
    def parse_plant_uml(self):
        """ Parse Plant UML lines from source file. """
        # parse UML from start to end
        for line in range(self.uml_start_index, self.uml_end_index+1):
            text = self.file.get_line_text(line)

            # make logic operator substitutions
            text = self.mangle_guard(text)

            # process each line of text
            if self.is_uml(text):
                # enter valid UML into our dictionary
                logging.debug('UML: %s' % text)
                self.statemachine.append({
                       'isuml': True,
                       'lineno': line,
                       'text': text,
                       'state1': self.state1,
                       'state2': self.state2,
                       'event': self.event,
                       'guard': self.guard,
                       'trans': self.tfunc,
                       'state': self.state,
                       'enter': self.enter,
                       'do': self.do,
                       'exit': self.exit,
                       })
            else:
                # ignore anything we don't grok
                logging.debug('IGN: %s' % text)

        # display what we just parsed
        logging.debug('Parse_PlantUML Length: %s' % len(self.statemachine))

        # process each line of the state machine
        for i in range(len(self.statemachine)):
            logging.debug('statemachine: %s' % self.statemachine[i])
            if 'isuml' in self.statemachine[i]:
                logging.debug('UML[%s] %s' % (i, self.statemachine[i]))

                self.state1 = self.statemachine[i]['state1']
                self.state2 = self.statemachine[i]['state2']
                self.event = self.statemachine[i]['event']
                self.guard = self.statemachine[i]['guard']
                self.tfunc = self.statemachine[i]['trans']

                if self.state1 is not None:
                    self.UML_PARSE['state1'](self, self.state1)
                if self.state2 is not None:
                    self.UML_PARSE['state2'](self, self.state2)
                if self.event is not None:
                    self.UML_PARSE['event'](self, self.event)
                if self.guard is not None:
                    self.UML_PARSE['guard'](self, self.state1, self.state2, self.event, self.guard)
                if self.tfunc is not None:
                    self.UML_PARSE['trans'](self, self.state1, self.state2, self.event, self.tfunc)

                # sanity check state transitions
                # all must be None or NOT none
                trans = 0
                if self.state1 is not None:
                    trans = trans + 1
                if self.state2 is not None:
                    trans = trans + 1
                if self.event is not None:
                    trans = trans + 1
                if trans != 0 and trans != 3:
                    if self.state1 != self.INITIAL_STATE:
                        logging.debug('Transition Check: %s / %s / %s' % (self.state1, self.state2, self.event))

                # substitute labels for initial and final states
                if self.state1 == self.INITIAL_STATE:
                    self.state1 = self.INITIAL_STATE_LABEL
                if self.state2 == self.FINAL_STATE:
                    self.state2 = self.FINAL_STATE_LABEL

                # record details of transitions
                if self.state1 is not None and self.state2 is not None:
                    self.transitions.append({
                       'state1': self.state1,
                       'state2': self.state2,
                       'event': self.event,
                       'guard': self.guard,
                       'trans': self.tfunc,
                       })

                self.state = self.statemachine[i]['state']
                self.enter = self.statemachine[i]['enter']
                self.do = self.statemachine[i]['do']
                self.exit = self.statemachine[i]['exit']

                if self.state is not None:
                    self.UML_PARSE['state'](self, self.state)

                    # only parse enter/do/exit if state is valid
                    if self.enter is not None:
                        self.UML_PARSE['enter'](self, self.state, self.enter)
                    if self.do is not None:
                        self.UML_PARSE['do'](self, self.state, self.do)
                    if self.exit is not None:
                        self.UML_PARSE['exit'](self, self.state, self.exit)
            else:
                logging.debug('Skipping %s: %s' % (i, self.statemachine[i]))

        logging.debug('Parse_PlantUML Done')

    # =========================================================================
    # Regular Expression search/match strings
    # Used for parsing state transitions
    RE_STATE1 = r'(?P<state1>([a-zA-Z_]+[a-zA-Z0-9_]*)|(\[\*\]))'
    RE_STATE2 = r'(?P<state2>([a-zA-Z_]+[a-zA-Z0-9_]*)|(\[\*\]))'
    RE_TRANS = r' \-\-\> '
    RE_COLON = r' \:'
    RE_EVENT = r' (?P<event>[a-zA-Z_]+[a-zA-Z0-9_]*)'
    RE_GUARD = r' \[(?P<guard>[a-zA-Z_]+[a-zA-Z0-9_]*)\]'
    RE_FUNC = r' (?P<func>[a-zA-Z_]+[a-zA-Z0-9_]*)'
    RE_SLASH = r' \/'

    # state1 --> state2 : Event [Guard] / Transition
    re_st1_st2_event_guard_func = re.compile(RE_STATE1+RE_TRANS+RE_STATE2+RE_COLON+RE_EVENT+RE_GUARD+RE_SLASH+RE_FUNC)

    # state1 --> state2 : Event / Transition
    re_st1_st2_event_func = re.compile(RE_STATE1+RE_TRANS+RE_STATE2+RE_COLON+RE_EVENT+RE_SLASH+RE_FUNC)

    # state1 --> state2 : Event [Guard]
    re_st1_st2_event_guard = re.compile(RE_STATE1+RE_TRANS+RE_STATE2+RE_COLON+RE_EVENT+RE_GUARD)

    # state1 --> state2 : Event
    re_st1_st2_event = re.compile(RE_STATE1+RE_TRANS+RE_STATE2+RE_COLON+RE_EVENT)

    # state1 --> state2
    re_st1_st2 = re.compile(RE_STATE1+RE_TRANS+RE_STATE2)

    # Regular Expression search/match strings
    # Used for parsing Enter/Do/Exit functions

    RE_STATE = r'(?P<state>[a-zA-Z_]+[a-zA-Z0-9_]*)'
    RE_ENTER = r' \: [eE]nter \:'
    RE_ENTRY = r' \: [eE]ntry \:'
    RE_DO = r' \: [dD]o \:'
    RE_EXIT = r' \: [eE]xit \:'

    re_enter = re.compile(RE_STATE + RE_ENTER + RE_FUNC)    # state : enter : Enter
    re_entry = re.compile(RE_STATE + RE_ENTRY + RE_FUNC)    # state : entry : Entry
    re_do = re.compile(RE_STATE + RE_DO + RE_FUNC)          # state : do    : Do
    re_exit = re.compile(RE_STATE + RE_EXIT + RE_FUNC)      # state : exit  : Exit

    # =========================================================================
    def dump_uml(self):
        """ Dump current state of UML class variables. """
        logging.debug('State1 : %s' % self.states1)
        logging.debug('State2 : %s' % self.states2)
        logging.debug('Events : %s' % self.events)
        logging.debug('Guards : %s' % self.guards)
        logging.debug('Trans  : %s' % self.trans)

        logging.debug('gFuncs : %s' % self.guard_funcs)
        logging.debug('tFuncs : %s' % self.trans_funcs)

        logging.debug('States : %s' % self.states)
        logging.debug('Enters : %s' % self.enters)
        logging.debug('Dos    : %s' % self.dos)
        logging.debug('Exits  : %s' % self.exits)

        for _transition in self.transitions:
            logging.debug('Transition : %s' % _transition)

    # =========================================================================
    def is_uml(self, text):
        """ Verify text is valid UML.

            Parameters:
                text : text to be tested for valid UML

            Returns:
                True : text is valid UML
                False : text is not valid UML
        """
        # bump / display sequence id
        self.seqid += 1
        # self.debug.set_seq_id(self.seqid)

        # RE search/match result strings (state transitions)
        self.state1 = None
        self.state2 = None
        self.event = None
        self.guard = None
        self.tfunc = None

        # RE search/match result strings (enter/do/exit)
        self.state = None
        self.enter = None
        self.do = None
        self.exit = None

        # check for uml start/end tags
        if (text == self.START_UML) | (text == self.END_UML):
            return True

        # state1 --> state2 : Event [Guard] / Transition
        match = self.re_st1_st2_event_guard_func.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state1 = match.group('state1')
            self.state2 = match.group('state2')
            self.event = match.group('event')
            self.guard = match.group('guard')
            self.tfunc = match.group('func')
            return True

        # state1 --> state2 : Event [Guard]
        match = self.re_st1_st2_event_guard.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state1 = match.group('state1')
            self.state2 = match.group('state2')
            self.event = match.group('event')
            self.guard = match.group('guard')
            return True

        # state1 --> state2 : Event / Transition
        match = self.re_st1_st2_event_func.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state1 = match.group('state1')
            self.state2 = match.group('state2')
            self.event = match.group('event')
            self.tfunc = match.group('func')
            return True

        # state1 --> state2 : Event
        match = self.re_st1_st2_event.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state1 = match.group('state1')
            self.state2 = match.group('state2')
            self.event = match.group('event')
            return True

        # state1 --> state2
        match = self.re_st1_st2.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state1 = match.group('state1')
            self.state2 = match.group('state2')
            return True

        # state : enter : enter
        match = self.re_enter.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state = match.group('state')
            self.enter = match.group('func')
            return True

        # state : entry : enter
        match = self.re_entry.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state = match.group('state')
            self.enter = match.group('func')
            return True

        # state : do : do
        match = self.re_do.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state = match.group('state')
            self.do = match.group('func')
            return True

        # state : exit : exit
        match = self.re_exit.match(text)
        if match is not None:
            logging.debug('SUCCESS: %s' % text)
            self.state = match.group('state')
            self.exit = match.group('func')
            return True

        # failed to find a Match
        if len(text) > 0:
            logging.debug('FAILURE: %s' % text)
            exit(1)
        return False
