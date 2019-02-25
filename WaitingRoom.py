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
from threading import Lock as Lock
from queue import Queue as Queue

# Project imports
import Customer
import Common

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))


class CustomerWaitingError(Exception):
    """ No customer waiting to return """
    pass


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same
        state and behavior.

        Taken from "Python Cookbook" by David Ascher, Alex Martelli
        https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html
    """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class WaitingRoom(Borg, Queue):
    """ Waiting Room Implementation

        Implemented as a Borg so that all instantiations of the WaitingRoom class will
        utilize the same data for waiting customers
    """
    def __init__(self, chairs=None):
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            if chairs is None:
                chairs = Common.Config.WaitingChairs
            Queue.__init__(self, maxsize=chairs)
            self.lock = Lock()
            self.stats = Common.Statistics()

    def get_chair(self, customer):
        if self.full():
            chair = False
        else:
            self.put(customer, block=False)
            chair = True
            with self.stats.lock:
                self.stats.max_waiters = max(self.stats.max_waiters, self.qsize())
        logging.debug('WR: get_chair [%s]' % chair)
        return chair

    def get_customer(self):
        if self.empty():
            raise CustomerWaitingError
        else:
            customer = self.get(block=False)
        logging.debug('WR: get_customer [%s]' % customer.customer_id)
        return customer

    def customer_waiting(self):
        if not self.empty():
            logging.debug('WR: customer_waiting [TRUE]')
            return True
        else:
            logging.debug('WR: customer_waiting [FALSE]')
            return False
