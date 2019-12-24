""" Sleeping Barber(s) Configuration """

# System imports
import argparse
import random
import logging

# Project imports
import source.config as cfg


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Config(object):
    """ SleepingBarber configuration items """

    HairCut_Min = 20                    #: minimum number of seconds to cut hair
    HairCut_Max = 30                    #: maximum number of seconds to cut hair
    Barbers = 4                         #: number of barbers cutting hair
    BarbersMax = 5                      #: maximum number of barbers for animation
    WaitingChairs = 4                   #: number of chairs in the waiting room
    WaitingChairsMax = 5                #: maximum number of waiters for animation
    CustomerRate = 5                    #: rate for new customers
    CustomerVariance = 2                #: variance in the customer rate
    SimulationLoops = 100               #: total number of loops (seconds) to run
    Class_Name = 'Barbers'              #: class name for Event registration
    Actor_Base_Name = 'Barber'          #: used when identifying actors
    Customer_Class_Name = 'Customers'   #: class name for Event registration
    Customer_Base_Name = 'Customer'     #: used when identifying actors
    verbosity = logging.INFO            #: default level for logging


class ConfigData(cfg.ConfigData, Borg):
    """ Sleeping Barber Configuration Data """

    def __init__(self, parser=None, args=None):
        Borg.__init__(self)
        if self._shared_state:
            return
        cfg.ConfigData.__init__(self, parser=parser)
        self.haircut_min = Config.HairCut_Min
        self.haircut_max = Config.HairCut_Max
        self.barbers = Config.Barbers
        self.barbers_max = Config.BarbersMax
        self.waiting_chairs = Config.WaitingChairs
        self.waiting_chairs_max = Config.WaitingChairsMax
        self.customer_rate = Config.CustomerRate
        self.customer_variance = Config.CustomerVariance
        self.simulation_loops = Config.SimulationLoops
        self.class_name = Config.Class_Name
        self.actor_base_name = Config.Actor_Base_Name
        self.customer_class_name = Config.Customer_Class_Name
        self.customer_actor_base_name = Config.Customer_Base_Name
        self.verbosity = logging.INFO

        # remember parser/args if given
        if parser:
            self.parser = parser
            self.args = args
        else:
            self.parser = argparse.ArgumentParser()
            self.add_args(self.parser)
            self.parse_args(self.parser)
        pass

    def add_args(self, parser=None):
        """ Add parser arguments

            :param parser: Parser to add arguments to [optional]
        """
        if parser:
            self.parser = parser
        self.parser.add_argument('-v', '--verbosity', help='Increase logging verbosity', action='count')
        self.parser.add_argument('-l', '--simulation_loops', type=int, help='Number of simulation loops')
        self.parser.add_argument('-b', '--barbers', type=int, help='Number of barbers in simulation')
        self.parser.add_argument('-min', '--haircut_min', type=int, help='Minimum haircut time (seconds)')
        self.parser.add_argument('-max', '--haircut_max', type=int, help='Maximum haircut time (seconds)')
        self.parser.add_argument('-c', '--waiting_chairs', type=int, help='Number of chairs in waiting room')
        self.parser.add_argument('-r', '--customer_rate', type=int, help='Customer generator rate (seconds)')
        self.parser.add_argument('-var', '--customer_variance', type=int, help='Customer generation variance (seconds)')
        pass

    def parse_args(self, parser=None):
        """ Parse command line arguments

            :param parser: Parser to use for parsing
        """
        if parser:
            self.parser = parser
        self.args = self.parser.parse_args()
        if self.args.verbosity:
            raise Exception('Verbosity switch not presently supported')
        if self.args.simulation_loops:
            self.simulation_loops = self.args.simulation_loops
        if self.args.barbers:
            self.barbers = self.args.barbers
        if self.args.haircut_min:
            self.haircut_min = self.args.haircut_min
        if self.args.haircut_max:
            self.haircut_max = self.args.haircut_max
        if self.args.waiting_chairs:
            self.waiting_chairs = self.args.waiting_chairs
        if self.args.customer_rate:
            self.customer_rate = self.args.customer_rate
        if self.args.customer_variance:
            self.customer_variance = self.args.customre_variance
        pass

    @staticmethod
    def seconds(minimum, maximum):
        """ Function to return a random integer between 'minimum' and 'maximum'.

            * Used as the number of seconds for a haircut.
            * Used as the number of seconds between new customers.

            :param minimum: range minimum value
            :param maximum: range maximum value
            :returns: Random number between minimum and maximum
        """
        return random.randint(minimum, maximum)

    @staticmethod
    def cutting_time():
        """ Utility function to return a random time between minimum and maximum
            time specified in the configuration class

            :returns: Random cutting time
        """
        return ConfigData.seconds(Config.HairCut_Min, Config.HairCut_Max)

    def get_barbers(self):
        return self.barbers

    def get_barbers_max(self):
        return self.barbers_max

    def get_waiters(self):
        return self.waiting_chairs

    def get_waiters_max(self):
        return self.waiting_chairs_max
