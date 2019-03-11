""" Code Scanning (Ansi-C State Engine)

The purpose of this module is to scan code source files and
generate a list of function prototypes and function instantiations.
"""
# System imports
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

import re                       # noqa 408

import modules.ErrorHandling    # noqa 408
import modules.FileSupport      # noqa 408
import modules.ansi_c.Signature  # noqa 408
import modules.Singleton        # noqa 408


class CodeScan(modules.Singleton.Singleton):
    """ Code Scanning for StateEngineCrank
        The purpose of this module is to scan code source files and
        generate a list of function prototypes and function instantiations.
    """

    # Regular Expression - function prototype
    # static void funcName (int id);
    # static BOOL guardName (int id);
    re_func_proto = re.compile(r'static void (?P<funcName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(int id\);')
    re_guard_proto = re.compile(r'static BOOL_TYPE (?P<guardName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(int id\);')
    prototypes = []     # array of function prototypes found

    # Regular Expression - function declaration
    # static void funcName (int id)
    # static BOOL guardName (int id)
    re_func_declaration = re.compile(r'static void (?P<funcName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(int id\)')
    re_guard_declaration = re.compile(r'static BOOL_TYPE (?P<guardName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(int id\)')
    functions = []      # array of functions found

    # =========================================================================
    def __init__(self):
        self.error = modules.ErrorHandling.Error()
        self.file = modules.FileSupport.File()
        self.sig = modules.ansi_c.Signature.Signature()
        logging.debug('CodeScan ID: %s' % id(self))

    # =========================================================================
    def scan_code(self):
        """ Scan code for prototypes and functions. """
        self.scan_user_prototypes()
        self.prototypes.sort()

        self.scan_user_functions()
        self.functions.sort()

        self.dump_prototypes()
        self.dump_functions()

    # =========================================================================
    def find_prototype(self, proto_name):
        """ Scan our list of prototypes (True if found). """
        for proto in self.prototypes:
            if proto_name == proto:
                return True
        return False

    # =========================================================================
    def find_function(self, func_name):
        """ Scan our list of functions (True if found). """
        for func in self.functions:
            if func_name == func:
                return True
        return False

    # =========================================================================
    def dump_prototypes(self):
        """ Dump prototypes we Found. """
        logging.debug('Prototypes:')
        for proto in self.prototypes:
            logging.debug('    %s' % proto)

    # =========================================================================
    def dump_functions(self):
        """ Dump functions we Found. """
        logging.debug('Functions:')
        for func in self.functions:
            logging.debug('    %s' % func)

    # =========================================================================
    def scan_user_prototypes(self):
        """ Find start and end line of User Code Prototypes. """
        start_line = self.sig.find_user_code_proto_start()
        end_line = self.sig.find_user_code_proto_end()

        logging.debug('Start/End: %s/%s' % (start_line, end_line))

        # start with empty prototype list
        del self.prototypes[:]
        logging.info('Prototypes: %s' % self.prototypes)

        # scan all lines in the file
        for line in range(start_line, end_line):
            line_text = self.file.get_line_text(line)

            # check for a function prototype
            match = self.re_func_proto.match(line_text)
            if match is not None:
                logging.debug('SUCCESS: %s' % line_text)
                self.prototypes.append(match.group('funcName'))
                continue

            # check for a guard prototype
            match = self.re_guard_proto.match(line_text)
            if match is not None:
                logging.debug('SUCCESS: %s' % line_text)
                self.prototypes.append(match.group('guardName'))
                continue

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
