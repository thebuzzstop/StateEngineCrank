"""
    * Customer waiting room support for SleepingBarber(s) simulation
    * Provides synchronized access to waiting room for barber(s) and customer(s)
"""

# System imports
import sys
from threading import Lock as Lock
from queue import Queue as Queue

# Project imports
from SleepingBarber import Common
from mvc import Model


class CustomerWaitingError(Exception):
    """ No customer waiting to return """
    pass


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state  #: Borg class shared state


class WaitingRoom(Borg, Queue, Model):
    """ Waiting Room Implementation

        Implemented as a Borg so that all instantiations of the WaitingRoom class will
        utilize the same data for waiting customers

        * Implements a Queue (FIFO) for customers waiting for a haircut.
        * Implements a Lock to prevent deadlock and race conditions between barbers and customers.
        * Anyone calling a WaitingRoom function needs to obtain the lock before calling.
    """
    def __init__(self, chairs=None):
        """ Class constructor

            :param chairs: number of chairs in the waiting room
        """
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            if chairs is None:
                chairs = Common.Config.WaitingChairs
            Queue.__init__(self, maxsize=chairs)
            Model.__init__(self, name='WaitingRoom')

            self.lock = Lock()  #: waitingroom lock, needs to be obtained before calling WaitingRoom methods
            self.stats = Common.Statistics()    #: statistics module, used to gather simulation statistics

    def get_chair(self, customer):
        """ Function called by a customer to get a chair in the waiting room.
            It is assumed that the caller has obtained the WaitingRoom lock.

            :param customer: Customer class object of the customer needing a chair

            :returns: True : Chair available, customer added to the waiting queue
            :returns: False : No chair available
        """
        if self.full():
            chair = False
        else:
            self.put(customer, block=False)
            chair = True
            with self.stats.lock:
                self.stats.max_waiters = max(self.stats.max_waiters, self.qsize())
        self.logger('WR: get_chair [%s]' % chair)
        return chair

    def get_customer(self):
        """ Function called by a barber to get a customer from the waiting room.
            It is assumed that the caller has obtained the WaitingRoom lock.

            :returns: Customer object of the next waiting customer from the queue.

            :raises: CustomerWaitingError : no customer waiting.
        """
        if self.empty():
            raise CustomerWaitingError
        else:
            customer = self.get(block=False)
        self.logger('WR: get_customer [%s]' % customer.id)
        return customer

    def customer_waiting(self):
        """ Function to test if a customer is waiting.
            It is assumed that the caller has obtained the WaitingRoom lock.

            :returns: True : Customer is waiting
            :returns: False : No customer is waiting
        """
        if not self.empty():
            self.logger('WR: customer_waiting [TRUE]')
            return True
        else:
            self.logger('WR: customer_waiting [FALSE]')
            return False

    def update(self, event):
        """ Called by views or controllers to tell us to update
            We currently do nothing.
        """
        pass

    def run(self):
        pass
