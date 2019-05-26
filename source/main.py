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
from mvc import Controller


class Unimplemented(Exception):
    pass


class Main(Controller):
    """ Main code """

    def __init__(self):
        super().__init__(name='State Engine Main', target=self.run)

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

        # register models and views
        self._register_models()
        self._register_views()

        # start our thread of execution
        self.thread.start()

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
