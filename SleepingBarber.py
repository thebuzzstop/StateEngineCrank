#!/usr/bin/env python
"""
Created on January 25, 2019

@author:    Mark Sawyer
@date:      25-Jan-2019

@package:   SleepingBarber(s)
@brief:     Top level code for SleepingBarber(s) simulation
@details:   Main driver, instantiates Barber(s) and Customer(s) and drives the state machines

@copyright: Mark B Sawyer, All Rights Reserved 2019
"""

# System imports
import sys
from threading import Thread
import time
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports
from Common import Config as Config             # noqa
from Barber import UserCode as Barber           # noqa
from Barber import Events as BarberEvents       # noqa
from Customer import UserCode as Customer       # noqa
from Customer import Events as CustomerEvents   # noqa
from WaitingRoom import WaitingRoom             # noqa

# An array of barbers to cut hair
barbers = [Barber(barber_id=_) for _ in range(Config.Barbers)]

# Instantiate the waiting room
waiting_room = WaitingRoom(chairs=Config.WaitingChairs)


class CustomerGenerator(Thread):

    def __init__(self, customer_rate, customer_variance):
        Thread.__init__(self, target=self.run)
        self.customer_rate = customer_rate
        self.customer_variance = customer_variance
        self.customer_count = 0
        self.customer_list = []
        self.running = False
        logging.debug('CG: Start')
        self.start()

    def run(self):
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
            next_customer = Customer(customer_id=self.customer_count, barbers=barbers)
            next_customer.running = True
            next_customer.event(CustomerEvents.EvStart)
            self.customer_list.append(next_customer)

            # alert barber(s) to new customer
            for cg_barber in barbers:
                cg_barber.event(BarberEvents.EvCustomerEnter)

            # delay between generating new customers
            sleep = Config.seconds(
                self.customer_rate - self.customer_variance,
                self.customer_rate + self.customer_variance
            )
            logging.debug('CG[%s] Zzzz [%s]' % (self.customer_count, sleep))
            time.sleep(sleep)


if __name__ == '__main__':

    # Instantiate the customer generator
    customers = CustomerGenerator(Config.CustomerRate, Config.CustomerVariance)

    # Start the simulation, i.e. start all barbers and the customer generator
    for barber in barbers:
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
    for barber in barbers:
        barber.event(BarberEvents.EvStop)

    # Tell any waiting customers to stop
    for customer in customers.customer_list:
        customer.event(CustomerEvents.EvStop)

    # Joining threads
    logging.debug('Customers: Join')
    customers.join()
    logging.debug('Customers: Joined')

    for barber in barbers:
        logging.debug('Barber[%s] Join' % barber.id)
        barber.join()
        logging.debug('Barber[%s] Joined' % barber.id)

    logging.info('Barber(s) all stopped')

    # Print some statistics of the simulation
    # for id in range(Config.Philosophers):
    #     t = philosophers[id].thinking_seconds
    #     e = philosophers[id].eating_seconds
    #     h = int(philosophers[id].hungry_seconds + 0.5)
    #     total = t + e + h
    #     print('Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (id, t, e, h, total))
