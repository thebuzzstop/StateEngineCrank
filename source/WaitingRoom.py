##
# @package    SleepingBarber.WaitingRoom
# @brief:     Customer waiting room support for SleepingBarber(s) simulation
# @details:   Provides synchronized access to waiting room for barber(s) and customer(s)
# @author:    Mark Sawyer
# @date:      27-Jan-2019

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
        """ Class constructor """
        self.__dict__ = self._shared_state


class WaitingRoom(Borg, Queue):
    """ Waiting Room Implementation

        Implemented as a Borg so that all instantiations of the WaitingRoom class will
        utilize the same data for waiting customers

        Implements a Queue (FIFO) for customers waiting for a haircut.
        Implements a Lock to prevent deadlock and race conditions between barbers and customers.
        Anyone calling a WaitingRoom function needs to obtain the lock before calling.
    """
    def __init__(self, chairs=None):
        """ Class constructor
            @param chairs - number of chairs in the waiting room
        """
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            if chairs is None:
                chairs = Common.Config.WaitingChairs
            Queue.__init__(self, maxsize=chairs)

            ## @var lock
            # waitingroom lock, needs to be obtained before calling WaitingRoom methods
            self.lock = Lock()

            ## @var stats
            # statistics module, used to gather simulation statistics
            self.stats = Common.Statistics()

    def get_chair(self, customer):
        """ Function called by a customer to get a chair in the waiting room
            It is assumed that the caller has obtained the WaitingRoom lock.

            @param customer - class object of the customer needing a chair
            @retval True - Chair available, customer added to the waiting queue
            @retval False - No chair available
        """
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
        """ Function called by a barber to get a customer from the waiting room
            It is assumed that the caller has obtained the WaitingRoom lock.

            @returns Customer object of the next waiting customer from the queue.
            @exception Raises CustomerWaitingError if there is no customer waiting.
        """
        if self.empty():
            raise CustomerWaitingError
        else:
            customer = self.get(block=False)
        logging.debug('WR: get_customer [%s]' % customer.id)
        return customer

    def customer_waiting(self):
        """ Function to test if a customer is waiting
            It is assumed that the caller has obtained the WaitingRoom lock.
            @retval True - Customer is waiting
            @retval False - No customer is waiting
        """
        if not self.empty():
            logging.debug('WR: customer_waiting [TRUE]')
            return True
        else:
            logging.debug('WR: customer_waiting [FALSE]')
            return False
