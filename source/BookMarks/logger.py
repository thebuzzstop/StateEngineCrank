# System imports
import sys
import os
import logging.handlers

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARN


class Borg(object):

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Logger(Borg):

    def set_level(self, logger_level: int = None, console_level: int = None, file_level: int = None):
        if logger_level is not None:
            self.logger.setLevel(logger_level)
        if console_level is not None:
            self.ch.setLevel(console_level)
        if file_level is not None:
            self.fh.setLevel(file_level)

    def __init__(self, name=__name__, log_level: int = INFO):
        Borg.__init__(self)
        if not self._shared_state:
            # only get stream handlers the first time
            self.ch = logging.StreamHandler(stream=sys.stdout)
            self.ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
            self.ch.setLevel(log_level)

            self.fh = logging.handlers.RotatingFileHandler('logs/bookmarks.log', maxBytes=2500000, backupCount=5,
                                                           delay=True)
            self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.fh.setLevel(log_level)
            if not os.path.exists('logs'):
                os.makedirs('logs')
            self.delchars = str.maketrans({c: '' for c in map(chr, range(256)) if not c.isprintable()})

        # get a logger for this instantiation, set level and add handlers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.addHandler(self.ch)
        self.logger.addHandler(self.fh)

    def clean(self, text: str) -> str:
        """ Cleans up text by cleaning up non-printable chars

            :param text: Text string to be cleaned up
            :returns: Cleaned up text with no non-printable chars
        """
        text = text.translate(self.delchars)
        return text
