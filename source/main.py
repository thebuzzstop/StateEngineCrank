""" StateEngineCrank Model-View-Controller Main Module

Functions as the Controller for the StateEngineCrank MVC implementation

Provides control for:

* StateEngineCrank execution
* DiningPhilosophers simulation
* SleepingBarber simulation

"""

# System imports
import time

# Project imports
import Defines
import DiningPhilosophers.main as philosophers
import SleepingBarber.main as barbers

# import SleepingBarber.Barber as Barber
# import SleepingBarber.Customer as Customer
# import SleepingBarber.WaitingRoom as WaitingRoom
# import SleepingBarber.Common as BarberCommon

# import view
from console import ConsoleView
from gui import GuiView
from mvc import Model
from mvc import Controller


class Unimplemented(Exception):
    pass


class Main(Controller):
    """ Main code """

    def __init__(self):
        super().__init__('State Engine Main')

        # instantiate models
        self.philosophers = philosophers.DiningPhilosophers()
        self.barbers = barbers.SleepingBarber()
        self.models = {
            'philosophers': self.philosophers,
            'barbers': self.barbers
        }

        # instantiate views
        self.console = ConsoleView()
        self.gui = GuiView()
        self.views = {
            'console': self.console,
            'gui': self.gui
        }

        # register views and models
        self._register_views()
        self._register_models()

        # start our thread of execution
        self.start()

    def _register_views(self):
        """ register views with models """
        for m in self.models.keys():
            for v in self.views.values():
                self.models[m].register(v)

    def _register_models(self):
        """ register models with views """
        for v in self.views.keys():
            for m in self.models.values():
                self.views[v].register(m)

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
            time.sleep(Defines.Times.Waiting)

        # Start views and models
        for v in self.views.keys():
            self.views[v].start()
        for m in self.models.keys():
            self.models[m].start()

        # Start models and views running
        for v in self.views.keys():
            self.views[v].set_running()

        # main loop of execution
        while self.running:
            time.sleep(0.1)

        # Tell all views and models to stop
        self.stopping = True
        for v in self.views.keys():
            self.views[v].stop()
        for m in self.models.keys():
            self.models[m].stop()


if __name__ == '__main__':
    """ Run from the command line """
    main = Main()
    main.running = True
