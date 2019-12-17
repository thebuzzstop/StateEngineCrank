""" SleepingBarber.CustomerGen

The Customer Generator Module supplies customers to the Sleeping Barber Simulation.

Customers are generated:

* At a specified rate (e.g. 5 customers per unit of time)
* With a randomization provided at the start of the simulation.

This provides a random nature to the arrival of customers to the barber shop.
"""

# System imports
import time
from queue import Queue
from threading import Thread

# Project imports
import mvc
import Defines
from SleepingBarber.Common import Config as Config
from SleepingBarber.Common import ConfigData as ConfigData
from SleepingBarber.Customer import UserCode as Customer


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


class CustomerGenerator(mvc.Model):
    """ Class for generating customers based on configurable criteria. """

    def cleanup(self):
        """ Cleanup threads and registrations """

        # Cleanup registrations
        for c in self.customer_list:
            c.sm_events.events.unregister_actor(c.name)
        self.mvc_events.unregister_class(self.config.customer_class_name)

        # Join threads
        self.pool.wait_completion()

    def __init__(self, customer_rate, customer_variance, barbers):
        """ CustomerGenerator Class Constructor

            :param customer_rate: rate at which customers will be generated
            :param customer_variance: used to introduce variation in customer rate
            :param barbers: list of barbers cutting hair
        """
        super().__init__('CG', target=self.run)
        self.customer_rate = customer_rate          #: rate at which customers will be generated
        self.customer_variance = customer_variance  #: variance in rate, used by random number generator
        self.customer_count = 0                     #: total customers
        self.customer_list = []                     #: list of customer objects
        self.barbers = barbers                      #: list of barbers cutting hair
        self.config = ConfigData()                  #: simulation configuration data
        self.mvc_events = mvc.Event()               #: for event registration
        self.mvc_events.register_class(self.config.customer_class_name)

        #: maximum number of customers active simultaneously
        self.customer_max = self.config.waiting_chairs + self.config.barbers_max + 1
        self.pool = ThreadPool(self.customer_max)   #: a thread pool for customers

    def update(self, event):
        pass

    def run(self):
        """ Customer generator main thread

            The customer generator thread runs in the background creating customers for the simulation.
        """
        # loop until we are told we are done
        self.logger('run.wait')
        # wait until the simulation is running
        while not self.running:
            time.sleep(Defines.Times.Starting)
        self.logger('running')

        # run until the simulation is stopped or we are done
        while self.running:
            # generate a new customer
            self.customer_count += 1
            self.logger(f'New customer [{self.customer_count}]')
            next_customer = Customer(id_=self.customer_count, barbers=self.barbers)
            self.pool.add_task(next_customer.run)
            for v in self.views:
                next_customer.register(self.views[v])

            next_customer.running = True
            self.customer_list.append(next_customer)

            # delay between generating new customers
            sleep = Config.seconds(
                self.customer_rate - self.customer_variance,
                self.customer_rate + self.customer_variance
            )
            self.logger(f'[{self.customer_count}] Zzzz [{sleep}]')
            time.sleep(sleep)

            # pause if requested, keep monitoring the running flag
            while self.pause and self.running:
                time.sleep(Defines.Times.Pausing)

        self.logger('Done')
