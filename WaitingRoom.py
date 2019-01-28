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

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same
        state and behavior.

        Taken from "Python Cookbook" by David Ascher, Alex Martelli
        https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html
    """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class ChairStatus(enum.Enum):
    Free = 0
    InUse = 1


class WaitingRoom(Borg):
    """ Waiting Room Implementation

        Implemented as a Borg so that all instantiations of the WaitingRoom class will
        utilize the same data for waiting customers
    """
    def __init__(self, chairs):
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            self.waiting_customers = 0
            self.chairs = [ChairStatus.Free for _ in range(chairs)]
            self.lock = threading.Lock()
