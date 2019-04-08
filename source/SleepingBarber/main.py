""" SleepingBarber.main

* Top level code for SleepingBarber(s) simulation.
* Main driver, instantiates Barber(s) and Customer(s) and drives the state machines
"""

# System imports
import time

# Project imports
from mvc import Model
from Common import Config as Config
from Common import Statistics as Statistics
from Barber import UserCode as Barber
from Barber import Events as BarberEvents
from Customer import UserCode as Customer
from Customer import Events as CustomerEvents
from WaitingRoom import WaitingRoom


class CustomerGenerator(Model):
    """ Class for generating customers based on configurable criteria. """

    def __init__(self, customer_rate, customer_variance, barbers):
        """ Constructor

            :param customer_rate: rate at which customers will be generated
            :param customer_variance: used to introduce variation in customer rate
            :param barbers: list of barbers cutting hair
        """
        super().__init__('CG')
        self.customer_rate = customer_rate          #: rate at which customers will be generated
        self.customer_variance = customer_variance  #: variance in rate, used by random number generator
        self.customer_count = 0                     #: total customers
        self.customer_list = []                     #: list of customer objects
        self.barbers = barbers                      #: list of barbers cutting hair

    def update(self, event):
        pass

    def run(self):
        """ Customer generator main thread

            The customer generator thread runs in the background creating customers for the simulation.
        """
        self.logger('run.wait')
        # wait until the simulation is running
        while not self.running:
            time.sleep(0.100)
        self.logger('running')

        # run until the simulation is stopped
        while self.running:
            # generate a new customer
            self.customer_count += 1
            self.logger('[%s] new customer' % self.customer_count)
            next_customer = Customer(id_=self.customer_count, barbers=self.barbers)
            for v in self.views:
                next_customer.register(self.views[v])
            next_customer.running = True
            self.customer_list.append(next_customer)

            # delay between generating new customers
            sleep = Config.seconds(
                self.customer_rate - self.customer_variance,
                self.customer_rate + self.customer_variance
            )
            self.logger('[%s] Zzzz [%s]' % (self.customer_count, sleep))
            time.sleep(sleep)
        self.logger('Done')


class SleepingBarber(Model):
    """ Main SleepingBarber(s) Class """

    def __init__(self):
        super().__init__('barbers')

        #: An array of barbers to cut hair
        self.barbers = [Barber(id_=_ + 1) for _ in range(Config.Barbers)]

        #: Instantiate the customer generator
        self.cg = CustomerGenerator(Config.CustomerRate, Config.CustomerVariance, self.barbers)

        #: Instantiate the waiting room
        self.waiting_room = WaitingRoom(chairs=Config.WaitingChairs)

        #: Instantiate the statistics module
        self.statistics = Statistics()

    def register(self, view):
        self.views[view.name] = view
        for b in self.barbers:
            b.register(view)
        self.cg.register(view)

    def update(self, event):
        """ Called by view to alert us to a change - we ignore for now """
        pass

    def stop(self):
        raise Exception

    def run(self):
        """ SleepingBarber Main Program

            Implemented as a function so as to be callable from an outside
            entity when running in concert with other applications.

            Also runnable as a standalone application.
        """

        # Wait for simulation to be running
        while not self.running:
            time.sleep(1)

        # Start the simulation, i.e. start all barbers and the customer generator
        for barber in self.barbers:
            barber.running = True
            barber.event(BarberEvents.EvStart)

        # Start the customer generator
        self.cg.start()
        self.cg.running = True

        # Wait for the simulation to complete
        for loop in range(Config.SimulationLoops):
            time.sleep(1)
            loop += 1
            if loop % 10 is 0:
                self.logger('Iterations: %s' % loop)

        # Stop the customer generator
        self.cg.running = False

        # Tell the barber(s) to stop
        for barber in self.barbers:
            barber.event(BarberEvents.EvStop)

        # Tell any waiting customers to stop
        for customer in self.cg.customer_list:
            customer.event(CustomerEvents.EvStop)

        # Joining threads
        self.logger('Main: Joining customers')
        for customer in self.cg.customer_list:
            customer.join()
        self.logger('Main: Customers joined')

        self.logger('CG: Join')
        self.cg.join()
        self.logger('CG: Joined')

        for barber in self.barbers:
            self.logger('Barber[%s] Join' % barber.id)
            barber.join()
            self.logger('Barber[%s] Joined' % barber.id)

        self.logger('Barber(s) all stopped')

        # print statistics
        self.logger(self.statistics.barber_stats())
        self.logger(self.statistics.customer_stats())
        self.logger(self.statistics.summary_stats())


if __name__ == '__main__':
    """ Execute main code if run from the command line """

    sleeping_barbers = SleepingBarber()
    sleeping_barbers.set_running()
