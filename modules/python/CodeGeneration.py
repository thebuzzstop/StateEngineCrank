"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     Code Generation (Python State Engine)
@details:   Code Generation for StateEngineCrank

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""

# System imports
import re
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project specific imports
import modules.python.CodeScan   # noqa 408
import modules.ErrorHandling     # noqa 408
import modules.FileSupport       # noqa 408
import modules.python.Signature  # noqa 408
import modules.UMLParse          # noqa 408


class CodeGen(object):
    """ Code Generation for StateEngineCrank """
    CODE_LINE_TERMINATOR = ';'
    BLANK_LINE = ''
    TAB_SPACES = '    '

    CLASS_STATES = 'class States(Enum):'
    CLASS_EVENTS = 'class Events(Enum):'
    CLASS_TABLES = 'class StateTables(object):'

    STATE_TABLE_CLOSING_BRACE = '}'

    STATE_TRANSITION_TABLE = '    state_transition_table = {}'
    STATE_TRANSITION_TABLE_TEMPLATE = 'StateTables.state_transition_table[States.%s] = {'
    STATE_TRANSITION_TABLE_EVENT_TEMPLATE = \
        "    Events.%s: {'state2': States.%s, 'guard': %s, 'transition': %s},"

    STATE_FUNCTION_TABLE = '    state_function_table = {}'
    STATE_FUNCTION_TABLE_TEMPLATE = 'StateTables.state_function_table[States.%s] = \\'
    STATE_FUNCTION_TABLE_FUNCTIONS_TEMPLATE = "    {'enter': %s, 'do': %s, 'exit': %s}"
    STATE_FUNCTION_USERCODE_TEMPLATE = 'UserCode.%s'

    USER_CODE_CLASS = 'class UserCode(StateMachine):'
    USER_CODE_DEF_INIT = 'def __init__(self, id=None):'
    USER_CODE_INIT_CODE = [
        '    def __init__(self, id=None):',
        '        StateMachine.__init__(self, id=id, startup_state=States.StartUp,',
        '                              function_table=StateTables.state_function_table,',
        '                              transition_table=StateTables.state_transition_table)',
    ]

    GUARD_FUNC_HEADER_TEMPLATE = [
        '    # =========================================================',
        '    """ {GUARD_FUNC_TAG} ',
        '        @Todo FIXME',
        '    """'
    ]
    GUARD_FUNC_TAG = '{GUARD_FUNC_TAG}'
    GUARD_FUNC_DECL_TEMPLATE = ['    def {GUARD_FUNC_TAG}(id):']
    GUARD_FUNC_CLOSE = ['        return True']

    FUNC_HEADER_TEMPLATE = [
        '    # =========================================================',
        '    """ {FUNC_TAG} ',
        '        @Todo FIXME',
        '    """',
    ]
    FUNC_TAG = '{FUNC_TAG}'
    FUNC_DECL_TEMPLATE = ['    def {FUNC_TAG}(id):']
    FUNC_CLOSE = ['        return']

    ENUM_FORMAT = '    %s = %s'

    FUNCTION_PARENS = '(id)'
    EVT_TAG = '{EVT_TAG}'
    EVT_HANDLER_HEADER_TEMPLATE = [
        '"""',
        '===========================================================================',
        '@brief Event processing {EVT_TAG}',
        '',
        '@details State machine event processing for {EVT_TAG}.',
        '         This function needs to be called whenever the event',
        '         {EVT_TAG} is detected.',
        '===========================================================================',
        '"""']

    MissingFunctions = []   # list of functions missing in source file

    # =========================================================================
    def __init__(self):
        """ CodeGeneration module initialization. """
        logging.debug('CodeGeneration ID: %s' % id(self))
        self.code = modules.python.CodeScan.CodeScan()
        self.error = modules.ErrorHandling.Error()
        self.file = modules.FileSupport.File()
        self.sig = modules.python.Signature.Signature()
        self.uml = modules.UMLParse.UML()
        self.current_line = 0
        self.user_code_start = 0
        self.user_code_end = 0
        self.class_declaration = 0

    # =========================================================================
    def update_code(self):
        """ Update source file code. """
        self.delete_main_state_definitions()
        self.delete_main_state_tables()

        self.create_main_state_definitions()
        self.create_main_state_tables()

        self.user_code_start = self.sig.find_user_code_start()
        self.user_code_end = self.sig.find_user_code_end()

        self.create_user_class_declaration()
        self.create_user_class_init_function()

        # delete any missing functions from previous scans
        del self.MissingFunctions[:]

        self.find_user_enter_functions()
        self.find_user_do_functions()
        self.find_user_exit_functions()
        self.find_user_guard_functions()
        self.find_user_transition_functions()
        self.update_user_functions()

        self.file.dump_file()
        self.uml.dump_uml()
        self.code.dump_functions()

    # =========================================================================
    def create_main_state_definitions(self):
        """ Create main state engine definitions. """

        # find current state engine comment and bump to first line of code
        self.current_line = self.sig.find_main_state_engine_definitions_start()
        self.current_line = self.current_line + 2
        self.add_line(self.BLANK_LINE)
        self.add_line(self.BLANK_LINE)

        # output States class enumerations
        self.add_line(self.CLASS_STATES)
        logging.debug(self.CLASS_STATES)
        value = 1
        for state in self.uml.states:
            state_string = self.ENUM_FORMAT % (state, value)
            logging.debug(state_string)
            self.add_line(state_string)
            value += 1
        self.add_line(self.BLANK_LINE)
        self.add_line(self.BLANK_LINE)

        # output Events class enumerations
        self.add_line(self.CLASS_EVENTS)
        logging.debug(self.CLASS_EVENTS)
        value = 1
        for event in self.uml.events:
            event_string = self.ENUM_FORMAT % (event, value)
            logging.debug(event_string)
            self.add_line(event_string)
            value += 1
        self.add_line(self.BLANK_LINE)
        self.add_line(self.BLANK_LINE)

        # output StateTables class
        self.add_line(self.CLASS_TABLES)
        logging.debug(self.CLASS_TABLES)
        self.add_line(self.STATE_TRANSITION_TABLE)
        self.add_line(self.STATE_FUNCTION_TABLE)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_main_state_tables(self):
        """ Create main state engine tables. """

        # find current state engine comment and bump to first line of code
        self.current_line = self.sig.find_main_state_engine_tables_start()
        self.current_line = self.current_line + 2
        self.add_line(self.BLANK_LINE)
        self.create_state_transition_table()
        self.create_state_function_table()

    # =========================================================================
    def create_state_transition_table(self):
        """ Create state transition tables.
            There is a table for every state.
            Every state table contains entries for all events which will
            trigger a transition.
        """
        # create a table for every state.
        for state in self.uml.states:
            declaration = self.STATE_TRANSITION_TABLE_TEMPLATE % state
            self.add_line(declaration)
            logging.debug(declaration)

            # scan for events relevant to the current state
            for trans in self.uml.transitions:
                if trans['state1'] == state:
                    event = trans['event']
                    state2 = trans['state2']
                    if trans['guard'] is None:
                        guard = 'None'
                    else:
                        guard = self.STATE_FUNCTION_USERCODE_TEMPLATE % trans['guard']
                    if trans['trans'] is None:
                        trans_ = 'None'
                    else:
                        trans_ = self.STATE_FUNCTION_USERCODE_TEMPLATE % trans['trans']
                    line = self.STATE_TRANSITION_TABLE_EVENT_TEMPLATE % (event, state2, guard, trans_ )
                    self.add_line(line)
                    logging.debug(line)

            self.add_line(self.STATE_TABLE_CLOSING_BRACE)
            logging.debug(self.STATE_TABLE_CLOSING_BRACE)
            self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_state_function_table(self):
        """ Create state function tables.
            There is a table for every state.
            Every state table contains entries for enter, do and exit functions.
        """
        # create a table entry for every state.
        for state in self.uml.states:
            declaration = self.STATE_FUNCTION_TABLE_TEMPLATE % state
            self.add_line(declaration)
            logging.debug(declaration)

            if state in self.uml.enters:
                enter_ = self.STATE_FUNCTION_USERCODE_TEMPLATE % self.uml.enters[state]
            else:
                enter_ = 'None'
            if state in self.uml.dos:
                do_ = self.STATE_FUNCTION_USERCODE_TEMPLATE % self.uml.dos[state]
            else:
                do_ = 'None'
            if state in self.uml.exits:
                exit_ = self.STATE_FUNCTION_USERCODE_TEMPLATE % self.uml.exits[state]
            else:
                exit_ = 'None'

            line_ = self.STATE_FUNCTION_TABLE_FUNCTIONS_TEMPLATE % (enter_, do_, exit_)
            self.add_line(line_)
            logging.debug(line_)
            self.add_line(self.BLANK_LINE)

    # =========================================================================
    def delete_lines(self, start_signature, end_signature):
        """ Delete lines from file in memory based on location of signature. """
        # find start and end and delete
        result_start, line_start = self.sig.find_signature(start_signature)
        result_end, line_end = self.sig.find_signature(end_signature)

        # sanity check the start and end
        if (not result_start) and (not result_end):
            self.error.invalid_start_end(line_start, line_end)

        # adjust the start and end line numbers
        line_start = line_start + 2   # start past the START signature
        line_end = line_end - 2       # stop before the END signature

        # delete a range of lines
        # print "Delete lines ", line_start, " thru ", line_end
        for line in range(line_start, line_end+1):
            line_offset = line_end - line
            self.file.delete_line(line_start+line_offset)

    # =========================================================================
    def delete_main_state_definitions(self):
        """ Delete main state engine definitions. """
        self.delete_lines(self.sig.MAIN_DEFINES_START, self.sig.MAIN_DEFINES_END)

    # =========================================================================
    def delete_main_state_tables(self):
        """ Delete main state engine tables. """
        self.delete_lines(self.sig.MAIN_TABLES_START, self.sig.MAIN_TABLES_END)

    # =========================================================================
    def create_user_class_declaration(self):
        # scan user code for class declaration
        for line in range(self.user_code_start, self.user_code_end):
            line_text = self.file.get_line(line)
            if line_text[1].startswith(self.USER_CODE_CLASS):
                self.class_declaration = line_text[0]
                return

        # if not found, create it
        self.current_line = self.user_code_start + 2
        self.add_line(self.USER_CODE_CLASS)
        self.add_line(self.BLANK_LINE)

        # remember location of class declaration
        self.class_declaration = self.current_line

    # =========================================================================
    def create_user_class_init_function(self):
        # scan user code for __init__() function declaration
        for line in range(self.user_code_start, self.user_code_end):
            line_text = self.file.get_line(line)
            if self.USER_CODE_DEF_INIT in line_text:
                return

        # if not found, create it
        self.current_line = self.class_declaration + 1
        self.add_line(self.BLANK_LINE)
        self.add_lines(self.USER_CODE_INIT_CODE)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_event_functions(self):
        """ Create event function handlers. """
        for event in sorted(self.uml.events):
            # self.add_event_handler(event)
            self.error.unimplemented('create_event_functions()', self.error.lineno())

    # =============================================================================================
    def update_user_state_code(self):
        """ Create/Update user functions. """
        logging.debug('Missing User Functions: %s' % self.MissingFunctions)
        # early exit if no missing functions
        if len(self.MissingFunctions) == 0:
            return
        # find current user code end comment and backup to insert missing
        # user functions
        self.current_line = self.sig.find_user_code_end()
        self.current_line = self.current_line - 2
        for func in sorted(self.MissingFunctions):
            self.add_line(self.BLANK_LINE)
            if self.uml.is_guard(func):
                self.error.unimplemented('if: is_guard()', self.error.lineno())
                # self.add_lines_template(self.GUARD_FUNC_HEADER_TEMPLATE, self.GUARD_FUNC_TAG, func)
                # self.add_lines_template(self.GUARD_FUNC_DECL_TEMPLATE, self.GUARD_FUNC_TAG, func)
                # self.add_lines_template(self.GUARD_FUNC_CLOSE, self.GUARD_FUNC_TAG, func)
            else:
                self.error.unimplemented('else: is_guard()', self.error.lineno())
                # self.add_lines_template(self.VOID_FUNC_HEADER_TEMPLATE, self.VOID_FUNC_TAG, func)
                # self.add_lines_template(self.VOID_FUNC_DECL_TEMPLATE, self.VOID_FUNC_TAG, func)
                # self.add_lines_template(self.VOID_FUNC_CLOSE, self.VOID_FUNC_TAG, func)

    # =============================================================================================
    def update_user_functions(self):
        """ Create/Update user functions. """
        logging.debug('Missing User Functions: %s' % self.MissingFunctions)
        # early exit if no missing functions
        if len(self.MissingFunctions) == 0:
            return
        # find current user code end comment and backup to insert missing
        # user functions
        self.current_line = self.sig.find_user_code_end()
        self.current_line = self.current_line - 2
        for func in sorted(self.MissingFunctions):
            self.add_line(self.BLANK_LINE)
            if self.uml.is_guard(func):
                self.add_lines_template(self.GUARD_FUNC_HEADER_TEMPLATE, self.GUARD_FUNC_TAG, func)
                self.add_lines_template(self.GUARD_FUNC_DECL_TEMPLATE, self.GUARD_FUNC_TAG, func)
                self.add_lines_template(self.GUARD_FUNC_CLOSE, self.GUARD_FUNC_TAG, func)
            else:
                self.add_lines_template(self.FUNC_HEADER_TEMPLATE, self.FUNC_TAG, func)
                self.add_lines_template(self.FUNC_DECL_TEMPLATE, self.FUNC_TAG, func)
                self.add_lines_template(self.FUNC_CLOSE, self.FUNC_TAG, func)

    # =============================================================================================
    def find_user_functions(self, func_list):
        """ Scan current list functions for UML functions. """
        logging.debug('FuncList: %s' % func_list)
        # scan code for missing functions
        for func in func_list:
            # check for functions
            found = self.code.find_function(func)
            if not found:
                self.MissingFunctions.append(func)
                logging.debug('Missing function: %s' % func)
            else:
                logging.debug('Found function: %s ' % func)

    # =============================================================================================
    def find_user_event_functions(self):
        """ Scan current list of functions for UML event functions. """
        self.find_user_functions(self.uml.events.values())

    # =============================================================================================
    def find_user_enter_functions(self):
        """ Scan current list of functions for UML enter functions. """
        self.find_user_functions(self.uml.enters.values())

    # =========================================================================
    def find_user_do_functions(self):
        """ Scan current list of functions for UML enter functions. """
        self.find_user_functions(self.uml.dos.values())

    # =========================================================================
    def find_user_exit_functions(self):
        """ Scan current list of functions for UML exit functions. """
        self.find_user_functions(self.uml.exits.values())

    # =========================================================================
    def find_user_guard_functions(self):
        """ Scan current list of functions for UML guard functions. """
        self.find_user_functions(self.uml.gfuncs)

    # =========================================================================
    def find_user_transition_functions(self):
        """ Scan current list of functions for UML transition functions. """
        self.find_user_functions(self.uml.tfuncs)

    # =========================================================================
    def add_lines_template(self, lines_text, token, arg):
        """ Add lines of text to file in memory using template. """
        for line_text in lines_text:
            self.add_line_template(line_text, token, arg)

    # =========================================================================
    def add_lines(self, lines_text):
        """ Add lines of text to file in memory. """
        for line_text in lines_text:
            self.add_line(line_text)

    # =========================================================================
    def add_line_template(self, line_text, token, arg):
        """ Add line of text to file in memory using template. """
        # make text substitutions for caller
        text = line_text.replace(token, arg)
        # currentLine needs to be 0-relative
        self.file.insert_line_text(self.current_line-1, text)
        self.current_line = self.current_line + 1

    # =========================================================================
    def add_line(self, line_text):
        """ Add line of text to file in memory. """
        # currentLine needs to be 0-relative
        self.file.insert_line_text(self.current_line-1, line_text)
        self.current_line = self.current_line + 1
