"""BookMarks logging module"""

# System imports
import sys
import os
import logging.handlers

# define logging levels per logging module
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN


class Borg:

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state

class StreamHandlers(Borg):
    """Initialize logger stream handlers"""

    def __init__(self, log_level):
        Borg.__init__(self)
        if self._shared_state:
            return

        # only get stream handlers the first time
        self.ch = logging.StreamHandler(stream=sys.stdout)
        self.ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.ch.setLevel(log_level)
        self.fh = logging.handlers.RotatingFileHandler(filename = 'logs/bookmarks.log', maxBytes=2500000,
                                                    backupCount=5, delay=True)
        self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.fh.setLevel(log_level)
        if not os.path.exists('logs'):
            os.makedirs('logs')


class Logger:

    def set_level(self, logger_level: int = None, console_level: int = None, file_level: int = None):
        if logger_level is not None:
            self._logger.setLevel(logger_level)
        if console_level is not None:
            self.stream_handlers.ch.setLevel(console_level)
        if file_level is not None:
            self.stream_handlers.fh.setLevel(file_level)

    def __init__(self, name=__name__, log_level: int = INFO):
        """Constructor

        :param name: Logger name (typically the callers module)
        :param log_level: Logging level
        """
        # get stream handlers
        self.stream_handlers = StreamHandlers(log_level)

        # get a logger for this instantiation, set level and add handlers
        self._logger: logging.Logger = logging.getLogger(name)
        self._logger.setLevel(log_level)
        self._logger.addHandler(self.stream_handlers.ch)
        self._logger.addHandler(self.stream_handlers.fh)
        self._logger.propagate = False       # don't propagate to higher level(s)

    @property
    def logger(self) -> logging.Logger:
        """Property returning this logger object"""
        return self._logger


#: Characters to delete when cleaning text
delchars = str.maketrans({c: '' for c in map(chr, range(256)) if not c.isprintable()})


def clean(text: str) -> str:
   """Cleans up text by cleaning up non-printable chars

   :param text: Text string to be processed
   :returns: Cleaned up text with no non-printable chars
   """
   return text.translate(delchars)
