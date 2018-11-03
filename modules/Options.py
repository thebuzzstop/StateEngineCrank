"""
Created on Jun 29, 2016

@author:    Mark B Sawyer
@date:      Jun 29, 2016

@package:   /home/mark/Eclipse/eclipse/plugins/org.python.pydev_5.0.0.201605051159/pysrc
@module:    modules.Options

@brief:     Implements Options Class
@details:   Implements Options Class - pulls together options specified on the command line and
            and in the configuration file.

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""

import modules.CommandLineParsing
import modules.ConfigurationFileParsing


class Options(object):
    """ Implements Options Class
        Pulls together options specified on the command line and
        and in the optional configuration file.
    """

    # =========================================================================
    def __init__(self):
        """ Constructor """
        self.cmdline = modules.CommandLineParsing.CommandLine()
        self.cfgfile = modules.ConfigurationFileParsing.ConfigFile()

    # =========================================================================
    def debug(self):
        """ Return status of debug option. """
        return self.cmdline.debug() or self.cfgfile.debug()

    # =========================================================================
    def quiet(self):
        """ Return status of quiet option.
            Note that the command line has a higher priority than the
            configuration file. """
        return self.cmdline.quiet() or (self.cfgfile.quiet() and not self.cmdline.verbose())

    # =========================================================================
    def verbose(self):
        """ Return status of verbose option.
            Note that the command line has a higher priority than the
            configuration file. """
        return self.cmdline.verbose() or (self.cfgfile.verbose() and not self.cmdline.quiet())

    # =========================================================================
    def files(self):
        """ Return list of files specified on the command Line
            and in the configuration file. """

        # Get a list of source files from configuration file
        cfg = modules.ConfigurationFileParsing.ConfigFile()
        files_cfg = cfg.files()

        # Get a list of source files from command line
        cmd = modules.CommandLineParsing.CommandLine()
        files_cmd = cmd.files()

        if self.debug():
            for filename in files_cfg:
                print('cfgfile:', filename)
            for filename in files_cmd:
                print('cmdline:', filename)

        # Return a list of unique values from cfgfile and cmdline
        # Note that the idiom list(set(a+b)) was snarfed from
        # StackOverflow (get-only-unique-elements-from-two-lists-python)
        return list(set(files_cfg + files_cmd))
