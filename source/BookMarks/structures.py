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
import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class Bookmark(object):
    """ A bookmark """
    def __init__(self, text, href, add_date, icon=None):
        self.text = text
        self.link = href
        self.add_date = add_date
        self.icon = icon


class Heading(object):
    """ A bookmark heading """
    def __init__(self, level, heading, add_date, last_modified):
        """ Constructor """
        self.level = level
        self.heading = heading
        self.add_date = add_date
        self.last_modified = last_modified


class List(object):
    """ A bookmark list """
    def __init__(self, level, heading):
        """ Constructor """
        self.level = level
        self.heading = heading
        self.list = []


class BookMarks(object):
    """ Class implementing a multi-level list """

    # =================================================================
    def __init__(self):
        my_logger.debug('INIT')

        self.level = 0              #: Current level
        self.heading = None         #: Heading for current level
        self.current_list = None    #: current list being created

        self.headings_dict = {}     #: Headings: Dict
        self.headings_list = []     #: Headings: List
        self.headings_stack = []    #: Headings: Stack (first-in, last-out)
        self.bookmarks = {}         #: Dictionary of bookmarks

    # =================================================================
    def start_list(self):
        """ Start a new list
            The last header passed to us will be used as the heading
            :raises: DuplicateKey
        """
        self.level += 1
        self.debug(f'LIST: {self.level} {self.heading}')

        # keep a list of all headings passed to us
        if self.heading not in self.headings_list:
            self.headings_list.append(self.heading)

        # create a key for this heading
        key = self.bookmarks_key(self.level, self.heading)
        if key in self.headings_dict:
            raise Exception(f'DUPLICATE KEY: {key}')

        # create a new list, add it to our dictionary and push it onto the stack
        self.current_list = List(self.level, self.heading)
        self.headings_dict[key] = self.current_list
        self.headings_stack.append(self.current_list)

    # =================================================================
    def end_list(self):
        """ End currently active list

            :raises: NoList
        """
        if not self.level:
            raise Exception("NoList")
        self.debug(f'ListEnd: {self.level}')
        self.level -= 1
        # pop the current heading off the stack
        self.headings_stack.pop()
        # new current heading is now the top of the stack
        self.heading = self.headings_stack[-1]
        self.current_list = self.heading

    # =================================================================
    def add_heading(self, text):
        """ Add a new heading to the list
            :param text: Text for the heading
        """
        self.debug(f'Heading: {text}')
        if text not in self.headings_list:
            self.headings_list.append(text)
        self.headings_stack.append(text)
        self.heading = text

    # =================================================================
    def add_bookmark(self, text):
        """ Add a new bookmark to the dictionary

            :param text: Text for the bookmark
        """
        self.debug(f'BookMark: {text}')

    # =================================================================
    @staticmethod
    def bookmarks_key(level, heading):
        """ Make a bookmarks key given a level and a heading

            :param level: Current level
            :param heading: Text string for heading
        """
        return f'{level:02d}-{heading}'

    # =================================================================
    def debug(self, text):
        """ Print debug information with level added

            :param text: debug text to display
        """
        level_plus = '+'*self.level
        my_logger.debug(f'{self.level:02d}{level_plus} {text}')
