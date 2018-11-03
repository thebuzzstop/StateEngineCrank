"""
Created on Jun 25, 2016

@author:    Mark Sawyer
@date:      25-Jun-2016

@package:   StateEngineCrank
@module:    Borg Class

@brief:     Borg Class
@details:   Borg Class snarfed from Python Cookbook (O'Reilly)

            Usage:
                class Foo(Borg): pass
                x = Foo()    # 1st instantiation of Foo()
                y = Foo()    # 2nd instantiation of Foo()

                # x and y will share state

            Refer to the Python Cookbook for the details.

@copyright: none
"""
print('Loading modules: ', __file__, 'as', __name__)


class Borg(object):
    """ Return a Borg object. (Replaces 'Singleton')
        snarfed from Python Cookbook (O'Reilly)
    """

    _shared_state = {}

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls, *args, **kwargs)
        obj.__dict__ = cls._shared_state
        return obj
