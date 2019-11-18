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
from urllib.parse import urlparse

# Project imports
import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class List(object):
    """ A bookmark list """
    def __init__(self, level, label):
        """ Constructor """
        self.level = level
        self.label = label
        self.list = []


class BookMark(object):
    """ A bookmark """
    def __init__(self, label, heading, href, add_date, icon=None):
        self.label = label
        self.heading = heading
        self.scanned = False
        self.attrs = {
            'href': href,
            'add_date': add_date,
            'icon': icon,
            'attrs': []
        }
        self.href_urlparts = None

    def add_attr(self, attr, value):
        """ add attribute 'attr' / 'value' to bookmark
            :param attr: Attribute designation
            :param value: Attribute value
        """
        if attr in self.attrs:
            self.attrs[attr] = value
            if attr == 'href':
                self.href_urlparts = urlparse(value)
        else:
            self.attrs['attrs'].append({attr: value})


class Heading(object):
    """ A bookmark heading """

    def __init__(self, level, label, heading_stack, add_date, last_modified):
        """ Constructor """
        self.level = level
        self.label = label
        self.attrs = {
            'add_date': add_date,
            'last_modified': last_modified,
            'personal_toolbar_folder': None
        }
        #: current state of heading_stack when created
        self.heading_stack = heading_stack

        #: current state of heading_stack when created - label text only
        self.heading_stack_text = []
        for heading in heading_stack:
            self.heading_stack_text.append(heading.label)

        #: list of topic links and other sub-headings
        self.list = None


class HeadingLabel(object):
    """ Bookmark heading label """

    def __init__(self, label, level, stack):
        """ Constructor """
        self.label = label
        self.levels = [level]
        self.stack = [stack]
        self.count = 1

    def add_label(self, level, stack):
        self.count += 1
        if level not in self.levels:
            self.levels.append(level)
            self.stack.append(stack)


class HeadingLabels(object):
    """ Bookmark heading label collection """

    def __init__(self):
        """ Constructor """
        self.labels = {}

    def add_label(self, heading):
        """ Add a heading label to the dictionary
            :param heading:
        """
        if heading.label not in self.labels:
            self.labels[heading.label] = HeadingLabel(heading.label, heading.level, heading.heading_stack_text)
        else:
            self.labels[heading.label].add_label(heading.level, heading.heading_stack_text)


class BookMarks(object):
    """ Class implementing a multi-level list """

    # =================================================================
    def __init__(self):
        my_logger.debug('INIT')

        self.level = 0              #: Current level
        self.heading = None         #: Heading for current level

        #: Heading labels, used in post-processing
        self.heading_labels = HeadingLabels()

        self.headings_dict = {}     #: Headings: Dict
        self.headings_stack = []    #: Headings: Stack (first-in, last-out)
        self.headings_dups = []     #: Headings: Duplicates
        self.bookmarks = {}         #: Dictionary of bookmarks

        self.bookmark = None

    # =================================================================
    def headings_data(self):
        return {
            'dict': self.headings_dict,
            'dups': self.headings_dups,
            'labels': self.heading_labels,
        }

    # =================================================================
    def start_list(self):
        """ Start a new list
            The last header passed to us will be used as the heading
            :raises: DuplicateKey
        """
        if not self.heading:
            raise Exception("No heading for list")
        if self.heading.list:
            raise Exception("List already active")

        self.level += 1
        self.debug(f'LIST: {self.level} {self.heading.label}')

        # keep a list of all headings passed to us
        self.heading_labels.add_label(self.heading)

        # create a key for this heading
        key = self.bookmarks_key(self.level, self.heading.label)
        if key in self.headings_dict:
            self.headings_dups.append(key)
            key = f'{key} (DUP)'
            if key in self.headings_dict:
                raise Exception(f'DUPLICATE KEY: {key}')

        # create a new list, add it to our dictionary and push it onto the stack
        self.heading.list = List(self.level, self.heading.label)
        self.headings_dict[key] = self.heading.list
        self.headings_stack.append(self.heading)

    # =================================================================
    def end_list(self):
        """ End currently active list

            :raises: NoList
        """
        if not self.level:
            raise Exception("NoList")
        self.debug(f'LISTEND: {self.level}')
        self.level -= 1
        # pop the current heading off the stack
        if self.headings_stack:
            self.headings_stack.pop()
        # new current heading is now the top of the stack
        if self.headings_stack:
            self.heading = self.headings_stack[-1]
        else:
            self.heading = None

    # =================================================================
    def add_heading(self, label):
        """ Add a new heading to the list
            :param label: Text for the heading
        """
        self.debug(f'HEADING: {label}')
        self.heading = Heading(self.level, label, self.headings_stack, None, None)
        self.heading_labels.add_label(self.heading)

    # =================================================================
    def set_bookmark_data(self, data):
        """ Set data for current bookmark """
        self.debug(f'BookMark: {data}')
        self.bookmark.label = data

    # =================================================================
    def new_bookmark(self):
        """ Add a new bookmark to the dictionary """
        if self.bookmark:
            raise Exception(f'Overwriting bookmark {self.bookmark}')
        self.bookmark = BookMark(None, None, None, None, None)
        self.debug(f'BookMark: NEW')

    # =================================================================
    def add_bookmark(self, label, attrs):
        """ Add a new bookmark to the dictionary

            :param label: Bookmark label
            :param attrs: Bookmark attrs
        """
        self.debug(f'BookMark: {label}:{attrs}')
        self.bookmark.label = label
        self.bookmark.heading = self.heading
        # process all attributes passed to us
        for attr, value in attrs:
            if attr in self.bookmark.attrs:
                self.bookmark.add_attr(attr, value)

        # add new bookmark to the list associated with the current heading
        self.heading.list.list.append(self.bookmark)

        # add new bookmark to main bookmark dictionary
        # if the key already exists then convert the entry to a list
        key = self.bookmarks_key(self.level, label)
        if key not in self.bookmarks:
            self.bookmarks[key] = [self.bookmark]
        else:
            self.bookmarks[key].append(self.bookmark)

        # zap the bookmark for logic error detection
        self.bookmark = None

    # =================================================================
    @staticmethod
    def bookmarks_key(level, label):
        """ Make a bookmarks key given a level and a heading

            :param level: Current level
            :param label: Text string for heading
        """
        return f'{level:02d}-{label}'

    # =================================================================
    def debug(self, text):
        """ Print debug information with level added

            :param text: debug text to display
        """
        level_plus = '+'*self.level
        my_logger.debug(f'{self.level:02d}{level_plus} {logger.clean(text)}')
