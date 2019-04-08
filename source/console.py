""" StateEngineCrank Console View """

# System imports
import datetime
import time
import queue

# Project imports
import mvc
import Defines


class ConsoleView(mvc.View, queue.Queue):
    """ StateEngineCrank Console View """

    def __init__(self):
        mvc.View.__init__(self, 'console')
        queue.Queue.__init__(self)

    def update(self, event):
        """ ConsoleView is a simple logger, we do nothing for an update

            :param event: An event to be processed
        """
        pass

    def write(self, text):
        self.put_nowait('%s %s' % (str.split('%s' % datetime.datetime.now(), ' ')[1], text))

    def run(self):
        """ Console view running """
        # wait until we are running
        while not self.running:
            time.sleep(Defines.Times.Waiting)
        # loop until no longer running
        while self.running and not self._stopevent.isSet():
            time.sleep(Defines.Times.Running)
            while not self.empty():
                print(self.get_nowait())
