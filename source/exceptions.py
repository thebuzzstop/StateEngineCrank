""" Model-View-Controller (MVC) Exceptions """

import inspect


class MyException(Exception):
    """ Base exception class """

    def __init__(self, text=None):
        stack = inspect.stack()[1][0]
        caller = inspect.getframeinfo(stack)
        filename = caller.filename
        func = caller.function
        line = caller.lineno
        msg = 'Filename: {0}\nLine: {1} Function: {2}'.format(filename, line, func)
        if text is not None:
            msg = '[Error] {0}\n{1}'.format(text, msg)


class InvalidThread(MyException):
    """ Thread operation on invalid thread object """
    pass


class InvalidMVC(MyException):
    """ Invalid model/view/controller passed """
    pass


class InvalidModel(MyException):
    """ Invalid model passed """

    def __init__(self, model):
        super().__init__(f'Invalid model: {model}')


class InvalidView(MyException):
    """ Invalid view passed """

    def __init__(self, view):
        super().__init__(f'Invalid view: {view}')


class UnknownModelEvent(MyException):
    """ Invalid/Unknown model event received """

    def __init__(self, event):
        super().__init__(f'Unknown model event: {event}')


class UnknownViewEvent(MyException):
    """ Invalid/Unknown view event received """

    def __init__(self, event):
        super().__init__(f'Unknown view event: {event}')


class ClassAlreadyRegistered(MyException):
    """ Class name is already registered """

    def __init__(self, classname):
        super().__init__(f'Class name already registered: {classname}')


class EventAlreadyRegistered(MyException):
    """ Event name is already registered """

    def __init__(self, event):
        super().__init__(f'Event already registered: {event}')


class ActorAlreadyRegistered(MyException):
    """ Event actor is already registered """

    def __init__(self, actor):
        super().__init__(f'Actor already registered: {actor}')


class ClassNotRegistered(MyException):
    """ Class name is not registered """

    def __init__(self, classname):
        super().__init__(f'Class not registered: {classname}')


class EventNotRegistered(MyException):
    """ Event name is not registered """

    def __init__(self, event):
        super().__init__(f'Event not registered: {event}')


class ActorNotRegistered(MyException):
    """ Event actor is not registered """

    def __init__(self, actor):
        super().__init__(f'Actor not registered: {actor}')


class JoinFailure(MyException):
    """ Failure to join thread """

    def __init__(self, text):
        super().__init__(text=text)
