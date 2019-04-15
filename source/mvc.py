""" StateEngineCrank MVC - Model/View Base Class Module """

# System Imports
from abc import ABC, abstractmethod
import threading
import datetime

# Project Imports
import Defines
import exceptions


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Event(Borg):
    """ MVC Events - Model and View """

    def __init__(self):
        """ A Model-View-Controller Event

            An Event contains::

                * class : the class the event belongs to
                * event : the specific event
                * type : the type of event [model, view, controller]
                * time : timestamp [auto-generated]
                * text : optional text string
                * data : optional data payload
        """
        Borg.__init__(self)
        if len(self._shared_state) is 0:
            self.events = {}
            self.event_counter = 0

            # register some well-known events
            self.register_class('mvc')
            self.register_event('mvc', 'Start', '*', text='Start execution, enter run-state')
            self.register_event('mvc', 'Stop', '*', text='Stop execution, terminate program')
            self.register_event('mvc', 'Step', '*', text='Single execution step')
            self.register_event('mvc', 'Pause', '*', text='Pause execution, retain current state')
            self.register_event('mvc', 'Resume', '*', text='Resume execution')
            self.register_event('mvc', 'Logger', '*', text='Log entry')

    def register_class(self, class_name):
        """ Register a class name for the events database

            :param class_name: Name of event class
            :raises: ClassAlreadyRegistered
        """
        if class_name in self.events.keys():
            raise exceptions.ClassAlreadyRegistered

        # create a dictionary entry for the new class
        self.events[class_name] = {}

    def register_event(self, class_name, event_name, event_type, **kwargs):
        """ Register a class event

            :param class_name: Name of the class this event belongs to
            :param event_name: Name of the event (text)
            :param event_type: Type of event [model, view, controller]
            :param kwargs:
                ['text'] Optional text associated with this event
                ['data'] Optional data associated with this event
            :raises: ClassNotRegistered, EventAlreadyRegistered
        """
        # Set text to user text if present
        text = None
        if 'text' in kwargs.keys():
            text = kwargs['text']
        elif isinstance(event_name, str):
            text = event_name

        # Set data to user data if present
        data = None
        if 'data' in kwargs.keys():
            data = kwargs['data']

        # verify registrations
        if class_name not in self.events.keys():
            raise exceptions.ClassNotRegistered
        if event_name in self.events[class_name].keys():
            raise exceptions.EventAlreadyRegistered

        # register the event in our classes database
        self.event_counter += 1
        self.events[class_name][event_name] = \
            {'class': class_name, 'event': self.event_counter, 'type': event_type, 'text': text, 'data': data}

    def post(self, class_name, event_name, text=None, data=None):
        """ Prepare an event for posting

            :param class_name: Class name for this event, must be registered
            :param event_name: Event name for this event, must be registered
            :param text: Optional text for this event
            :param data: Optional data for this event
            :raises: ClassNotRegistered, EventNotRegistered
        """
        if class_name not in self.events.keys():
            raise exceptions.ClassNotRegistered
        if event_name not in self.events[class_name].keys():
            raise exceptions.EventNotRegistered

        # add event timestamp information
        self.events[class_name][event_name]['datetime'] = datetime.datetime.now()

        # add conditional information
        if text is not None:
            self.events[class_name][event_name]['text'] = text
        if data is not None:
            self.events[class_name][event_name]['data'] = data

        return self.events[class_name][event_name]


class MVC(ABC, threading.Thread):
    """ Base class definition of an MVC Model, View or Controller """

    def __init__(self, name=None, target=None, parent=None):
        threading.Thread.__init__(self, name=name, target=target)
        self.name = name                        #: name of this MVC
        self.starting = True                    #: starting status
        self.running = False                    #: running status
        self.stopping = False                   #: stopping status
        self._stop_event = threading.Event()    #: event used to stop our thread
        if parent is not None:
            self.parent = parent                #: optional parent for notifications

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
        self._stop_event.set()
        threading.Thread.join(self, timeout)


class Logger(object):
    """ Logger class for simplified logging to console """

    def __init__(self, parent):
        self.logger_parent = parent
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
        if not hasattr(self.logger_parent, 'views'):
            print('logger[%s]: %s' % (self.name, text))

        # parent has views
        elif len(self.logger_parent.views.keys()) > 0:
            for v in self.logger_parent.views.keys():
                if hasattr(self.logger_parent.views[v], 'write'):
                    self.logger_parent.views[v].write(text)
        else:
            # parent has no views
            print('logger[%s]: %s' % (self.name, text))


class Controller(MVC, Logger):
    """ Base class definition of a Controller """

    def __init__(self, name=None, target=None, parent=None):
        MVC.__init__(self, name=name, target=target, parent=parent)
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
            We deliver 'model' events to Views.
            We deliver 'view' events to Models.
            We deliver '*' events to Views & Models

            :param event: Event to be sent
        """
        event_type = event['type'].lower()
        if event_type is 'model' or event_type is '*':
            for v in self.views:
                v.update(event)
        if event_type is 'view' or event_type is '*':
            for m in self.models:
                m.update(event)

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class Model(MVC, Logger):
    """ Base class definition of a Model """

    def __init__(self, name=None, target=None, parent=None):
        MVC.__init__(self, name=name, target=target, parent=parent)
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
        pass

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class View(MVC, Logger):
    """ Base class definition of a View """

    def __init__(self, name=None, target=None, parent=None):
        MVC.__init__(self, name=name, target=target, parent=parent)
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
        pass

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass
