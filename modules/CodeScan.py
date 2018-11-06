"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      17-June-2016

@package:   StateEngineCrank
@brief:     Code Scanning
@details:   Code Scanning for StateEngineCrank
            The purpose of this module is to scan code source files and
            generate a list of function prototypes and function instantiations.

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
print('Loading modules: ', __file__, 'as', __name__)

import re                       # noqa 408

import modules.ErrorHandling    # noqa 408
import modules.FileSupport      # noqa 408
import modules.Signature        # noqa 408
import modules.Singleton        # noqa 408


class CodeScan(modules.Singleton.Singleton):
    """ Code Scanning for StateEngineCrank
        The purpose of this module is to scan code source files and
        generate a list of function prototypes and function instantiations.
    """

    # Regular Expression - function prototype
    # static void funcName (void);
    # static BOOL guardName (void);
    re_func_proto = re.compile(r'static void (?P<funcName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(void\);')
    re_guard_proto = re.compile(r'static BOOL_TYPE (?P<guardName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(void\);')
    prototypes = []     # array of function prototypes found

    # Regular Expression - function declaration
    # static void funcName (void)
    # static BOOL guardName (void)
    re_func_declaration = re.compile(r'static void (?P<funcName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(void\)')
    re_guard_declaration = re.compile(r'static BOOL_TYPE (?P<guardName>[a-zA-Z_]+[a-zA-Z0-9_]*)\(void\)')
    functions = []      # array of functions found

    # =========================================================================
    def __init__(self):
        self.error = modules.ErrorHandling.Error()
        self.file = modules.FileSupport.File()
        self.sig = modules.Signature.Signature()
        self.debug.dprint(("CodeScan ID:", id(self)))

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
        self.debug.dprint(('Prototypes:', ''))
        for proto in self.prototypes:
            self.debug.dprint(("    ", proto))

    # =========================================================================
    def dump_functions(self):
        """ Dump functions we Found. """
        self.debug.dprint(('Functions:', ''))
        for func in self.functions:
            self.debug.dprint(("    ", func))

    # =========================================================================
    def scan_user_prototypes(self):
        """ Find start and end line of User Code Prototypes. """
        start_line = self.sig.find_user_code_proto_start()
        end_line = self.sig.find_user_code_proto_end()

        self.debug.dprint(("Start/End:", start_line, end_line))

        # start with empty prototype list
        del self.prototypes[:]
        print('Prototypes: ', self.prototypes)

        # scan all lines in the file
        for line in range(start_line, end_line):
            line_text = self.file.get_line_text(line)

            # check for a function prototype
            match = self.re_func_proto.match(line_text)
            if match is not None:
                self.debug.dprint(('SUCCESS:', line_text))
                self.prototypes.append(match.group('funcName'))
                continue

            # check for a guard prototype
            match = self.re_guard_proto.match(line_text)
            if match is not None:
                self.debug.dprint(('SUCCESS:', line_text))
                self.prototypes.append(match.group('guardName'))
                continue

    # =========================================================================
    def scan_user_functions(self):
        """ Find start and end line of User Code Prototypes. """
        start_line = self.sig.find_user_code_start()
        end_line = self.sig.find_user_code_end()

        self.debug.dprint(("Start/End:", start_line, end_line))

        # start with empty function list
        del self.functions[:]
        print('Functions: ', self.functions)
        print('Scanning from %s to %s ==> %s lines' % (start_line, end_line, end_line-start_line))

        # scan all lines in the file
        for line in range(start_line, end_line):
            line_text = self.file.get_line_text(line)

            # check for a function declaration
            match = self.re_func_declaration.match(line_text)
            if match is not None:
                self.debug.dprint(('SUCCESS:', line_text))
                self.functions.append(match.group('funcName'))
                continue

            # check for a guard declaration
            match = self.re_guard_declaration.match(line_text)
            if match is not None:
                self.debug.dprint(('SUCCESS:', line_text))
                self.functions.append(match.group('guardName'))
                continue
