"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     Debug Support
@details:   Debug Support for StateEngineCrank

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
print('Loading modules: ', __file__, 'as', __name__)

import modules.CommandLineParsing       # noqa 408
import modules.Singleton                # noqa 408


class Debug(modules.Singleton.Singleton):
    """ Debug Support for StateEngineCrank. """

    # =========================================================================
    def __init__(self):
        cmd = modules.CommandLineParsing.CommandLine()
        self.debug = cmd.debug()
        self.verbose = cmd.verbose()
        self.quiet = cmd.quiet()
        self.seqid = 0
        self.dprint(('Debug ID:', id(self)))

    # =========================================================================
    def dvprint(self, params):
        """ Display debug message if Debug or Verbose are True."""
        if self.debug:
            self.dprint(params)
        elif self.verbose:
            self.vprint(params)

    # =========================================================================
    def dprint(self, params):
        """ Display debug message if Debug is True."""
        if self.debug:
            format_string = ' '.join(['%s'] * len(params))
            print('[', self.seqid, '] Debug:', format_string % params)

    # =========================================================================
    def vprint(self, params):
        """ Display debug message if Verbose is True."""
        if self.verbose:
            if len(params) == 1:
                print('%s' % params)
            elif len(params) > 1:
                format_string = ' '.join(['%s'] * len(params))
                print(format_string % params)

    # =========================================================================
    def set_seq_id(self, seqid):
        """ Update the debug sequence ID. """
        self.seqid = seqid

    # =========================================================================
    def seq_id(self):
        """ Return the debug sequence ID. """
        return self.seqid
