""" StateEngineCrank MVC - Model/View Base Class Module """

# System Imports
from abc import ABC, abstractmethod

# Project Imports
import exceptions


class Controller(ABC):
    """ Base class definition of a Controller """

    def __init__(self):
        self.models = {}    #: dictionary of models under our control
        self.views = {}     #: list of views to be updated

    def update_views(self):
        """ Called by models or view to initiate an update """
        for v in self.views:
            v.update()

    @abstractmethod
    def register_views(self):
        """ Called to register views with models """
        pass

    @abstractmethod
    def register_models(self):
        """ Called to register models with views """
        pass

    @abstractmethod
    def run(self):
        """ Called to initiate running of models and views """
        pass


class Model(ABC):
    """ Base class definition of a Model """

    def __init__(self):
        self.views = {}         #: dictionary of views we update

    def register(self, view):
        """ Register a view with us

            :param view: View to be registered
        """
        if isinstance(view, dict):
            self.views['name'] = view['view']
        else:
            raise exceptions.InvalidModel

    def update(self):
        """ Called by view or controller to initiate an update """
        for v in self.views:
            v.update()

    @abstractmethod
    def run(self):
        pass


class View(ABC):
    """ Base class definition of a View """

    def __init__(self):
        self.models = {}                #: our models

    def register(self, model):
        """ Register a model with us

            :param model: Model to be registered
        """
        if isinstance(model, dict):
            self.models['name'] = model['model']
        else:
            raise exceptions.InvalidModel

    @abstractmethod
    def run(self):
        """ Called by controller to initiate running """
        pass

    @abstractmethod
    def stop(self):
        """ Called by controller to stop running """
        pass

    @abstractmethod
    def update(self):
        """ Called by models or controller to initiate an update """
        pass
