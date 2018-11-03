"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     Command Line Parsing
@details:   Command Line Parsing for StateEngineCrank

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
print('Loading modules: ', __file__, 'as', __name__)

import argparse             # noqa 408
import modules.Singleton    # noqa 408

VERSION = '1.0'
MY_DESCRIPTION = 'StateEngineCrank command line utility.'


class CommandLine(modules.Singleton.Singleton):
    """ Command Line Parsing for StateEngineCrank. """

    # =========================================================================
    def __init__(self):
        # parse command line for switches and files to process
        parser = argparse.ArgumentParser(description=MY_DESCRIPTION)

        # parse quiet/verbose are mutually exclusive
        verbosity = parser.add_mutually_exclusive_group()
        verbosity.add_argument('-q', '--quiet',   action='store_true', help='enable quiet mode')
        verbosity.add_argument('-v', '--verbose', action='store_true', help='enable maximum verbosity')

        parser.add_argument('-d', '--debug',   action='store_true', help='enable debug support')
        parser.add_argument('-V', '--version', action='version',    help='display program version',
                            version='%(prog)s ' + VERSION)

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
