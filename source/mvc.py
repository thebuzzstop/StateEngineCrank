""" StateEngineCrank MVC - Model/View Base Class Module """

# System Imports
from abc import ABC, abstractmethod
import threading
import datetime
import copy
import enum

# Project Imports
import Defines
import exceptions


class Borg(object):
    """ The Borg class ensures that all instantiations refer to the same state and behavior. """

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


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


class Event(Borg):
    """ MVC Events - Model and View """

    class Events(enum.Enum):
        START, STOP, STEP, PAUSE, RESUME, LOGGER, LOOPS, TIMER, ALLSTOPPED, STATISTICS, UNHANDLED = range(11)

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
            self.events = {}        #: dictionary of events
            self.event_by_id = []   #: list of events, used for lookups by ID
            self.actors = {}        #: dictionary of actors (i.e. posters of events)
            self.event_counter = 0

            # register some well-known events
            self.register_class('mvc')
            self.register_event('mvc', Event.Events.START, '*', text='Start execution, enter run-state')
            self.register_event('mvc', Event.Events.STOP, '*', text='Stop execution, terminate program')
            self.register_event('mvc', Event.Events.STEP, '*', text='Single execution step')
            self.register_event('mvc', Event.Events.PAUSE, '*', text='Pause execution, retain current state')
            self.register_event('mvc', Event.Events.RESUME, '*', text='Resume execution')
            self.register_event('mvc', Event.Events.LOGGER, '*', text='Log entry')
            self.register_event('mvc', Event.Events.LOOPS, '*', text='Loop count', data=0)
            self.register_event('mvc', Event.Events.ALLSTOPPED, '*', text='All processes stopped')
            self.register_event('mvc', Event.Events.STATISTICS, '*', text='Generate statistics')
            self.register_event('mvc', Event.Events.TIMER, '*', text='State timer tick')
            self.register_event('mvc', Event.Events.UNHANDLED, '*', text='Unhandled condition')

    def register_class(self, class_name):
        """ Register a class name for the events database

            :param class_name: Name of event class
            :raises: ClassAlreadyRegistered
        """
        if class_name in self.events.keys():
            raise exceptions.ClassAlreadyRegistered

        # create a dictionary entry for the new class
        self.events[class_name] = {}

    def register_event(self, class_name, event, event_type, **kwargs):
        """ Register a class event

            :param class_name: Name of the class this event belongs to
            :param event: Event class name
            :param event_type: Type of event [model, view, controller]
            :param kwargs:
                ['user.id'] Optional ID associated with this event
                ['text'] Optional text associated with this event
                ['data'] Optional data associated with this event
            :raises: ClassNotRegistered, EventAlreadyRegistered
        """
        # Set UserId to user ID if present
        user_id = None
        if 'user_id' in kwargs.keys():
            user_id = kwargs['user_id']

        # Set text to user text if present
        text = None
        if 'text' in kwargs.keys():
            text = kwargs['text']
        elif isinstance(event, str):
            text = event

        # Set data to user data if present
        data = None
        if 'data' in kwargs.keys():
            data = kwargs['data']

        # verify registrations
        if class_name not in self.events.keys():
            raise exceptions.ClassNotRegistered
        if event in self.events[class_name].keys():
            raise exceptions.EventAlreadyRegistered

        # register the event in our classes database
        self.event_counter += 1
        self.events[class_name][event] = \
            {'class': class_name, 'event': event, 'event.id': self.event_counter, 'type': event_type,
             'user.id': user_id, 'text': text, 'data': data}

        # append the event to our 'event_by_id' lookup table
        self.event_by_id.append(self.events[class_name][event])

    def register_actor(self, class_name, actor_name):
        """ Register an actor for the events database

            Actors are participants that post events in a simulation.
            Actors may register for more than one event class.

            :param class_name: Class of events
            :param actor_name: Name of this actor
        """
        if class_name not in self.events.keys():
            raise exceptions.ClassNotRegistered
        if actor_name in self.actors.keys():
            if class_name in self.actors[actor_name]:
                raise exceptions.ActorAlreadyRegistered
            else:
                # append class to actor class list
                self.actors[actor_name].append(class_name)
        else:
            # create a dictionary entry for the new actor
            self.actors[actor_name] = [class_name]

    def lookup_event(self, class_name, event):
        if class_name not in self.events.keys():
            return None
        if event in self.events[class_name].keys():
            return self.events[class_name][event]
        return None

    def lookup_by_id(self, event_id):
        if 0 < event_id < len(self.event_by_id):
            return self.event_by_id[event_id-1]
        else:
            return None

    def unregister_class(self, class_name):
        """ Unregister a class

            :param class_name: Class to unregister
            :raises: ClassNotRegistered
        """
        # delete the class, it is an error if it is not registered
        if class_name in self.events.keys():
            del self.events[class_name]
        else:
            raise exceptions.ClassNotRegistered

        # delete all actors who were registered for the just deleted class events
        actors = list(self.actors.keys())
        for actor in actors:
            if class_name in actor:
                del self.actors[actor]

    def unregister_actor(self, actor_name):
        """ Unregister an actor

            :param actor_name: Name of actor to unregister
            :raises: ActorNotRegistered
        """
        if actor_name in self.actors.keys():
            del self.actors[actor_name]

    def post(self, class_name, event, actor_name, user_id=None, text=None, data=None):
        """ Prepare an event for posting

            :param class_name: Class name for this event, must be registered
            :param event: Event class name for this event, must be registered
            :param actor_name: Actor name for this event, must be registered
            :param user_id: Optional ID for the poster of this event
            :param text: Optional text for this event
            :param data: Optional data for this event
            :raises: ClassNotRegistered, EventNotRegistered
        """
        if class_name not in self.events.keys():
            raise exceptions.ClassNotRegistered
        if event not in self.events[class_name].keys():
            raise exceptions.EventNotRegistered
        if actor_name not in self.actors.keys():
            raise exceptions.ActorNotRegistered

        # verify actor is registered for this event class
        if class_name not in self.actors[actor_name]:
            raise exceptions.ActorNotRegistered

        # create a copy of the event
        event_ = copy.copy(self.events[class_name][event])
        event_['actor'] = actor_name

        # add event timestamp information
        event_['datetime'] = datetime.datetime.now()

        # add conditional information
        if hasattr(self, 'name'):
            event_['origin'] = self.name
        if text is not None:
            event_['text'] = text
        if data is not None:
            event_['data'] = data
        if user_id is not None:
            event_['user.id'] = user_id
        return event_


class MVC(ABC, threading.Thread):
    """ Base class definition of an MVC Model, View or Controller """

    def __init__(self, name=None, running=False, target=None, parent=None):
        threading.Thread.__init__(self, name=name, target=target)
        self.name = name                        #: name of this MVC
        self.starting = True                    #: starting status
        self.running = running                  #: running status
        self.stopping = False                   #: stopping status
        self.pause = False                      #: pause status
        self.resuming = True                    #: resuming status
        self._step_event = threading.Event()    #: event used to step our thread
        self._stop_event = threading.Event()    #: event used to stop our thread
        if parent is not None:
            self.parent = parent                #: optional parent for notifications

    def set_running(self):
        """ Accessor to set the *running* flag """
        self.starting = False
        self.running = True

    def step(self):
        if self._step_event.is_set():
            self._step_event.clear()
            return True
        else:
            return False

    def set_step(self):
        """ Accessor to set the *step* flag """
        self._step_event.set()

    def clr_step(self):
        """ Accessor to set the *step* flag """
        self._step_event.clear()

    def set_pause(self):
        """ Accessor to set the *pause* flag """
        self.pause = True
        self._step_event.clear()

    def set_resume(self):
        """ Accessor to clear the *pause* flag """
        self.pause = False
        self._step_event.clear()

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
        self.pause = False
        self.clr_step()
        self.join(timeout=Defines.Times.Stopping)
        self.stopping = False

    def join(self, timeout=None):
        """ Called to terminate a thread
            Assumes thread is monitoring the stopevent
        """
        self._stop_event.set()
        threading.Thread.join(self, timeout)

    def prepare(self, event, **kwargs):
        """ Prepare an event for logging and/or notification
            1) Make a shallow copy of this event so we don't modify the original
            2) Add a datetime if one is not present
            3) Add 'text' if present in kwargs
            4) Add 'data' if present in kwargs
        """
        event_ = copy.copy(event)
        if 'datetime' not in event_.keys():
            event_['datetime'] = datetime.datetime.now()
        if 'text' in kwargs.keys() and kwargs['text'] is not None:
            event_['text'] = kwargs['text']
        if 'data' in kwargs.keys() and kwargs['data'] is not None:
            event_['data'] = kwargs['data']
        if 'actor' not in event_.keys() and hasattr(self, 'name'):
            event_['actor'] = self.name
        if 'user.id' not in event_.keys() and hasattr(self, 'id'):
            event_['user.id'] = self.id
        return event_


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

    def notify(self, event, **kwargs):
        """ Called to send notification of the occurrence of event
            We deliver:
                * 'model' events to Views.
                * 'view' events to Models.
                * '*' events to Views & Models

            :param event: Event to be sent
        """
        event_ = self.prepare(event, **kwargs)
        event_type = event_['type'].lower()
        if event_type is 'model' or event_type is '*':
            for v in self.views:
                v.update(event_)
        if event_type is 'view' or event_type is '*':
            for m in self.models:
                m.update(event_)

    @abstractmethod
    def run(self):
        """ Called to initiate running """
        pass


class Model(MVC, Logger):
    """ Base class definition of a Model """

    def __init__(self, name=None, running=False, target=None, parent=None):
        MVC.__init__(self, name=name, running=running, target=target, parent=parent)
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

    def notify(self, event, **kwargs):
        """ Called by us to notify Views about a Model event

            :param event: Model event to be sent
        """
        event_ = self.prepare(event, **kwargs)
        for vk in self.views.keys():
            self.views[vk].update(event_)

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

    def notify(self, event, **kwargs):
        """ Called by us to notify Models about a View event

            :param event: View event to be sent
        """
        event_ = self.prepare(event, **kwargs)
        for mk in self.models.keys():
            self.models[mk].update(event_)

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