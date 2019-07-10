""" SleepingBarber.WaitingRoom

The Waiting Room module provides accommodations for customers who are waiting
for a barber to be available to cut hair.
The waiting room module utilizes a lock to ensure synchronized access to waiting
room for barber(s) and customer(s).
The waiting room lock must be obtained by anyone wanting access to the waiting room.

* The waiting room has a fixed number of chairs.
* If there is an empty chair, a customer arriving at the waiting room is assigned a chair and entered into a waiting queue.
* If there are no empty chairs the customer leaves the barber shop without a haircut.
* A barber that finishes cutting a customers hair checks the waiting room for a waiting customer.
"""

# System imports
import sys
from threading import Lock as Lock
from collections import deque

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


class WaitingRoom(Borg, Model):
    """ Waiting Room Implementation

        Implemented as a Borg so that all instantiations of the WaitingRoom class will
        utilize the same data for waiting customers

        * Implements a Queue (FIFO) for customers waiting for a haircut.
        * Implements a Lock to prevent deadlock and race conditions between barbers and customers.
        * Anyone calling a WaitingRoom function needs to obtain the lock before calling.
    """
    def __init__(self):
        """ WaitingRoom Class Constructor

            :param chairs: number of chairs in the waiting room
        """
        Borg.__init__(self)
        if len(self._shared_state) > 0:
            return
        Model.__init__(self, name='WaitingRoom')
        self.lock = Lock()  #: waitingroom lock, needs to be obtained before calling WaitingRoom methods
        self.chairs = Common.ConfigData().waiting_chairs
        self.stats = Common.Statistics()        #: statistics module, used to gather simulation statistics
        self.deque = deque(maxlen=self.chairs)  #: a queue of waiting room chairs
        self.customers_waiting = 0              #: number of customers waiting

    def reset(self):
        self.chairs = Common.ConfigData().waiting_chairs
        self.deque = deque(maxlen=self.chairs)
        self.customers_waiting = 0
        self.stats.reset()

    def get_chair(self, customer):
        """ Function called by a customer to get a chair in the waiting room.
            It is assumed that the caller has obtained the WaitingRoom lock.

            :param customer: Customer class object of the customer needing a chair

            :returns: True : Chair available, customer added to the waiting queue
            :returns: False : No chair available
        """
        if len(self.deque) == self.deque.maxlen:
            chair = False
        else:
            self.deque.append(customer)
            self.customers_waiting += 1
            chair = True
            with self.stats.lock:
                self.stats.max_waiters = max(self.stats.max_waiters, len(self.deque))
        self.logger('WR: get_chair [%s][%s][%s]' % (chair, self.customers_waiting, self.get_waiting_list_ids()))
        return chair

    def get_customer(self):
        """ Function called by a barber to get a customer from the waiting room.
            It is assumed that the caller has obtained the WaitingRoom lock.

            :returns: Customer object of the next waiting customer from the queue.

            :raises: CustomerWaitingError : no customer waiting.
        """
        if len(self.deque) == 0:
            raise CustomerWaitingError
        else:
            customer = self.deque.popleft()
            self.customers_waiting -= 1
        self.logger('WR: get_customer [%s][%s][%s]' %
                    (customer.id, self.customers_waiting, self.get_waiting_list_ids()))
        return customer

    def get_waiting_list_ids(self):
        waiting_list = []
        for c in range(len(self.deque)):
            waiting_list.append(self.deque[c].id)
        return waiting_list

    def get_waiting_list(self):
        """ Returns a list of the waiting customers

            In general, anyone calling a WaitingRoom function needs to obtain the lock before calling.
            This is one case where we will acquire the lock on behalf of the caller.

            :returns: current state of the waiting queue
        """
        with self.lock:
            waiting_list = []
            for c in range(len(self.deque)):
                waiting_list.append(self.deque[c])
            return waiting_list

    def customer_waiting(self):
        """ Function to test if a customer is waiting.
            It is assumed that the caller has obtained the WaitingRoom lock.

            :returns: True : Customer is waiting
            :returns: False : No customer is waiting
        """
        if len(self.deque) > 0:
            self.logger('WR: customer_waiting [TRUE]')
            return True
        else:
            self.logger('WR: customer_waiting [FALSE]')
            return False

    def full(self):
        """ Function to return state of waitingroom
            It is assumed that the caller has obtained the WaitingRoom lock.

            :returns: True if waitingroom is full
        """
        return len(self.deque) == self.deque.maxlen

    def update(self, event):
        """ Called by views or controllers to tell us to update
            We currently do nothing.
        """
        pass

    def run(self):
        pass
