"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     Error Handling
@details:   Error Handling for StateEngineCrank

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
# System imports
import inspect
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports
import modules.Singleton    # noqa 408


class ConfigFileError(Exception):
    """ Error encountered while processing configuration file. """
    pass


class FileBackupError(Exception):
    """ Error encountered during file backup. """
    pass


class FileWriteError(Exception):
    """ Error encountered during file write. """
    pass


class FileTypeError(Exception):
    """ Unknown file type error encountered """
    pass


class ScanCodeError(Exception):
    """ Error encountered while scanning code. """
    pass


class SignatureError(Exception):
    """ Error encountered while processing signature. """
    pass


class SourceFileError(Exception):
    """ Error encountered while processing source file. """
    pass


class UMLParseError(Exception):
    """ Error encountered while parsing UML."""
    pass


class UnimplementedCodeError(Exception):
    """ Error encountered --- Unimplemented code. """
    pass


class FunctionTypeError(Exception):
    """ Error encountered --- Function type not found. """
    pass


class UpdateCodeError(Exception):
    """ Error encountered wile updating code. """
    pass


class Error(modules.Singleton.Singleton):
    """ Error Handling for StateEngineCrank. """

    # =========================================================================
    def __init__(self):
        pass

    # =========================================================================
    @staticmethod
    def lineno():
        return inspect.currentframe().f_back.f_lineno

    # =========================================================================
    @staticmethod
    def config_file_open_error(filename):
        """ Config File Open Error - display message and raise source file error."""
        logging.fatal('ERROR: Configuration File Open Error: %s' % filename)
        raise ConfigFileError(filename)

    # =========================================================================
    @staticmethod
    def config_file_parse_error(filename):
        """ Config File Parse Error - display message and raise source file error."""
        logging.fatal('ERROR: Configuration File Parse Error: %s' % filename)
        raise ConfigFileError(filename)

    # =========================================================================
    @staticmethod
    def config_file_missing_error(filename):
        """ Config File Parse Error - display message and raise source file error."""
        logging.fatal('ERROR: Configuration File Missing Error: %s' % filename)
        raise ConfigFileError(filename)

    # =========================================================================
    @staticmethod
    def input_file_open_error(filename):
        """ Input File Open Error - display message and raise source file error."""
        logging.fatal('ERROR: File Open Error: %s' % filename)
        raise SourceFileError(filename)

    # =========================================================================
    @staticmethod
    def input_file_read_error(filename):
        """ Input File Read Error - display message and raise file read error."""
        logging.fatal('ERROR: File Read Error: %s' % filename)
        raise SourceFileError(filename)

    # =========================================================================
    @staticmethod
    def input_file_close_error(filename):
        """ Input File Close Error - display message and raise file close error. """
        logging.fatal('ERROR: File Close Error: %s' % filename)
        raise SourceFileError(filename)

    # =========================================================================
    @staticmethod
    def output_file_open_error(filename):
        """ Output File Open Error - display message and raise IOError. """
        logging.fatal('ERROR: File Open Error: %s' % filename)
        raise IOError

    # =========================================================================
    @staticmethod
    def output_file_write_error(filename):
        """ Output File Write Error - display message and raise IOError. """
        logging.fatal('ERROR: File Write Error: %s' % filename)
        raise IOError

    # =========================================================================
    @staticmethod
    def output_file_close_error(filename):
        """ Output File Close Error - display message and raise IOError. """
        logging.fatal('ERROR: File Close Error: %s' % filename)
        raise IOError

    # =========================================================================
    @staticmethod
    def uml_not_found(error_string):
        """ UML Not Found - display message and punt. """
        logging.fatal('ERROR: UML_NotFound: %s' % error_string)
        raise UMLParseError

    # =========================================================================
    @staticmethod
    def uml_statemachine_not_found():
        """ UML State Machine Not Found - display message and punt. """
        logging.fatal('ERROR: UML State Machine Not Found')
        raise UMLParseError

    # =========================================================================
    @staticmethod
    def invalid_start_end(start, end):
        """ Invalid UML start and/or end - display message and punt. """
        logging.fatal('ERROR: Invalid UML: start=%s end=%s' % (start, end))
        raise UMLParseError

    # =========================================================================
    @staticmethod
    def file_index_error(index):
        """ Bad file index encountered - display message and punt. """
        logging.fatal('ERROR: Bad file index: %s' % index)
        raise Exception

    # =========================================================================
    @staticmethod
    def signature_scan_error(filename):
        """ Error scanning signature - display message and punt. """
        logging.fatal('ERROR: Signature scanning error.')
        raise SourceFileError(filename)

    # =========================================================================
    @staticmethod
    def signature_not_found(signature):
        """ Signature not found - display message and punt. """
        logging.fatal('ERROR: Signature %s not found error.' % signature)
        raise SignatureError(signature)

    # =========================================================================
    @staticmethod
    def function_type_not_found(func):
        """ Function type not found - display message and punt. """
        logging.fatal('ERROR: Function %s not found error.' % func)
        raise FunctionTypeError(func)

    # =========================================================================
    @staticmethod
    def bad_file_index(index):
        """ Bad file index encountered - display message and punt. """
        logging.fatal('ERROR: Bad File Index: %s' % index)
        raise Exception

    # =========================================================================
    @staticmethod
    def file_type_error(file_type):
        """ Unknown file type encountered - display message and punt. """
        logging.fatal('ERROR: Unknown file type: %s' % file_type)
        raise Exception

    # =========================================================================
    @staticmethod
    def unimplemented(msg, line):
        """ Unimplemented code - display message and punt. """
        logging.fatal('ERROR: Unimplemented code: %s @ line #%s' % (msg, line))
        raise UnimplementedCodeError


class Warn(modules.Singleton.Singleton):
    """ Warning for StateEngineCrank. """

    # =========================================================================
    def __init__(self):
        pass

    # =========================================================================
    @staticmethod
    def uml_not_found(warning_string):
        """ UML Not Found - display message and punt. """
        logging.warning('WARNING: UML_NotFound: %s' % warning_string)
