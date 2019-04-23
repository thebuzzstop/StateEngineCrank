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


class InvalidMVC(MyException):
    """ Invalid model/view/controller passed """
    pass


class InvalidModel(MyException):
    """ Invalid model passed """

    def __init__(self, model):
        super().__init__('Invalid model: %s' % model)


class InvalidView(MyException):
    """ Invalid view passed """

    def __init__(self, view):
        super().__init__('Invalid view: %s' % view)


class UnknownModelEvent(MyException):
    """ Invalid/Unknown model event received """
    pass


class UnknownViewEvent(MyException):
    """ Invalid/Unknown view event received """
    pass


class ClassAlreadyRegistered(MyException):
    """ Class name is already registered """
    pass


class EventAlreadyRegistered(MyException):
    """ Event name is already registered """
    pass


class ActorAlreadyRegistered(MyException):
    """ Event actor is already registered """
    pass


class ClassNotRegistered(MyException):
    """ Class name is not registered """
    pass


class EventNotRegistered(MyException):
    """ Event name is not registered """
    pass


class ActorNotRegistered(MyException):
    """ Event actor is not registered """
    pass
