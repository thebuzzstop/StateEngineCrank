""" StateEngineCrank MVC - View Module """

# System Imports
from abc import ABC, abstractmethod

# 3rd Party Imports

# Project Imports


class View(ABC):
    """ Base class definition of a View """

    def __init__(self):
        self.model = None   #: our model

    def register(self, model):
        """ Register a model with us

            :param model: Model to be registered
        """
        self.model = model

    @abstractmethod
    def update(self):
        """ Called by either model or controller to initiate a view update """
        pass
