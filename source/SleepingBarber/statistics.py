""" Sleeping Barber(s) Configuration """

# System imports
from threading import Lock as Lock
import time

# Project imports


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self, myclass):
        if myclass not in self._shared_state.keys():
            self._shared_state[myclass] = {}
        self.__dict__ = self._shared_state[myclass]


class Statistics(Borg):
    """ This class is used by both barbers and customers to collect statistics.

        Implemented as a Borg, it can be instantiated as many times as necessary.
    """
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __init__(self):
        Borg.__init__(self, 'statistics')
        if len(self._shared_state['statistics']):
            return
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

        # Summary statistics - fetchable as strings
        self._customer_stats = ''
        self._barber_stats = ''
        self._summary_stats = ''

    def reset(self):
        self.customers = []
        self.barbers = []
        self.max_waiters = 0
        self.barber_sleeping_time = 0
        self.barber_cutting_time = 0
        self.barber_total_customers = 0
        self.lost_customers = 0
        self.simulation_start_time = 0
        self.simulation_finish_time = 0
        self.customers_cutting_time = 0
        self.customers_waiting_time = 0
        self.customers_elapsed_time = 0
        self.customers_simulation_time = 0
        self.simulation_start_time = time.time()
        self._customer_stats = ''
        self._barber_stats = ''
        self._summary_stats = ''

    def customer_stats(self):
        """ Compiles customer statistics for the simulation

        Calculates:
            * total customers elapsed time
            * total customers cutting time
            * total customers waiting time
            * total customers simulation time

        Returns:
            * individual customer statistics
            * cumulative statistics for all customers

        :returns: Statistics for all customers (string)
        """

        # sort customers by ID
        customers = sorted(self.customers, key=lambda customer_: customer_.id)

        # Compile customer statistics for the simulation
        self._customer_stats = 'Customer Statistics:'
        for c in range(len(customers)):
            customer = customers[c]
            elapsed_time = customer.finish_time - customer.start_time
            simulation_time = customer.cutting_time + customer.waiting_time
            self.customers_elapsed_time += elapsed_time
            self.customers_simulation_time += simulation_time
            self.customers_cutting_time += customer.cutting_time
            self.customers_waiting_time += customer.waiting_time
            self._customer_stats = self._customer_stats + \
                '\ncustomer[%03d] start: %4.2d  finish: %4.2d  elapsed: %3.2d  cutting: %2d  waiting: %2d  simulation: %2d' % \
                (customer.id,
                 customer.start_time - self.simulation_start_time,
                 customer.finish_time - self.simulation_start_time,
                 elapsed_time,
                 customer.cutting_time,
                 customer.waiting_time,
                 simulation_time)

        self._customer_stats = self._customer_stats + \
            '\n\nCustomer Totals:\nelapsed: %4.2d  cutting: %3d  waiting: %3d  simulation: %3d' % \
            (self.customers_elapsed_time, self.customers_cutting_time,
             self.customers_waiting_time, self.customers_simulation_time)

        return self._customer_stats + '\n'

    def barber_stats(self):
        """ Compiles statistics for all barbers

            * total barber sleeping time
            * total barber cutting time
            * total barber customers

            :returns: Statistics for all barbers (string)
        """

        # Sort barber array by ID
        barbers = sorted(self.barbers, key=lambda barber_: barber_.id)

        # Compile barber statistics for the simulation
        self._barber_stats = 'Barber Statistics:'
        for b in range(len(barbers)):
            barber = barbers[b]
            self.barber_sleeping_time += barber.sleeping_time
            self.barber_cutting_time += barber.cutting_time
            self.barber_total_customers += barber.customers
            self._barber_stats = self._barber_stats + \
                '\nbarber[%s] customers: %3d  cutting: %3d  sleeping: %3d' % \
                (barber.id, barber.customers, barber.cutting_time, barber.sleeping_time)

        return self._barber_stats + '\n'

    def summary_stats(self):
        """ Compiles summary statistics for barbers and customers

            * total barber customers
            * total barber sleeping time
            * total barber cutting time
            * total customer waiting time
            * number of lost customers (no chairs)
            * maximum number of customer waiting

            :returns: Compiled summary statistics (string)
        """
        self._summary_stats = 'Summary Statistics:' + \
            '\nCustomers: %d  Sleeping: %d  Cutting: %d  Waiting: %d  Lost Customers: %d  Max Waiting: %d' % \
            (self.barber_total_customers, self.barber_sleeping_time, self.barber_cutting_time,
             self.customers_waiting_time, self.lost_customers, self.max_waiters)

        return self._summary_stats + '\n'
