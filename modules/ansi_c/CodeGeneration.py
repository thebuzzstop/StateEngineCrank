"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     Code Generation (Ansi-C State Engine)
@details:   Code Generation for StateEngineCrank

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""

# System imports
import re
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project specific imports
import modules.ansi_c.CodeScan  # noqa 408
import modules.ErrorHandling    # noqa 408
import modules.FileSupport      # noqa 408
import modules.ansi_c.Signature  # noqa 408
import modules.UMLParse         # noqa 408


class CodeGen(object):
    """ Code Generation for StateEngineCrank """

    CODE_LINE_TERMINATOR = ';'
    BLANK_LINE = ''
    TAB_SPACES = '    '

    FUNCTION_CLOSE = '}'
    FUNCTION_PARENS = '(id)'

    SWITCH_START = [
        '    switch (GET_CURRENT_STATE(id)) // dispatch according to current state',
        '    {']

    SWITCH_DELIMIT = ':'
    SWITCH_CASE = '        case '
    SWITCH_CASE_GUARD_IF = '            if ('
    SWITCH_CASE_GUARD_IF2 = ') {'
    SWITCH_CASE_GUARD_CLOSE = '            }'
    SWITCH_CASE_GUARD_ELSE = '            } else'
    SWITCH_CASE_GUARD_ELSE2 = '            } else {'

    SWITCH_CASE_INDENT = '            '
    SWITCH_CASE_INDENT2 = '                '
    SWITCH_BREAK = '            break;'
    SWITCH_CLOSE = '    }'

    STATES_TYPEDEF_START = [
        'typedef enum STATES {',
        '    InitialState = -1, //!< initial state is automatic']

    STATES_TYPEDEF_END = [
        '    FinalState = -2 //!< final state is automatic',
        '} State;']

    MAIN_PROTOTYPES = [
        'static void StateEngineCrank_MainDoLoop(int id);']

    MAIN_LOOP_HEADER = [
        '/**',
        ' * ===========================================================================',
        ' * @brief StateEngineCrank - Main Loop',
        ' *',
        ' * @details This is the main state machine processing loop.',
        ' * ===========================================================================',
        ' */']

    MAIN_LOOP_DECLARATION = [
        'static void StateEngineCrank_MainDoLoop(int id)',
        '{',
        '    STATE_ENGINE_INITIALIZE_HOOK(id);',
        'loop:']

    MAIN_LOOP_CLOSE = [
        'goto loop;',
        '    STATE_ENGINE_TERMINATE_HOOK(id);',
        '}']

    MAIN_LOOP_SWITCH_USER_DO = '            '
    MAIN_LOOP_SWITCH_INITIAL = [
        '        case InitialState:',
        '            MAIN_LOOP_INITIAL_STATE_HOOK(id);',
        '            break;']

    MAIN_LOOP_SWITCH_FINAL = [
        '        case FinalState:',
        '            MAIN_LOOP_FINAL_STATE_HOOK(id);',
        '            break;']

    MAIN_LOOP_SWITCH_DEFAULT = [
        '        default:',
        '            MAIN_LOOP_DEFAULT_HOOK(id);',
        '            break;']

    MAIN_LOOP_INITIAL_STATE_HOOK = 'MAIN_LOOP_INITIAL_STATE_HOOK(id)'
    MAIN_LOOP_FINAL_STATE_HOOK = 'MAIN_LOOP_FINAL_STATE_HOOK(id)'
    MAIN_LOOP_DEFAULT_HOOK = 'MAIN_LOOP_DEFAULT_HOOK(id)'

    NUM_THREADS_HOOK = 'NUM_THREADS'

    GET_CURRENT_STATE = 'GET_CURRENT_STATE(id)'
    SET_CURRENT_STATE = 'SET_CURRENT_STATE(id, state)'

    STATE_ENGINE_RUNNING = 'STATE_ENGINE_RUNNING(id)'

    STATE_ENGINE_INITIALIZE_HOOK = 'STATE_ENGINE_INITIALIZE_HOOK(id)'
    STATE_ENGINE_TERMINATE_HOOK = 'STATE_ENGINE_TERMINATE_HOOK(id)'
    EVT_HANDLER_DEFAULT_HOOK = 'EVT_HANDLER_DEFAULT_HOOK(id)'

    HOOK_IFNDEF = '#ifndef '
    HOOK_DEFINE = '#define '
    HOOK_ENDIF = '#endif'

    EVT_TAG = '{EVT_TAG}'
    EVT_PROTO = 'static void {EVT_TAG}(int id);'

    EVT_HANDLER_HEADER_TEMPLATE = [
        '/**',
        ' * ===========================================================================',
        ' * @brief Event processing {EVT_TAG}',
        ' *',
        ' * @details State machine event processing for {EVT_TAG}.',
        ' *          This function needs to be called whenever the event',
        ' *          {EVT_TAG} is detected.',
        ' * ===========================================================================',
        ' */']

    EVT_DECLARATION_TEMPLATE = [
        'static void {EVT_TAG}(int id)',
        '{']

    EVT_HANDLER_SWITCHDEF_TEMPLATE = [
        '        default:',
        '            EVT_HANDLER_DEFAULT_HOOK(id);',
        '            break;']

    STATE_TAG = '{STATE_TAG}'
    EVT_HANDLER_CURSTATE_TEMPLATE = 'SET_CURRENT_STATE(id, {STATE_TAG});'

    MissingPrototypes = []  # list of prototypes missing in source file
    MissingFunctions = []   # list of functions missing in source file

    VOID_FUNC_TAG = '{VOID_FUNC_TAG}'
    VOID_FUNC_PROTO_TEMPLATE = 'static void {VOID_FUNC_TAG}(int id);'
    VOID_FUNC_HEADER_TEMPLATE = ['/**', ' * @todo FIXME', ' */']
    VOID_FUNC_DECL_TEMPLATE = ['static void {VOID_FUNC_TAG}(int id)', '{']
    VOID_FUNC_CLOSE = ['    return;', '}']

    GUARD_FUNC_TAG = '{GUARD_FUNC_TAG}'
    GUARD_FUNC_PROTO_TEMPLATE = 'static BOOL_TYPE {GUARD_FUNC_TAG}(int id);'
    GUARD_FUNC_HEADER_TEMPLATE = ['/**', ' * @todo FIXME', ' */']
    GUARD_FUNC_DECL_TEMPLATE = ['static BOOL_TYPE {GUARD_FUNC_TAG}(int id)', '{']
    GUARD_FUNC_CLOSE = ['    return TRUE;', '}']

    re_hook = re.compile(r'(?P<hook>[a-zA-Z_]+[a-zA-Z0-9_]*)')

    # =========================================================================
    def __init__(self):
        """ CodeGeneration module initialization. """
        logging.debug('CodeGeneration ID: %s' % id(self))
        self.code = modules.ansi_c.CodeScan.CodeScan()
        self.error = modules.ErrorHandling.Error()
        self.file = modules.FileSupport.File()
        self.sig = modules.ansi_c.Signature.Signature()
        self.uml = modules.UMLParse.UML()
        self.current_line = 0

    # =========================================================================
    def update_code(self):
        """ Update source file code. """
        self.delete_state_engine_enums()
        self.delete_state_engine_prototypes()
        self.delete_state_engine_variables()
        self.delete_state_engine_defines()
        self.delete_state_engine_code()

        self.create_main_enums()
        self.create_main_prototypes()
        self.create_main_variables()
        self.create_main_defines()
        self.create_main_loop()

        self.create_event_functions()

        # delete any missing functions/prototypes from previous scans
        del self.MissingFunctions[:]
        del self.MissingPrototypes[:]

        self.find_user_enter_functions()
        self.find_user_do_functions()
        self.find_user_exit_functions()
        self.find_user_guard_functions()
        self.find_user_transition_functions()

        self.update_user_prototypes()
        self.update_user_functions()

        self.file.dump_file()
        self.uml.dump_uml()
        self.code.dump_prototypes()
        self.code.dump_functions()

    # =========================================================================
    def create_main_prototypes(self):
        """ Create main state engine prototypes. """

        # find current state engine comment and bump to first line of code
        self.current_line = self.sig.find_state_engine_code_proto_start()
        self.current_line = self.current_line + 2

        self.add_line(self.BLANK_LINE)
        self.add_lines(self.MAIN_PROTOTYPES)
        self.add_line(self.BLANK_LINE)

        # add event handler prototypes
        for event in sorted(self.uml.events):
            self.add_line_template(self.EVT_PROTO, self.EVT_TAG, event)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_main_defines(self):
        """ Create main state engine defines. """

        # find current state engine comment and bump to first line of code
        self.current_line = self.sig.find_state_engine_code_defines_start()
        self.current_line = self.current_line + 2
        self.add_line(self.BLANK_LINE)

        # add conditionals here (#ifdef's)
        self.add_conditional_hook(self.NUM_THREADS_HOOK, '1')
        self.add_conditional_hook(self.GET_CURRENT_STATE, '')
        self.add_conditional_hook(self.SET_CURRENT_STATE, '')

        self.add_conditional_hook(self.STATE_ENGINE_RUNNING, '')

        self.add_conditional_hook(self.STATE_ENGINE_INITIALIZE_HOOK, '')
        self.add_conditional_hook(self.STATE_ENGINE_TERMINATE_HOOK, '')
        self.add_conditional_hook(self.EVT_HANDLER_DEFAULT_HOOK, '')

        self.add_conditional_hook(self.MAIN_LOOP_INITIAL_STATE_HOOK, '')
        self.add_conditional_hook(self.MAIN_LOOP_FINAL_STATE_HOOK, '')
        self.add_conditional_hook(self.MAIN_LOOP_DEFAULT_HOOK, '')

    # =========================================================================
    def create_main_enums(self):
        """ Create main state engine enumerations. """

        # find current state engine comment and bump to first line of code
        self.current_line = self.sig.find_state_engine_code_enums_start()
        self.current_line = self.current_line + 2
        self.add_line(self.BLANK_LINE)

        # add typedef's for states enumeration
        self.add_lines(self.STATES_TYPEDEF_START)
        for line in self.uml.states:
            self.add_line('    ' + line + ',')
        self.add_lines(self.STATES_TYPEDEF_END)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_main_variables(self):
        """ Create main state engine variables. """

        # find current state variable comment and bump to first line of code
        self.current_line = self.sig.find_state_engine_code_variables_start()
        self.current_line = self.current_line + 2
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_main_loop(self):
        """ Create main state engine monitoring loop. """

        # find current state engine comment and bump to first line of code
        self.current_line = self.sig.find_state_engine_code_start()
        self.current_line = self.current_line + 2
        self.add_line(self.BLANK_LINE)

        # main loop function
        self.add_lines(self.MAIN_LOOP_HEADER)
        self.add_lines(self.MAIN_LOOP_DECLARATION)
        self.add_lines(self.SWITCH_START)

        # add a switch-case for each state
        for state in self.uml.states:
            self.add_switch_state(state)

        # close out the main switch
        self.add_lines(self.MAIN_LOOP_SWITCH_INITIAL)
        self.add_lines(self.MAIN_LOOP_SWITCH_FINAL)
        self.add_lines(self.MAIN_LOOP_SWITCH_DEFAULT)
        self.add_line(self.SWITCH_CLOSE)
        self.add_lines(self.MAIN_LOOP_CLOSE)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def create_event_functions(self):
        """ Create event function handlers. """
        for event in sorted(self.uml.events):
            self.add_event_handler(event)

    # =========================================================================
    def update_user_prototypes(self):
        """ Create/Update user prototypes. """
        logging.debug('Missing User Prototypes: %s' % self.MissingPrototypes)
        # early exit if no missing prototypes
        if len(self.MissingPrototypes) == 0:
            return
        # find current user prototype end comment and backup to insert missing
        # user prototypes
        self.current_line = self.sig.find_user_code_proto_end()
        self.current_line = self.current_line - 2
        self.add_line(self.BLANK_LINE)
        for proto in sorted(self.MissingPrototypes):
            if self.uml.is_guard(proto):
                self.add_line_template(self.GUARD_FUNC_PROTO_TEMPLATE, self.GUARD_FUNC_TAG, proto)
            else:
                self.add_line_template(self.VOID_FUNC_PROTO_TEMPLATE, self.VOID_FUNC_TAG, proto)

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
                self.add_lines_template(self.VOID_FUNC_HEADER_TEMPLATE, self.VOID_FUNC_TAG, func)
                self.add_lines_template(self.VOID_FUNC_DECL_TEMPLATE, self.VOID_FUNC_TAG, func)
                self.add_lines_template(self.VOID_FUNC_CLOSE, self.VOID_FUNC_TAG, func)

    # =============================================================================================
    def find_user_functions(self, func_list):
        """ Scan current list of prototypes and functions for UML functions. """
        logging.debug('FuncList: %s' % func_list)
        # scan code for missing functions/prototypes
        for func in func_list:
            # check for prototypes
            found = self.code.find_prototype(func)
            if not found:
                self.MissingPrototypes.append(func)
                logging.debug('Missing prototype: %s ' % func)
            else:
                logging.debug('Found prototype: %s ' % func)

            # check for functions
            found = self.code.find_function(func)
            if not found:
                self.MissingFunctions.append(func)
                logging.debug('Missing function: %s' % func)
            else:
                logging.debug('Found function: %s ' % func)

    # =============================================================================================
    def find_user_enter_functions(self):
        """ Scan current list of prototypes and functions for UML enter
            functions. """
        self.find_user_functions(self.uml.enters.values())

    # =========================================================================
    def find_user_do_functions(self):
        """ Scan current list of prototypes and functions for UML enter
            functions. """
        self.find_user_functions(self.uml.dos.values())

    # =========================================================================
    def find_user_exit_functions(self):
        """ Scan current list of prototypes and functions for UML exit
            functions. """
        self.find_user_functions(self.uml.exits.values())

    # =========================================================================
    def find_user_guard_functions(self):
        """ Scan current list of prototypes and functions for UML guard
            functions. """
        self.find_user_functions(self.uml.gfuncs)

    # =========================================================================
    def find_user_transition_functions(self):
        """ Scan current list of prototypes and functions for UML transition
            functions. """
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
    def delete_state_engine_code(self):
        """ Delete all state engine code. """
        self.delete_lines(self.sig.MAIN_CODE_START, self.sig.MAIN_CODE_END)

    # =========================================================================
    def delete_state_engine_defines(self):
        """ Delete all state engine defines. """
        self.delete_lines(self.sig.MAIN_CODE_DEFINES_START, self.sig.MAIN_CODE_DEFINES_END)

    # =========================================================================
    def delete_state_engine_enums(self):
        """ Delete all state engine enumerations. """
        self.delete_lines(self.sig.MAIN_CODE_ENUMS_START, self.sig.MAIN_CODE_ENUMS_END)

    # =========================================================================
    def delete_state_engine_prototypes(self):
        """ Delete all state engine prototypes. """
        self.delete_lines(self.sig.MAIN_CODE_PROTOTYPES_START, self.sig.MAIN_CODE_PROTOTYPES_END)

    # =========================================================================
    def delete_state_engine_variables(self):
        """ Delete all state engine variables. """
        self.delete_lines(self.sig.MAIN_CODE_VARIABLES_START, self.sig.MAIN_CODE_VARIABLES_END)

    # =========================================================================
    def add_switch_state(self, state):
        """ Add a switch case (state) to source file in memory. """
        self.add_line(self.SWITCH_CASE + state + self.SWITCH_DELIMIT)
        if state in self.uml.dos:
            self.add_line(self.MAIN_LOOP_SWITCH_USER_DO + self.uml.dos[state] +
                          self.FUNCTION_PARENS + self.CODE_LINE_TERMINATOR)
        self.add_line(self.SWITCH_BREAK)

    # =========================================================================
    def add_conditional_hook(self, hook, value):
        """ Add #ifndef conditional hook to source file in memory. """
        match = self.re_hook.match(hook)
        if match is not None:
            hook_ifdef = match.group('hook')
        else:
            hook_ifdef = hook
        self.add_line(self.HOOK_IFNDEF + hook_ifdef)
        self.add_line(self.HOOK_DEFINE + hook + ' ' + value)
        self.add_line(self.HOOK_ENDIF)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def add_conditional_hook_param(self, hook, param, value):
        """ Add #ifndef conditional hook to source file in memory. """
        match = self.re_hook.match(hook)
        if match is not None:
            hook_ifdef = match.group('hook')
        else:
            hook_ifdef = hook
        self.add_line(self.HOOK_IFNDEF + hook_ifdef)
        self.add_line(self.HOOK_DEFINE + hook + param + ' ' + value)
        self.add_line(self.HOOK_ENDIF)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def add_event_handler(self, event):
        """ Add event handler function to source file in memory. """
        # create event handler function header
        self.add_lines_template(self.EVT_HANDLER_HEADER_TEMPLATE, self.EVT_TAG, event)

        # create event handler function declaration
        self.add_lines_template(self.EVT_DECLARATION_TEMPLATE, self.EVT_TAG, event)

        # create event handler function switch
        self.add_lines(self.SWITCH_START)

        # create switch cases
        self.add_event_switch_cases(event)

        # create switch default
        self.add_lines(self.EVT_HANDLER_SWITCHDEF_TEMPLATE)

        # close out the switch and event function handler
        self.add_line(self.SWITCH_CLOSE)
        self.add_line(self.FUNCTION_CLOSE)
        self.add_line(self.BLANK_LINE)

    # =========================================================================
    def add_event_switch_cases(self, event):
        """ Add event switch cases to current event function being created. """
        self.uml.dump_uml()
        for state1 in self.uml.states:

            # start the switch case
            self.add_line(self.SWITCH_CASE + state1 + self.SWITCH_DELIMIT)

            # set True if we are actively processing guards
            guard_active = False

            # switch_case_code_indent used when indenting switch case code
            # this is adjusted if processing guards
            switch_case_code_indent = self.SWITCH_CASE_INDENT

            # scan transitions for this event in this state
            # scan for transitions that have a [guard] first
            for has_guard in [True, False]:
                for transition in self.uml.transitions:
                    if transition['event'] == event and transition['state1'] == state1:

                        # establish components of this transition
                        state2 = transition['state2']
                        guard = transition['guard']

                        # test if we are processing [guards]
                        if has_guard and guard is None:
                            continue
                        if not has_guard and guard is not None:
                            continue

                        # check for a guard function
                        if guard is not None:
                            # if we are already processing a guard then add the closing bracket
                            if guard_active:
                                self.add_line(self.SWITCH_CASE_GUARD_ELSE)
                            # add the if (guard()) {
                            self.add_line(self.SWITCH_CASE_GUARD_IF + guard +
                                          self.FUNCTION_PARENS + self.SWITCH_CASE_GUARD_IF2)
                            # increase the indent and flag that a guard is active
                            switch_case_code_indent = self.SWITCH_CASE_INDENT2
                            guard_active = True     # flag that guard logic is active
                        else:
                            # if we have already processed a guard then add the closing bracket
                            if guard_active:
                                self.add_line(self.SWITCH_CASE_GUARD_ELSE2)

                        # add exit function if it exists
                        # if self.uml.exits.has_key(state1):
                        if state1 in self.uml.exits:
                            self.add_line(switch_case_code_indent + self.uml.exits[state1] +
                                          self.FUNCTION_PARENS + self.CODE_LINE_TERMINATOR)

                        # add transition function if it exists
                        if transition['trans'] is not None:
                            self.add_line(switch_case_code_indent + transition['trans'] +
                                          self.FUNCTION_PARENS + self.CODE_LINE_TERMINATOR)

                        # set state variable to new state
                        self.add_line_template(switch_case_code_indent +
                                               self.EVT_HANDLER_CURSTATE_TEMPLATE,
                                               self.STATE_TAG, state2)

                        # add entry function if it exists
                        # if self.uml.enters.has_key(state2):
                        if state2 in self.uml.enters:
                            self.add_line(switch_case_code_indent + self.uml.enters[state2] +
                                          self.FUNCTION_PARENS + self.CODE_LINE_TERMINATOR)

            # close out guard if active
            if guard_active:
                self.add_line(self.SWITCH_CASE_GUARD_CLOSE)

            self.add_line(self.SWITCH_BREAK)
