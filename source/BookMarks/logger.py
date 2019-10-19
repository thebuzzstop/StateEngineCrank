# System imports
import sys
import os
import logging.handlers


class Logger(object):

    def __init__(self, name):

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler(stream=sys.stdout)
        self.ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        self.ch.setLevel(logging.INFO)
        self.logger.addHandler(self.ch)

        if not os.path.exists('logs'):
            os.makedirs('logs')

        self.fh = logging.handlers.RotatingFileHandler('logs/bookmarks.log', backupCount=5, delay=True)
        self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.fh.setLevel(logging.DEBUG)
        self.logger.addHandler(self.fh)

    def rollover(self):
        self.fh.doRollover()
