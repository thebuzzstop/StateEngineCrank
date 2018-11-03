"""
Created on Jun 28, 2016

@author:    Mark Sawyer
@date:      Jun 28, 2016

@package:   StateEngineCrank
@module:    Singleton Class

@brief:     Singleton Class
@details:   Singleton Class snarfed from Python Cookbook

            Usage:
                class Foo(Singleton): pass
                x = Foo()    # 1st instantiation of Foo()
                y = Foo()    # 2nd instantiation of Foo()

                # x and y will refer to the same object instantiation

            Refer to the Python Cookbook for the details.

@copyright: none
"""
print('Loading modules: ', __file__, 'as', __name__)


class Singleton(object):
    """ Return a Singleton object.
        Singleton Class snarfed from Python Cookbook.
        Refer to the Python Cookbook for the details.
    """
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._inst
