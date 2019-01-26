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

logging.debug("Importing modules.PyState")
from modules.PyState import StateMachine
logging.debug("Back from modules.PyState")
logging.debug("Importing Barber")
import Barber
logging.debug("Importing Customer")
import Customer


class Config(object):
    HairCut_Min = 15            # minimum number of seconds to cut hair
    HairCut_Max = 45            # maximum number of seconds to cut hair
    BarberChairs = 1            # number of barbers cutting hair
    WaitingChairs = 4           # number of chairs in the waiting room
    CustomerRate = 30           # rate for new customers
    Simulation_Loops = 10000    # number of loops for simulation


class WaitingRoomStatus(Enum):
    Free = 0
    InUse = 1


def seconds(minimum, maximum):
    """ Function to return a random integer between 'minimum' and 'maximum'.
        Used as the number of seconds to either 'eat' or 'think'.
    """
    return random.randint(minimum, maximum)


if __name__ == '__main__':

    pass
    # Initialize all philosophers
    #for id in range(Config.Philosophers):
    #    philosophers[id] = Philosopher(id=id)

    # Philosophers have been instantiated and threads created
    # Start the simulation, i.e. start all philosophers eating
    #for id in range(Config.Philosophers):
    #    philosophers[id].running = True
    #    philosophers[id].event_code = Events.EvStart

    # Wait for the simulation to complete
    #for loop in range(Config.Dining_Loops):
    #    time.sleep(1)
    #    loop += 1
    #    if loop % 10 is 0:
    #        logging.info('Iterations: %s' % loop)

    # Tell philosophers to stop
    #for id in range(Config.Philosophers):
    #    philosophers[id].event_code = Events.EvStop

    # Joining threads
    #for id in range(Config.Philosophers):
    #    philosophers[id].thread.join()
    #logging.info('All philosophers stopped')

    # Print some statistics of the simulation
    #for id in range(Config.Philosophers):
    #    t = philosophers[id].thinking_seconds
    #    e = philosophers[id].eating_seconds
    #    h = int(philosophers[id].hungry_seconds + 0.5)
    #    total = t + e + h
    #    print('Philosopher %2s thinking: %3s  eating: %3s  hungry: %3s  total: %3s' % (id, t, e, h, total))
