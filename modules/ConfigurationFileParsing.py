"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     Configuration File Parsing
@details:   Configuration File Parsing for StateEngineCrank

@copyright: Mark B Sawyer, All Rights Reserved 2016

"""
print('Loading modules: ', __file__, 'as', __name__)

import re                       # noqa 408

import modules.DebugSupport     # noqa 408
import modules.ErrorHandling    # noqa 408
import modules.Singleton        # noqa 408


class ConfigFile(modules.Singleton.Singleton):
    """ Configuration File Parsing for StateEngineCrank. """

    COMMENT_DELIMITER = '#'
    CONFIG_DELIMITER = '='

    RE_CONFIG_VAR = r'(?P<config_var>([a-zA-Z_]+[a-zA-Z0-9_]*))'
    RE_CONFIG_VAL = r'(?P<config_val>([a-zA-Z_]+[a-zA-Z0-9_\.]*))'
    RE_CONFIG_FILE = r'(?P<config_val>([\.\./]+[a-zA-Z_]+[a-zA-Z0-9_\.\/]*))'
    RE_CONFIG_EQU = r'\s*=\s*'

    re_config_var = re.compile(RE_CONFIG_VAR + RE_CONFIG_EQU + RE_CONFIG_VAL)
    re_config_file = re.compile(RE_CONFIG_VAR + RE_CONFIG_EQU + RE_CONFIG_FILE)

    def is_assignment(self, string):
        """ Return True if string is an assignment. """
        return self.CONFIG_DELIMITER in string

    # Set configuration option default values
    configuration = {'debug': False,
                     'quiet': False,
                     'verbose': False,
                     'version': False}

    def set_debug(self, value):
        """ Set debug configuration flag to 'value' """
        self.configuration['debug'] = value.capitalize()

    def set_quiet(self, value):
        """ Set quiet configuration flag to 'value' """
        self.configuration['quiet'] = value.capitalize()

    def set_verbose(self, value):
        """ Set verbose configuration flag to 'value' """
        self.configuration['verbose'] = value.capitalize()

    def get_version(self, value):
        """ Return version entry. """
        pass

    # Source files to process
    source_files = []

    def add_file(self, value):
        """ Add file to list of files to process. """
        self.source_files.append(value)

    # Configuration File Directives
    DIRECTIVES = {
        'debug': set_debug,         # syntax: debug = True
        'quiet': set_quiet,         # syntax: quiet = True
        'verbose': set_verbose,     # syntax: verbose = True
        'version': get_version,     # syntax: TBS
        'file': add_file            # syntax: file = Filename.c
        }

    # =========================================================================
    def debug(self):
        """ Return current value of debug option. """
        return self.configuration['debug']

    def quiet(self):
        """ Return current value of quiet option. """
        return self.configuration['quiet']

    def verbose(self):
        """ Return current value of verbose option. """
        return self.configuration['verbose']

    def version(self):
        """ Return current value of version option. """
        return self.configuration['version']

    def files(self):
        """ Return current value of files list. """
        self.dbg.dprint(("Source Files:", self.source_files))
        return self.source_files

    # =========================================================================
    def __init__(self):
        """ Constructor """
        self.dbg = modules.DebugSupport.Debug()
        self.err = modules.ErrorHandling.Error()
        self.config_file_name = None
        self.config_file_object = None
        self.config_file_content = []  # configuration file contents
        self.config_file_index = 0
        self.config_file_lines = 0
        self.config_file_var = ''
        self.config_file_val = ''
        self.dbg.dprint(('ConfigurationFileParsing Init Complete', ''))

    # =========================================================================
    def read_config_file(self, config_file):
        """ Read configuration file and parse options. """
        self.open(config_file)
        self.read()
        self.close()
        for i in range(len(self.config_file_content)):
            self.parse_config(self.config_file_content[i])

        # Display switches after parsing configuration file
        self.dbg.dprint(('debug:', self.configuration['debug']))
        self.dbg.dprint(('quiet:', self.configuration['quiet']))
        self.dbg.dprint(('verbose:', self.configuration['verbose']))
        self.dbg.dprint(('version:', self.configuration['version']))

        # Display source files after parsing configuration file
        for source_file in self.source_files:
            self.dbg.dprint(('file:', source_file))

    # =========================================================================
    def parse_config(self, line):
        """ Parse a line from the configuration file. """

        # Perform mangle magic before we do any testing
        line = self.mangle(line)

        # Ignore blank lines
        if len(line) == 0:
            return

        self.dbg.dprint(('[Parse_Config]', line))

        # Parse and process any valid entries
        parse_var = self.re_config_var.match(line)
        parse_file = self.re_config_file.match(line)
        if parse_var is not None:
            self.config_file_var = parse_var.group('config_var')
            self.config_file_val = parse_var.group('config_val')
            self.dbg.dprint(('Config: Var=', self.config_file_var, 'Val=', self.config_file_val))
        elif parse_file is not None:
            self.config_file_var = parse_file.group('config_var')
            self.config_file_val = parse_file.group('config_val')
            self.dbg.dprint(('Config: Var=', self.config_file_var, 'Val=', self.config_file_val))
        else:
            self.dbg.dprint(('Bad Config:', line))
            self.err.config_file_parse_error(self.config_file_name)

        # Pull the trigger and see what happens
        try:
            var = self.config_file_var.lower()
            self.DIRECTIVES[var](self, self.config_file_val)
        except IOError as e:
            self.dbg.dprint(('IOError:', e, line))
            self.err.config_file_parse_error(self.config_file_name)
        except Exception as e:
            self.dbg.dprint(('ERROR:', e, line))
            self.err.config_file_parse_error(self.config_file_name)

    # =========================================================================
    def get_option(self, option):
        """ Return option value as read from the configuration file. """
        self.dbg.dprint(('get_option:', option))
        return self.configuration[option]

    # =========================================================================`
    def open(self, filename):
        """ Open requested file for reading. """
        self.config_file_name = filename
        self.dbg.dprint(('[Config_File_Open]', self.config_file_name))
        try:
            self.config_file_name = filename
            self.config_file_object = open(self.config_file_name, 'r')
        except IOError:
            self.err.config_file_open_error(self.config_file_name)

    # =========================================================================
    def read(self):
        """ Read file contents into array. """
        self.dbg.dprint(('[Config_File_Read]', self.config_file_name))
        try:
            self.config_file_content = self.config_file_object.read().splitlines()
            self.config_file_index = 0
            self.config_file_lines = len(self.config_file_content)
            self.dbg.dprint(('Config Lines read:', self.config_file_lines))
        except IOError:
            self.err.input_file_read_error(self.config_file_name)

    # =========================================================================
    def close(self):
        """ Close file. """
        self.dbg.dprint(('[Config_File_Close]', self.config_file_name))
        self.config_file_object.close()

    # =========================================================================
    def mangle(self, string):
        """ Return mangled version of string for parsing. """
        if isinstance(string, str):
            # strip comments
            comment = string.find(self.COMMENT_DELIMITER)
            if comment >= 0:
                string = string[:comment]
            # strip leading & trailing whitespace
            string.strip()
            # replace multiple whitespace with single space
            string = re.sub(r'\s+', ' ', string)
            return string
        else:
            # return empty string if not regular ascii
            return ''
