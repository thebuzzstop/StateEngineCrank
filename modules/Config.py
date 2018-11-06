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

# system imports
import argparse
import configparser
import re

# project specific imports
import modules.Defines as Defines
import modules.Singleton as Singleton


class TheConfig(Singleton.Singleton):
    """ Implements TheConfig Class
        Pulls together options specified on the command line and
        and in the optional configuration file.
    """

    debug = False
    verbose = False
    quiet = False
    version = False
    files = []

    # =========================================================================
    def __init__(self):
        """ Constructor """
        super().__init__()
        self.cfg = CfgParser()      # parse first
        self.cmd = ArgParser()      # parse last, may override config file

        self.debug = self.cfg.debug or self.cmd.debug
        self.verbose = self.cmd.verbose or (self.cfg.verbose and not self.cmd.quiet)
        self.quiet = self.cmd.quiet or (self.cfg.quiet and not self.cmd.verbose)
        self.debug = self.cmd.debug or self.cfg.debug
        self.version = self.cmd.version or self.cfg.version

        self.files.append(self.cfg.files)
        self.files.append(self.cmd.files)

        print('files: %s' % self.files)

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
        self.config = None
        self.version = None
        self.files = []

        self.args = parser.parse_args()
        if self.verbose:
            self.verbose = True
        if self.quiet:
            self.quiet = True
        if self.debug:
            self.debug = True


class CfgParser(configparser.ConfigParser):
    """ Implements the configuration file parser """

    # =========================================================================
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read(Defines.DEFAULT_CONFIG_FILE)

        self.verbose = False
        self.quiet = False
        self.debug = False
        self.version = None
        self.files = []

        # check configuration file for user configuration items
        if 'verbose' in self.config['mode']:
            self.verbose = self.config['mode']['verbose']
        if 'debug' in self.config['mode']:
            self.debug = self.config['mode']['debug']
        if 'quiet' in self.config['mode']:
            self.quiet = self.config['mode']['quiet']
        if 'version' in self.config['info']:
            self.version = self.config['info']['version']
        if 'file' in self.config['files']:
            self.files = re.sub(r'\s+', '', self.config['files']['file']).split(',')
