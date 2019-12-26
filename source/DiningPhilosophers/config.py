""" Dining Philosophers Configuration """

# System imports
import argparse
import logging

# Project imports
import source.config as cfg


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Config(object):
    """ Dining Philosophers configuration items """

    Eat_Min = 5                         #: minimum number of seconds to eat
    Eat_Max = 10                        #: maximum number of seconds to eat
    Think_Min = 5                       #: minimum number of seconds to think
    Think_Max = 10                      #: maximum number of seconds to think
    Philosophers = 7                    #: number of philosophers dining
    Dining_Loops = 100                  #: number of main loops for dining
    Class_Name = 'philosophers'         #: class name for Event registration
    Actor_Base_Name = 'philosopher'     #: used when identifying actors
    verbosity = logging.INFO            #: default level for logging


class ConfigData(cfg.ConfigData, Borg):

    def __init__(self, parser=None, args=None):
        Borg.__init__(self)
        if self._shared_state:
            return
        cfg.ConfigData.__init__(self, parser=parser)
        self.logger = logging.getLogger(__name__)
        self.eat_max = Config.Eat_Max
        self.eat_min = Config.Eat_Min
        self.think_min = Config.Think_Min
        self.think_max = Config.Think_Max
        self.philosophers = Config.Philosophers
        self.dining_loops = Config.Dining_Loops
        self.class_name = Config.Class_Name
        self.actor_base_name = Config.Actor_Base_Name

        # instantiate a parser if not present
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
        try:
            self.parser.add_argument('-v', '--verbosity', help='Increase logging verbosity', action='store_true')
        except argparse.ArgumentError:
            pass
        self.parser.add_argument('--dining_loops', type=int, help='Number of dining simulation loops')
        self.parser.add_argument('--philosophers', type=int, help='Number of dining philosophers')
        self.parser.add_argument('--eat_min', type=int, help='Minimum seconds to eat')
        self.parser.add_argument('--eat_max', type=int, help='Maximum seconds to eat')
        self.parser.add_argument('--think_min', type=int, help='Minimum seconds to think')
        self.parser.add_argument('--think_max', type=int, help='Maximum seconds to think')

    def parse_args(self, parser=None):
        """ Parse command line arguments

            :param parser: Parser to use for parsing
        """
        if parser:
            self.parser = parser
        self.args = self.parser.parse_args()
        if self.args.verbosity:
            raise Exception('Verbosity switch not presently supported')
        if self.args.dining_loops:
            self.dining_loops = self.args.dining_loops
        if self.args.philosophers:
            self.philosophers = self.args.philosophers
        if self.args.eat_min:
            self.eat_min = self.args.eat_min
        if self.args.eat_max:
            self.eat_max = self.args.eat_max
        if self.args.think_min:
            self.think_min = self.args.think_min
        if self.args.think_max:
            self.think_max = self.args.think_max

    def set_eat_max(self, value):
        self.eat_max = value

    def set_eat_min(self, value):
        self.eat_min = value

    def set_think_max(self, value):
        self.think_max = value

    def set_think_min(self, value):
        self.think_min = value

    def set_philosophers(self, value):
        self.philosophers = value

    def set_dining_loops(self, value):
        self.dining_loops = value

    def get_philosophers(self):
        return self.philosophers
