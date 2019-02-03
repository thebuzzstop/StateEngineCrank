#!/usr/bin/env python
"""
Created on January 25, 2019

@author:    Mark Sawyer
@date:      27-Jan-2019

@package:   WaitingRoom
@brief:     Customer waiting room support for SleepingBarber(s) simulation
@details:   Provides synchronized access to waiting room for barber(s) and customer(s)

@copyright: Mark B Sawyer, All Rights Reserved 2019
"""

# System imports
import logging
import sys
import threading
import enum

# Project imports
from Borg import Borg

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))


class ChairStatus(enum.Enum):
    Free = 0
    InUse = 1


class WaitingRoom(Borg):
    """ Waiting Room Implementation

        Implemented as a Borg so that all instantiations of the WaitingRoom class will
        utilize the same data for waiting customers
    """
    def __init__(self, chairs=None):
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            if chairs is not None:
                self.chairs = [ChairStatus.Free for _ in range(chairs)]
            self.lock = threading.Lock()

    def get_chair(self):
        with self.lock:
            for chair in range(len(self.chairs)):
                if self.chairs[chair] is ChairStatus.Free:
                    self.chairs[chair] = ChairStatus.InUse
                    return True
            return False

    def get_customer(self):
        with self.lock:
            for chair in range(len(self.chairs)):
                if self.chairs[chair] is ChairStatus.InUse:
                    self.chairs[chair] = ChairStatus.Free
                    return True
            return False
