"""
* Shared code and configuration definitions
"""

# System imports
import random
from threading import Lock as Lock
import time

# Project imports


class Config(object):
    """ SleepingBarber configuration items """
    HairCut_Min = 9         #: minimum number of seconds to cut hair
    HairCut_Max = 13        #: maximum number of seconds to cut hair
    Barbers = 4             #: number of barbers cutting hair
    WaitingChairs = 4       #: number of chairs in the waiting room
    CustomerRate = 3        #: rate for new customers
    CustomerVariance = 1    #: variance in the customer rate
    SimulationLoops = 100   #: total number of loops (seconds) to run

    @staticmethod
    def seconds(minimum, maximum):
        """ Function to return a random integer between 'minimum' and 'maximum'.

            * Used as the number of seconds for a haircut.
            * Used as the number of seconds between new customers.

            :param minimum: range minimum value
            :param maximum: range maximum value
            :returns: Random number between minimum and maximum
        """
        return random.randint(minimum, maximum)

    @staticmethod
    def cutting_time():
        """ Utility function to return a random time between minimum and maximum
            time specified in the configuration class

            :returns: Random cutting time
        """
        return Config.seconds(Config.HairCut_Min, Config.HairCut_Max)


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same
        state and behavior.

        Taken from `The Python Cookbook
        <https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html>`_
        by David Ascher, Alex Martelli
    """
    _shared_state = {}

    def __init__(self):
        """ Class constructor """
        self.__dict__ = self._shared_state  #: Borg class shared state


class Statistics(Borg):
    """ This class is used by both barbers and customers to collect statistics.

        Implemented as a Borg, it can be instantiated as many times as necessary.
    """

    def __init__(self):
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            self.lock = Lock()      #: obtained by callers to ensure sole access
            self.customers = []     #: list of customers instantiated in the simulation
            self.barbers = []       #: list of barbers instantiated in the simulation
            self.max_waiters = 0    #: maximum number of waiters encountered during the simulation
            self.barber_sleeping_time = 0       #: total sleeping time for all barbers
            self.barber_cutting_time = 0        #: total cutting time for all barbers
            self.barber_total_customers = 0     #: total number of customers served
            self.lost_customers = 0             #: number of customers lost due to no chairs in waiting room
            self.simulation_start_time = 0      #: clock time, start of simulation
            self.simulation_finish_time = 0     #: clock time, finish time of simulation
            self.customers_cutting_time = 0     #: total cutting time for all customers
            self.customers_waiting_time = 0     #: total waiting time for all customers
            self.customers_elapsed_time = 0     #: total elapsed time for all customers
            self.customers_simulation_time = 0  #: total simulation time (cutting + waiting) for all customers
            self.simulation_start_time = time.time()

    def print_customer_stats(self):
        """ Calculates and prints customer statistics

        Calculates:
            * total customers elapsed time
            * total customers cutting time
            * total customers waiting time
            * total customers simulation time

        Prints:
            * individual customer statistics
            * cumulative statistics for all customers
        """

        # sort customers by ID
        customers = sorted(self.customers, key=lambda customer: customer.id)

        # Print some customer statistics of the simulation
        for c in range(len(customers)):
            customer = customers[c]
            elapsed_time = customer.finish_time - customer.start_time
            simulation_time = customer.cutting_time + customer.waiting_time
            self.customers_elapsed_time += elapsed_time
            self.customers_simulation_time += simulation_time
            self.customers_cutting_time += customer.cutting_time
            self.customers_waiting_time += customer.waiting_time
            print('customer[%03d] start: %4.2d  finish: %4.2d  elapsed: %3.2d  cutting: %2d  waiting: %2d  simulation: %2d' %
                (customer.id,
                 customer.start_time - self.simulation_start_time,
                 customer.finish_time - self.simulation_start_time,
                 elapsed_time,
                 customer.cutting_time,
                 customer.waiting_time,
                 simulation_time))

        print('\nelapsed: %4.2d  cutting: %3d  waiting: %3d  simulation: %3d' %
              (self.customers_elapsed_time, self.customers_cutting_time,
               self.customers_waiting_time, self.customers_simulation_time))

    def print_barber_stats(self):
        """ Prints statistics for all barbers

            * total barber sleeping time
            * total barber cutting time
            * total barber customers
        """

        # Sort barber array by ID
        barbers = sorted(self.barbers, key=lambda barber: barber.id)

        # Print some barber statistics of the simulation
        for b in range(len(barbers)):
            barber = barbers[b]
            self.barber_sleeping_time += barber.sleeping_time
            self.barber_cutting_time += barber.cutting_time
            self.barber_total_customers += barber.customers
            print('barber[%s] customers: %3d  cutting: %3d  sleeping: %3d' %
                  (barber.id, barber.customers, barber.cutting_time, barber.sleeping_time))

    def print_summary_stats(self):
        """ Prints summary statistics for barbers and customers

            * total barber customers
            * total barber sleeping time
            * total barber cutting time
            * total customer waiting time
            * number of lost customers (no chairs)
            * maximum number of customer waiting
        """
        print('Customers: %d  Sleeping: %d  Cutting: %d  Waiting: %d  Lost Customers: %d  Max Waiting: %d' %
              (self.barber_total_customers, self.barber_sleeping_time, self.barber_cutting_time,
               self.customers_waiting_time, self.lost_customers, self.max_waiters))
