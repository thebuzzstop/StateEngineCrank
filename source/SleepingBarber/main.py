""" SleepingBarber.main

* Top level code for SleepingBarber(s) simulation.
* Main driver, instantiates Barber(s) and Customer(s) and drives the state machines
"""

# System imports
import sys
from threading import Thread
import time
import logging

# Project imports
from mvc import Model                           # noqa
from Common import Config as Config             # noqa
from Common import Statistics as Statistics     # noqa
from Barber import UserCode as Barber           # noqa
from Barber import Events as BarberEvents       # noqa
from Customer import UserCode as Customer       # noqa
from Customer import Events as CustomerEvents   # noqa
from WaitingRoom import WaitingRoom             # noqa

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))


class CustomerGenerator(Thread):
    """ Class for generating customers based on configurable criteria. """

    def __init__(self, customer_rate, customer_variance, barbers):
        """ Constructor

            :param customer_rate: rate at which customers will be generated
            :param customer_variance: used to introduce variation in customer rate
            :param barbers: list of barbers cutting hair
        """
        Thread.__init__(self, target=self.run)
        self.customer_rate = customer_rate          #: rate at which customers will be generated
        self.customer_variance = customer_variance  #: variance in rate, used by random number generator
        self.customer_count = 0                     #: total customers
        self.customer_list = []                     #: list of customer objects
        self.running = False                        #: boolean determining when we are supposed to run
        self.barbers = barbers                      #: list of barbers cutting hair
        logging.debug('CG: Start')
        self.start()

    def run(self):
        """ Customer generator main thread

            The customer generator thread runs in the background creating customers for the simulation.
        """
        logging.debug('CG: run.wait')
        # wait until the simulation is running
        while not self.running:
            time.sleep(0.100)
        logging.debug('CG: running')

        # run until the simulation is stopped
        while self.running:
            # generate a new customer
            self.customer_count += 1
            logging.debug('CG[%s] new customer' % self.customer_count)
            next_customer = Customer(id=self.customer_count, barbers=self.barbers)
            next_customer.running = True
            self.customer_list.append(next_customer)

            # delay between generating new customers
            sleep = Config.seconds(
                self.customer_rate - self.customer_variance,
                self.customer_rate + self.customer_variance
            )
            logging.debug('CG[%s] Zzzz [%s]' % (self.customer_count, sleep))
            time.sleep(sleep)
        logging.debug('CG Done')


class SleepingBarber(Model):
    """ Main SleepingBarber(s) Class """

    def __init__(self):
        super().__init__('barbers')

        #: An array of barbers to cut hair
        self.barbers = [Barber(id=_ + 1) for _ in range(Config.Barbers)]

        #: Instantiate the waiting room
        self.waiting_room = WaitingRoom(chairs=Config.WaitingChairs)

        #: Instantiate the statistics module
        self.statistics = Statistics()

    def register(self, view):
        for b in self.barbers:
            b.register(view)

    def stop(self):
        raise Exception

    def run(self):
        """ SleepingBarber Main Program

            Implemented as a function so as to be callable from an outside
            entity when running in concert with other applications.

            Also runnable as a standalone application.
        """

        # Instantiate the customer generator
        customers = CustomerGenerator(Config.CustomerRate, Config.CustomerVariance, self.barbers)

        # Start the simulation, i.e. start all barbers and the customer generator
        for barber in self.barbers:
            barber.running = True
            barber.event(BarberEvents.EvStart)

        # Start the customer generator
        customers.running = True

        # Wait for the simulation to complete
        for loop in range(Config.SimulationLoops):
            time.sleep(1)
            loop += 1
            if loop % 10 is 0:
                logging.info('Iterations: %s' % loop)

        # Stop the customer generator
        customers.running = False

        # Tell the barber(s) to stop
        for barber in self.barbers:
            barber.event(BarberEvents.EvStop)

        # Tell any waiting customers to stop
        for customer in customers.customer_list:
            customer.event(CustomerEvents.EvStop)

        # Joining threads
        logging.debug('Main: Joining customers')
        for customer in customers.customer_list:
            customer.join()
        logging.debug('Main: Customers joined')

        logging.debug('CG: Join')
        customers.join()
        logging.debug('CG: Joined')

        for barber in self.barbers:
            logging.debug('Barber[%s] Join' % barber.id)
            barber.join()
            logging.debug('Barber[%s] Joined' % barber.id)

        logging.info('Barber(s) all stopped')

        # print statistics
        self.statistics.print_barber_stats()
        self.statistics.print_customer_stats()
        self.statistics.print_summary_stats()


if __name__ == '__main__':
    """ Execute main code if run from the command line """

    sleeping_barbers = SleepingBarber()
    sleeping_barbers.set_running()
