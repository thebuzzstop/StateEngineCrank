# System imports


class InvalidMVC(Exception):
    """ Invalid model/view/controller passed """
    pass


class InvalidModel(Exception):
    """ Invalid model passed """
    pass


class InvalidView(Exception):
    """ Invalid view passed """
    pass


class UnknownModelEvent(Exception):
    """ Invalid/Unknown model event received """
    pass


class UnknownViewEvent(Exception):
    """ Invalid/Unknown view event received """
    pass
