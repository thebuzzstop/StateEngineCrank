# System imports
import random
from threading import Lock as Lock
import time

# Project imports


class Config(object):
    HairCut_Min = 10        # minimum number of seconds to cut hair
    HairCut_Max = 20        # maximum number of seconds to cut hair
    Barbers = 4             # number of barbers cutting hair
    WaitingChairs = 4       # number of chairs in the waiting room
    CustomerRate = 3        # rate for new customers
    CustomerVariance = 2    # variance in the customer rate
    SimulationLoops = 40   # total number of loops (seconds) to run

    @staticmethod
    def seconds(minimum, maximum):
        """ Function to return a random integer between 'minimum' and 'maximum'.
            * Used as the number of seconds for a haircut.
            * Used as the number of seconds between new customers.
        """
        return random.randint(minimum, maximum)

    @staticmethod
    def cutting_time():
        return Config.seconds(Config.HairCut_Min, Config.HairCut_Max)


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same
        state and behavior.

        Taken from "Python Cookbook" by David Ascher, Alex Martelli
        https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s23.html
    """
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Statistics(Borg):
    """ Gather statistics for SleepingBarber simulation """

    def __init__(self):
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            self.lock = Lock()
            self.customers = []
            self.barbers = []
            self.max_waiters = 0
            self.barber_sleeping_time = 0
            self.barber_cutting_time = 0
            self.barber_total_customers = 0
            self.lost_customers = 0
            self.simulation_start_time = time.time()
            self.simulation_finish_time = 0
            self.customers_cutting_time = 0
            self.customers_waiting_time = 0
            self.customers_elapsed_time = 0
            self.customers_simulation_time = 0

    def print_customer_stats(self):
        # Print some customer statistics of the simulation
        for customer in self.customers:
            elapsed_time = customer.finish_time - customer.start_time
            simulation_time = customer.cutting_time + customer.waiting_time
            self.customers_elapsed_time += elapsed_time
            self.customers_simulation_time += simulation_time
            self.customers_cutting_time += customer.cutting_time
            self.customers_waiting_time += customer.waiting_time
            print('customer[%03d] start: %4.2d  finish: %4.2d  elapsed: %3.2d  cutting: %2d  waiting: %2d  simulation: %2d' %
                (customer.customer_id,
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
        # Print some barber statistics of the simulation
        for barber in self.barbers:
            self.barber_sleeping_time += barber.sleeping_time
            self.barber_cutting_time += barber.cutting_time
            self.barber_total_customers += barber.customers
            print('barber[%s] customers: %3d  cutting: %3d  sleeping: %3d' %
                  (barber.id, barber.customers, barber.cutting_time, barber.sleeping_time))

    def print_summary_stats(self):
        print('Customers: %d  Sleeping: %d  Cutting: %d  Waiting: %d  Lost Customers: %d  Max Waiting: %d' %
              (self.barber_total_customers, self.barber_sleeping_time, self.barber_cutting_time,
               self.customers_waiting_time, self.lost_customers, self.max_waiters))
