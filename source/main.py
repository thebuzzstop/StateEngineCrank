""" StateEngineCrank Model-View-Controller Main Module

Functions as the Controller for the StateEngineCrank MVC implementation

Provides control for:

* StateEngineCrank execution
* DiningPhilosophers simulation
* SleepingBarber simulation

"""

# System imports

# Project imports
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


class Main(Controller):
    """ Main code """

    def __init__(self):
        super().__init__()
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
        self.register_models()
        self.register_views()

    def register_models(self):
        # register models with views
        for v in self.views.keys():
            for m in self.models.keys():
                self.views[v].register({'name': m, 'model': self.models[m]})

    def register_views(self):
        # register views with models
        for m in self.models.keys():
            for v in self.views.keys():
                try:
                    func = self.models[m]
                    func.register({'name': v, 'view': self.views[m]})
                    self.models[m].register({'name': v, 'view': self.views[m]})
                except Exception as e:
                    print(e)

    def update(self):
        """ Called to initiate an update of all views """
        for v in self.views.keys():
            self.views[v].update()

    def run(self):
        for v in self.views.keys():
            self.views[v].run()
        for m in self.models.keys():
            self.models[m].run()


if __name__ == '__main__':
    """ Run from the command line """
    main = Main()
    main.run()
