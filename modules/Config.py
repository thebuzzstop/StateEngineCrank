"""
Created on Jun 29, 2016

@author:    Mark B Sawyer
@date:      Jun 29, 2016

@package:   /home/mark/Eclipse/eclipse/plugins/org.python.pydev_5.0.0.201605051159/pysrc
@module:    modules.Config.TheConfig

@brief:     Implements TheConfig Class
@details:   Implements TheConfig Class - pulls together options specified on the command line and
            and in the configuration file.

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
# System imports
import os
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

import argparse         # noqa 408
import configparser     # noqa 408
import re               # noqa 408

# project specific imports
import modules.Defines as Defines       # noqa 408
import modules.Singleton as Singleton   # noqa 408
import modules.ErrorHandling as Error   # noqa 408


class TheConfig(Singleton.Singleton):
    """ Implements TheConfig Class
        Pulls together options specified on the command line and
        and in the optional configuration file.
    """

    config_file = Defines.DEFAULT_CONFIG_FILE
    debug = False
    verbose = False
    quiet = False
    version = False
    files = []

    # =========================================================================
    def __init__(self):
        """ Constructor """
        super().__init__()
        self.cmd = ArgParser()      # parse first, may override config file
        self.cfg = CfgParser()      # parse last
        self.debug = self.cfg.debug or self.cmd.debug
        self.verbose = self.cmd.verbose or (self.cfg.verbose and not self.cmd.quiet)
        self.quiet = self.cmd.quiet or (self.cfg.quiet and not self.cmd.verbose)
        self.version = self.cmd.version or self.cfg.version
        self.files.extend(self.cfg.files)
        self.files.extend(self.cmd.files)
        logging.debug('files: %s' % self.files)


class ArgParser(argparse.ArgumentParser):
    """ Implements the command line argument parser """

    # =========================================================================
    def __init__(self):
        super().__init__()
        parser = argparse.ArgumentParser(description=Defines.MY_DESCRIPTION)

        # parse quiet/verbose are mutually exclusive
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument('-q', '--quiet',   action='store_true', help='enable quiet mode')
        verbosity.add_argument('-v', '--verbose', action='store_true', help='enable maximum verbosity')

        parser.add_argument('-d', '--debug',   action='store_true', help='enable debug support')
        parser.add_argument('-V', '--version', action='version',    help='display program version',
                            version='%(prog)s ' + Defines.VERSION)

        # configuration file is optional
        parser.add_argument('-c', '--config',  nargs='?', help='optional configuration file')

        # gather up the rest of the command line as file to process
        parser.add_argument('files', nargs='*', help='list of files to process')

        self.verbose = False
        self.quiet = False
        self.debug = False
        self.version = False
        self.files = []

        self.args = parser.parse_args()
        if hasattr(self.args, 'verbose'):
            self.verbose = self.args.verbose
        if hasattr(self.args, 'quiet'):
            self.quiet = self.args.quiet
        if hasattr(self.args, 'debug'):
            self.debug = self.args.debug

        # if user specifies a configuration file then update
        # TheConfig.config_file for config file parsing
        if hasattr(self.args, 'config'):
            TheConfig.config_file = self.args.config


class CfgParser(configparser.ConfigParser):
    """ Implements the configuration file parser """

    # =========================================================================
    def __init__(self):
        super().__init__()
        self.error = Error.Error()
        self.config_file = TheConfig.config_file
        self.config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            self.config.read(self.config_file)
        else:
            raise self.error.config_file_missing_error(self.config_file)

        self.verbose = False
        self.quiet = False
        self.debug = False
        self.version = False
        self.files = []

        # check configuration file for user configuration items
        if 'mode' in self.config:
            if 'verbose' in self.config['mode']:
                self.verbose = self.make_boolean(self.config['mode']['verbose'])
            if 'debug' in self.config['mode']:
                self.debug = self.make_boolean(self.config['mode']['debug'])
            if 'quiet' in self.config['mode']:
                self.quiet = self.make_boolean(self.config['mode']['quiet'])
        if 'info' in self.config:
            if 'version' in self.config['info']:
                self.version = self.make_boolean(self.config['info']['version'])
        if 'files' in self.config:
            for fkey in self.config['files'].keys():
                if fkey.startswith('file'):
                    # self.files = re.sub(r'\s+', '', self.config['files']['file']).split(',')
                    self.files.append(self.config['files'][fkey])

    def make_boolean(self, value):
        if str(value).lower() == 'true':
            return True
        if str(value).lower() == 'false':
            return False
        raise self.error.config_file_parse_error(self.config_file)
