""" BookMarks Structures module

The BookMarks Structures module maintains bookmark structures::

 + Bookmarks
 + Headings
 + Topics
 + Lists

.. code-block:: rest
    :caption **BookMarks List UML**
    :name: BookMarksListUml
"""

# System imports

# Project imports
import logger as log


class Bookmark(object):
    """ A bookmark """
    def __init__(self, text, href, add_date, icon=None):
        self.text = text
        self.link = href
        self.add_date = add_date
        self.icon = icon


class Heading(object):
    """ A bookmark heading """
    def __init__(self, title, parent, add_date, last_modified):
        """ Constructor """
        self.title = title
        self.parent = parent
        self.add_date = add_date
        self.last_modified = last_modified


class List(object):
    """ A bookmark list """
    def __init__(self, parent, level):
        """ Constructor """
        self.parent = parent
        self.level = level
        self.list = []


class BookMarksList(object):
    """ Class implementing a multi-level list """

    def __init__(self):
        self.logger = log.Logger(__name__).logger
        self.logger.debug('INIT')

        self.level = 0      #: Current level

    def start_list(self, name):
        """ Start a new list
            :param name: Name of the list
        """
        self.level += 1

    def end_list(self):
        """ End currently active list

            :raises: NoList
        """
        if not self.level:
            raise Exception("NoList")

        self.level -= 1
