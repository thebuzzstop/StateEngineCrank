# System imports
import random
import threading

# Project imports
from Borg import Borg


class Config(object):
    HairCut_Min = 15        # minimum number of seconds to cut hair
    HairCut_Max = 45        # maximum number of seconds to cut hair
    Barbers = 1             # number of barbers cutting hair
    WaitingChairs = 4       # number of chairs in the waiting room
    CustomerRate = 30       # rate for new customers
    CustomerVariance = 10   # variance in the customer rate
    Customers = 100         # total number of customers
    SimulationLoops = 500   # total number of loops (seconds) to run

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


class Statistics(Borg):
    """ Gather statistics for SleepingBarber simulation """

    def __init__(self):
        Borg.__init__(self)
        self.lock = threading.Lock()
        self.customers = 0
        self.sleeping_time = 0
        self.cutting_time = 0
        self.waiting_time = 0
        self.lost_customers = 0
