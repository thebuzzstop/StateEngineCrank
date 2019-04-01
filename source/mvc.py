""" StateEngineCrank MVC - Model/View Base Class Module """

# System Imports
from abc import ABC, abstractmethod
import threading

# Project Imports
import Defines
import exceptions


class MVC(ABC, threading.Thread):
    """ Base class definition of an MVC Model, View or Controller """

    def __init__(self, name):
        threading.Thread.__init__(self, name=name)
        self.name = name                    #: name of this MVC
        self.starting = True                #: starting status
        self.running = False                #: running status
        self.stopping = False               #: stopping status
        self._stopevent = threading.Event() #: event used to stop our thread

    def set_running(self):
        """ Accessor to set the *running* flag """
        self.starting = False
        self.running = True

    def set_stopping(self):
        """ Accessor to set the *stopping* flag """
        self.running = False
        self.stopping = True

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass

    def stop(self):
        """ Initiate stopping """
        self.stopping = True
        self.running = False
        self.join(timeout=Defines.Times.Stopping)
        self.stopping = False

    def join(self, timeout=None):
        """ Called to terminate a thread
            Assumes thread is monitoring the stopevent
        """
        self._stopevent.set()
        threading.Thread.join(self, timeout)


class Controller(MVC):
    """ Base class definition of a Controller """

    def __init__(self, name):
        super().__init__(name)
        self.models = {}    #: dictionary of models under our control
        self.views = {}     #: dictionary of views to be updated

    def update_views(self):
        """ Called by models or view to initiate an update """
        for v in self.views:
            v.update()

    def register(self, mv):
        """ Called to register a model or view with the controller

            :param mv: model/view to be registered
            :raises: InvalidMVC
        """
        if isinstance(mv, View):
            self.views[mv.name] = mv
        if isinstance(mv, Model):
            self.models[mv.name] = mv
        else:
            raise exceptions.InvalidMVC

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class Model(MVC):
    """ Base class definition of a Model """

    def __init__(self, name):
        super().__init__(name)
        self.views = {}         #: dictionary of views we update

    @abstractmethod
    def register(self, view):
        """ Register a view with us

            :param view: View to be registered
            :raises: InvalidView
        """
        if isinstance(view, View):
            self.views[view.name] = view
        else:
            raise exceptions.InvalidView(view)

    def update(self):
        """ Called by view or controller to initiate an update """
        for v in self.views:
            v.update()

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class View(MVC):
    """ Base class definition of a View """

    def __init__(self, name):
        super().__init__(name)
        self.models = {}        #: our models

    @abstractmethod
    def register(self, model):
        """ Register a model with us

            :param model: Model to be registered
        """
        if isinstance(model, Model):
            self.models[model.name] = model
        else:
            raise exceptions.InvalidModel(model)

    @abstractmethod
    def update(self):
        """ Called by models or controller to initiate an update """
        pass

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass
