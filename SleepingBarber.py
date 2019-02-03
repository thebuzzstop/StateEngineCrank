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
            self.customer_count += 1
            logging.debug('CG[%s] new customer' % self.customer_count)
            self.customer_list.append(Customer(customer_id=self.customer_count))
            self.customer_list[self.customer_count].running = True
            self.customer_list[self.customer_count].event(CustomerEvents.EvStart)
            sleep = Config.seconds(
                self.customer_rate - self.customer_variance,
                self.customer_rate + self.customer_variance
            )
            logging.debug('CG[%s] Zzzz [%s]' % (self.customer_count, sleep))
            time.sleep(sleep)


if __name__ == '__main__':

    # An array of barbers to cut hair
    barbers = []

    # Instantiate the waiting room and the barber(s)
    waiting_room = WaitingRoom(Config.WaitingChairs)
    for barber_id in range(Config.Barbers):
        barbers.append(Barber(barber_id=barber_id))

    # Instantiate the customer generator
    customers = CustomerGenerator(Config.CustomerRate, Config.CustomerVariance, Config.Customers)

    # Start the simulation, i.e. start all barbers and the customer generator
    for barber_id in range(Config.Barbers):
        barbers[barber_id].running = True
        barbers[barber_id].event(BarberEvents.EvStart)

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
    for id_ in range(Config.Barbers):
        barbers[id_].event(BarberEvents.EvStop)

    # Tell any waiting customers to stop
    for customer in customers.customer_list:
        customer.event(CustomerEvents.EvStop)

    # Joining threads
    customers.join()
    for id_ in range(Config.Barbers):
        barbers[id_].join()
    logging.info('Barber(s) stopped')

    # Print some statistics of the simulation
    # for id in range(Config.Philosophers):
    #     t = philosophers[id].thinking_seconds
    #     e = philosophers[id].eating_seconds
    #     h = int(philosophers[id].hungry_seconds + 0.5)
    #     total = t + e + h
    #     print('Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (id, t, e, h, total))
