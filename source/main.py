""" StateEngineCrank Model-View-Controller Main Module

Functions as the Controller for the StateEngineCrank MVC implementation

Provides control for:

* StateEngineCrank execution
* DiningPhilosophers simulation
* SleepingBarber simulation

"""

# System imports
import argparse
import time

# Project imports
import Defines
import DiningPhilosophers.main as philosophers
import DiningPhilosophers.config as dining_config

import SleepingBarber.main as barbers
import SleepingBarber.config as barber_config

# import view
from console import ConsoleView
from gui import GuiView
from mvc import Controller


class Main(Controller):
    """ Main code """

    def __init__(self):
        super().__init__(name='State Engine Main', target=self.run)

        # parse command line arguments
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-v', '--verbosity', help='Increase logging verbosity level', action='store_true')
        self.args = None

        # dictionary of configuration data
        self.configs = {
            'philosophers': dining_config.ConfigData(self.parser, self.args),
            'barbers': barber_config.ConfigData(self.parser, self.args)
        }
        for parse in self.configs.keys():
            self.configs[parse].add_args(self.parser)

        for parse in self.configs.keys():
            self.configs[parse].parse_args(self.parser)

        # dictionary of models
        self.models = {
            'philosophers': philosophers.DiningPhilosophers(exit_when_done=False),
            'barbers': barbers.SleepingBarber(exit_when_done=False)
        }

        # dictionary of views, instantiated
        self.views = {
            'console': ConsoleView(),
            'gui': GuiView()
        }

        # register models with views
        for v in self.views.keys():
            for m in self.models.values():
                self.views[v].register(m)

        # register views with models
        for m in self.models.keys():
            for v in self.views.values():
                self.models[m].register(v)

        # start our thread of execution
        self.start()

    def update(self, event):
        """ Called to initiate an update of all views

            :param event: event to be processed
        """
        for v in self.views.keys():
            self.views[v].update(event)

    def stop(self):
        self.running = False

    def run(self):
        """ Main running procedure """

        # Wait until we are running
        while not self.running:
            time.sleep(Defines.Times.Starting)

        # Start views and models
        for v in self.views.keys():
            self.views[v].thread.start()
        for m in self.models.keys():
            self.models[m].thread.start()

        # Start views running
        # Models are started running from the Views
        for v in self.views.keys():
            self.views[v].set_running()

        # main loop of execution
        while self.running:
            time.sleep(0.1)

        # Tell all views and models to stop
        self.stopping = True
        for v in self.views.keys():
            self.views[v].thread.stop()
        for m in self.models.keys():
            self.models[m].thread.stop()


if __name__ == '__main__':
    """ Run from the command line """
    main = Main()
    main.running = True
