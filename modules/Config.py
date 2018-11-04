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

import argparse
import configparser

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


class ArgParser(argparse.ArgumentParser):
    """ Implements the command line argument parser """

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

        self.args = parser.parse_args()

    # =========================================================================
    def config(self):
        """ Return True if configuration file specified. """
        return self.args.config

    # =========================================================================
    def debug(self):
        """ Return status of debug flag. """
        return self.args.debug

    # =========================================================================
    def quiet(self):
        """ Return status of quiet flag. """
        return self.args.quiet

    # =========================================================================
    def verbose(self):
        """ Return status of verbose flag. """
        return self.args.verbose

    # =========================================================================
    def parse(self):
        """ Parse/display status of our flags. """
        if self.args.verbose:
            print('Verbose mode enabled')

        if self.args.debug:
            print('Debug mode enabled')

        if self.args.quiet and self.args.debug:
            print('Quiet mode enabled')

    # =========================================================================
    def files(self):
        """ Display list of files to be processed. """
        if self.args.verbose or self.args.debug:
            print('Files: %s' % self.args.files)
        return self.args.files


class CfgParser(configparser.ConfigParser):
    """ Implements the configuration file parser """

    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read(Defines.DEFAULT_CONFIG_FILE)

        # check configuration file for user configuration items
        if 'verbose' in self.config['mode']:
            TheConfig.verbose = self.config['mode']['verbose']
        if 'debug' in self.config['mode']:
            TheConfig.debug = self.config['mode']['debug']
        if 'quiet' in self.config['mode']:
            TheConfig.quiet = self.config['mode']['quiet']
        if 'version' in self.config['info']:
            TheConfig.version = self.config['info']['version']
        if 'file' in self.config['files']:
            for key, value in self.config.items('files'):
                print("config: %s = %s" % (key, value))
