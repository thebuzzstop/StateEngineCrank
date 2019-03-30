""" StateEngineCrank Console View """

# System imports
from threading import Thread

# 3rd party imports

# Project imports
import mvc
import exceptions


class ConsoleView(mvc.View, Thread):
    """ StateEngineCrank Console View """

    def __init__(self):
        Thread.__init__(self, target=self.run)
        mvc.View.__init__(self)
        self.models = {}

    def update(self):
        pass

    def run(self):
        pass

    def stop(self):
        pass
