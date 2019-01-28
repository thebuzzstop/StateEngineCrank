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
from enum import Enum
import random
from threading import (Lock, Thread)
import time

import logging
from typing import List

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)-8s %(message)s',
                    stream=sys.stdout)
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports
from Barber import UserCode as Barber
from Barber import Events as BarberEvents
from Customer import UserCode as Customer
from Customer import Events as CustomerEvents
from WaitingRoom import WaitingRoom


class Config(object):
    HairCut_Min = 15            # minimum number of seconds to cut hair
    HairCut_Max = 45            # maximum number of seconds to cut hair
    Barbers = 1                 # number of barbers cutting hair
    WaitingChairs = 4           # number of chairs in the waiting room
    CustomerRate = 30           # rate for new customers
    CustomerVariance = 10       # variance in the customer rate
    Customers = 100             # total number of customers


def seconds(minimum, maximum):
    """ Function to return a random integer between 'minimum' and 'maximum'.
        * Used as the number of seconds for a haircut.
        * Used as the number of seconds between new customers.
    """
    return random.randint(minimum, maximum)


class CustomerGenerator(Thread):

    def __init__(self, customer_rate, customer_variance, total_customers):
        Thread.__init__(self, target=self.run)
        self.customer_rate = customer_rate
        self.customer_variance = customer_variance
        self.total_customers = total_customers
        self.customers = []
        self.start()

    def run(self):
        for id in range(self.total_customers):
            logging.debug('CG[%s] new customer' % id)
            self.customers.append(Customer(id=id))
            self.customers[id].running = True
            self.customers[id].event(CustomerEvents.EvStart)
            sleep = seconds(
                self.customer_rate - self.customer_variance,
                self.customer_rate + self.customer_variance
            )
            logging.debug('CG[%s] Zzzz [%s]' % (id, sleep))
            time.sleep(sleep)


if __name__ == '__main__':

    # An array of barbers to cut hair
    barbers = []

    # Initialize the waiting room and the barber(s)
    waiting_room = WaitingRoom(Config.WaitingChairs)
    for id in range(Config.Barbers):
        barbers.append(Barber(id=id))

    # Barber statemachine(s) instantiated
    # Start the simulation, i.e. start all barbers and the customer generator
    for id in range(Config.Barbers):
        barbers[id].running = True
        barbers[id].event(BarberEvents.EvStart)

    # Instantiate the customer generator
    customers = CustomerGenerator(Config.CustomerRate, Config.CustomerVariance, Config.Customers)

    # Wait for the simulation to complete
    #for loop in range(Config.Dining_Loops):
    #    time.sleep(1)
    #    loop += 1
    #    if loop % 10 is 0:
    #        logging.info('Iterations: %s' % loop)

    # Tell the barber(s) to stop
    for id in range(Config.Barbers):
        barbers[id].event(BarberEvents.EvStop)

    # Joining threads
    for id in range(Config.Barbers):
        barbers[id].join()
    logging.info('Barber(s) stopped')

    # Print some statistics of the simulation
    #for id in range(Config.Philosophers):
    #    t = philosophers[id].thinking_seconds
    #    e = philosophers[id].eating_seconds
    #    h = int(philosophers[id].hungry_seconds + 0.5)
    #    total = t + e + h
    #    print('Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (id, t, e, h, total))
