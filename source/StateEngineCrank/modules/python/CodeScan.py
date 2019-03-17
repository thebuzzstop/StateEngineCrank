""" StateEngineCrank.python.CodeScan

Python State Engine

The purpose of this module is to scan code source files and
generate a list of function prototypes and function instantiations.
"""
# System imports
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

import re                       # noqa 408

import modules.ErrorHandling  # noqa 408
import modules.FileSupport  # noqa 408
import modules.python.Signature  # noqa 408
import modules.Singleton  # noqa 408


class CodeScan(modules.Singleton.Singleton):
    """ Code Scanning for StateEngineCrank
        The purpose of this module is to scan code source files and
        generate a list of functions defined
    """

    # Regular Expression - function declaration
    #   def func_funcName(id)
    #   def guard_guardName(id)
    re_func_declaration = re.compile(r'def (?P<funcName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(self\)')
    re_guard_declaration = re.compile(r'def (?P<guardName>guard_[a-zA-Z_]+[a-zA-Z0-9_]*)\(self\)')
    functions = []      # array of functions found

    # =========================================================================
    def __init__(self):
        self.error = modules.ErrorHandling.Error()
        self.file = modules.FileSupport.File()
        self.sig = modules.python.Signature.Signature()
        logging.debug('CodeScan ID: %s' % id(self))

    # =========================================================================
    def scan_code(self):
        """ Scan code for functions. """
        self.scan_user_functions()
        self.functions.sort()
        self.dump_functions()

    # =========================================================================
    def find_function(self, func_name):
        """ Scan our list of functions (True if found). """
        for func in self.functions:
            if func_name == func:
                return True
        return False

    # =========================================================================
    def dump_functions(self):
        """ Dump functions we Found. """
        logging.debug('Functions:')
        for func in self.functions:
            logging.debug('    %s' % func)

    # =========================================================================
    def scan_user_functions(self):
        """ Find start and end line of User Code Prototypes. """
        start_line = self.sig.find_user_code_start()
        end_line = self.sig.find_user_code_end()

        logging.debug('Start/End: %s / %s' % (start_line, end_line))

        # start with empty function list
        del self.functions[:]
        logging.info('Functions: %s' % self.functions)
        logging.info('Scanning from %s to %s ==> %s lines' % (start_line, end_line, end_line-start_line))

        # scan all lines in the file
        for line in range(start_line, end_line):
            line_text = self.file.get_line_text(line)

            # check for a function declaration
            match = self.re_func_declaration.match(line_text)
            if match is not None:
                logging.debug('SUCCESS: %s' % line_text)
                self.functions.append(match.group('funcName'))
                continue

            # check for a guard declaration
            match = self.re_guard_declaration.match(line_text)
            if match is not None:
                logging.debug('SUCCESS:', line_text)
                self.functions.append(match.group('guardName'))
                continue
