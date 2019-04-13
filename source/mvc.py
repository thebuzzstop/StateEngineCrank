""" StateEngineCrank MVC - Model/View Base Class Module """

# System Imports
from abc import ABC, abstractmethod
import threading

# Project Imports
import Defines
import exceptions


class MVC(ABC, threading.Thread):
    """ Base class definition of an MVC Model, View or Controller """

    class Event(ABC):
        """ MVC Events - Model and View """

        Start = 1       #: Start execution, enter run-state
        Stop = 2        #: Stop execution, terminate program
        Step = 3        #: Single execution step
        Pause = 4       #: Pause execution, retain current state
        Resume = 5      #: Resume execution
        Logger = 6      #: Log entry

        def __init__(self, event, **kwargs):
            """ A Model-View-Controller Event

                An Event contains::

                    * event : the specific event
                    * text : optional text string
                    * data : optional data payload
            """
            self.event = event
            self.text = None
            self.data = None
            if 'text' in kwargs.keys():
                self.text = kwargs['text']
            if 'data' in kwargs.keys():
                self.data = kwargs['data']

    def __init__(self, name=None, target=None):
        threading.Thread.__init__(self, name=name, target=target)
        self.name = name                        #: name of this MVC
        self.starting = True                    #: starting status
        self.running = False                    #: running status
        self.stopping = False                   #: stopping status
        self._stopevent = threading.Event()     #: event used to stop our thread

    def set_running(self):
        """ Accessor to set the *running* flag """
        self.starting = False
        self.running = True

    def set_stopping(self):
        """ Accessor to set the *stopping* flag """
        self.running = False
        self.stopping = True

    @abstractmethod
    def notify(self, event):
        """ Called to send a notification of the occurrence of event
            Events are outbound.

            :param event: Event to be sent to those in registry
        """
        pass

    @abstractmethod
    def update(self, event):
        """ Called to notify us of the occurrence of event
            Events are inbound.

            :param event: Event to be processed
        """
        pass

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


class Logger(object):
    """ Logger class for simplified logging to console """

    def __init__(self, parent):
        self.parent = parent
        if not hasattr(self, 'name'):
            if hasattr(parent, 'name'):
                self.name = parent.name
            else:
                self.name = ''

    def logger(self, text):
        """ Function to support console logging

            :param text: Text to be displayed
        """
        # if there are no views then just print
        if not hasattr(self.parent, 'views'):
            print('logger[%s]: %s' % (self.name, text))

        # parent has views
        elif len(self.parent.views.keys()) > 0:
            for v in self.parent.views.keys():
                if hasattr(self.parent.views[v], 'write'):
                    self.parent.views[v].write(text)
        else:
            # parent has no views
            print('logger[%s]: %s' % (self.name, text))


class Controller(MVC, Logger):
    """ Base class definition of a Controller """

    def __init__(self, name=None, target=None):
        MVC.__init__(self, name=name, target=target)
        Logger.__init__(self, self)
        self.models = {}    #: dictionary of models under our control
        self.views = {}     #: dictionary of views to be updated

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

    def notify(self, event):
        """ Called to send notification of the occurrence of event
            We deliver Model Events to Views.
            We deliver View Events to Models.

            :param event: Event to be sent
        """
        if isinstance(event, Model.Event):
            for v in self.views:
                v.notify(event)
        elif isinstance(event, View.Event):
            for m in self.models:
                m.notify(event)

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class Model(MVC, Logger):
    """ Base class definition of a Model """

    def __init__(self, name=None, target=None):
        MVC.__init__(self, name=name, target=target)
        Logger.__init__(self, self)
        self.views = {}         #: dictionary of views we update

    def register(self, view):
        """ Register a view with us

            :param view: View to be registered
            :raises: InvalidView
        """
        if isinstance(view, View):
            self.views[view.name] = view
        else:
            raise exceptions.InvalidView(view)

    def notify(self, event):
        """ Called by us to notify Views about a Model event

            :param event: Model event to be sent
        """
        for vk in self.views.keys():
            self.views[vk].update(event)

    @abstractmethod
    def update(self, event):
        """ Called by Views to tell us to update

            :param event: View event to be processed
        """
        if not isinstance(event, View.Event):
            raise exceptions.UnknownViewEvent
        pass

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class View(MVC, Logger):
    """ Base class definition of a View """

    def __init__(self, name=None, target=None):
        MVC.__init__(self, name=name, target=target)
        Logger.__init__(self, self)
        self.models = {}        #: our models

    def register(self, model):
        """ Register a model with us

            :param model: Model to be registered
        """
        if isinstance(model, Model):
            self.models[model.name] = model
        else:
            raise exceptions.InvalidModel(model)

    def notify(self, event):
        """ Called by us to notify Models about a View event

            :param event: View event to be sent
        """
        for m in self.models:
            m.update(event)

    @abstractmethod
    def update(self, event):
        """ Called by Models to tell us to update

            :param event: Model event to be processed
        """
        if not isinstance(event, Model.Event):
            raise exceptions.UnknownModelEvent
        pass

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass
