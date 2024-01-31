""" BookMarks Structures module

The BookMarks Structures module maintains bookmark structures.

.. code-block:: rest
    :caption: **BookMarks List UML**
    :name: BookMarksClassUml

    @startuml

    class List {
        A generic list with custom attributes
        ===
        level : list level
        label : list label
        list [] : the actual list
    }

    class BookMark {
        A bookmark as parsed from bookmarks.html
        ===
        label : bookmark label
        heading : bookmark heading (section)
        scanned : boolean True when bookmark has been scanned
        attrs : url_parse attributes (href, add_date, icon, attrs)
        href_urlparts : url_parse href parts (components)
        scheme : html parsed scheme, e.g. http, https, ftp, etc.
        hostname : html parsed hostname, e.g. ford.com
        path : html parsed path, e.g. /index.html
        ---
        add_attr(attr, value) : add attr/value to bookmark object
    }

    class Heading {
        Bookmark heading
        ===
        level : current heading level
        label : heading label
        attrs : bookmark attributes
        heading_stack : current stack of headings
    }

    class HeadingLabel {
        Bookmark heading label
        ===
        label : label text
        levels [] : levels in which this label appears
        stack [] : current stack of headings
        count : count of occurrences of this label
        ---
        add_label(level, stack) : add a label to the collection
    }

    class HeadingLabels {
        Bookmark heading label collection
        ===
        labels [] : dictionary of labels
        ---
        add_label(heading) : add a heading label to the dictionary
    }
    HeadingLabels o-- HeadingLabel

    class BookMarks {
        Class that implements a multi-level list of bookmarks.
        ===
        level : current bookmark parsing level
        heading : heading for current level
        headings_dict [] : dictionary of headings
        headings_dups [] : list of duplicate headings
        bookmarks [] : Dictionary of bookmarks
        heading_labels : HeadingLabels object
        ---
        start_list() : begin a new html list
        end_list() : end current html list
        add_heading(label) : set bookmark heading to 'label'
        set_bookmark_data(data) : set bookmark label to 'data'
        new_bookmark() : create new bookmark
        add_bookmark(label, attrs) : add new bookmark label and attributes
        bookmarks_key(level, label) : Make a bookmarks key given a level and a heading
        debug(text) : Print debug information with level added
    }
    BookMarks o-- BookMark
    BookMarks o-- Heading
    BookMarks o-- HeadingLabels
    @enduml

"""

# System imports
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# Project imports
from the_config import TheConfig
from exceptions import MyException
from logger import Logger, clean as clean_text
logger = Logger(name=__name__, log_level=TheConfig.logging_level()).logger


class StructuresList:
    """A list with custom attributes used for structures"""

    def __init__(self, level, label):
        """ Constructor """
        self.level = level
        self.label = label
        self.list = []


#: BookMark global variable - current BookMark ID
_bm_id: int = 0
#: BookMark counter - bumped every init(), decremented for __del__()
_bm_counter: int = 0

def bm_id() -> int:
    """BM ID generator function

    Returns unique integer ID for each call.
    """
    global _bm_id, _bm_counter
    _bm_id += 1
    _bm_counter += 1
    return _bm_id

def bm_counter() -> int:
    """Function returning BookMark counter"""
    return _bm_counter


class BookMark:
    """ A bookmark """

    def __del__(self):
        """Decrement the global counter"""
        global _bm_counter
        _bm_counter -= 1

    def __init__(self, label, heading, href, add_date, icon=None):
        """BookMark class constructor"""
        self.id: int = bm_id()          #: BM unique ID
        self.label: str = label         #: BM string label
        self.heading: str = heading     #: BM heading this BM belongs under
        self._scanned: bool = False     #: BM has been scanned True/False
        self._tested: bool = False      #: BM has been tested True/False
        #: BM URL attributes
        self.attrs: Dict[str, Any] = {
            'href': href,
            'add_date': add_date,
            'icon': icon,
            'attrs': []
        }
        #: URL parts as parsed by URL parser lib
        self.href_urlparts = None

        # populate the following for ease of parsing later during reformat
        #: URL scheme (http, https, etc)
        self.scheme: Optional[str] = None
        #: URL scheme override - used to convert HTTP to HTTPS when requested
        self.scheme_override: Optional[str] = None
        #: URL hostname (e.g. www.google.com)
        self.hostname: Optional[str] = None
        #: URL path (e.g. /index.html
        self.path: Optional[str] = None
        #: Friendly hostname per config.ini (optional)
        self.friendly_host_name: Optional[str] = None

    # ==========================================
    # Class Properties
    # ==========================================

    @property
    def url(self) -> str:
        """Property returning BookMark URL string

        NB: Return override scheme if present
        """
        if self.scheme_override:
            return f'{self.scheme_override}://{self.hostname}{self.path}'
        else:
            return f'{self.scheme}://{self.hostname}{self.path}'

    @property
    def scanned(self) -> bool:
        """Property returning bookmark 'scanned' status

        A bookmark is marked as 'scanned' during Analysis processing.
        """
        return self._scanned

    @scanned.setter
    def scanned(self, value: bool):
        """Property setter - scanned"""
        self._scanned = value

    @property
    def tested(self) -> bool:
        """Property returning bookmark 'teste' status

        A bookmark is marked as 'tested' when the URL has been verified
        as being accessible.
        """
        return self._tested

    @property
    def protocol(self) -> str:
        """Property returning bookmark protocol (HTTP, HTTPS)"""
        return self.scheme

    @protocol.setter
    def protocol(self, value):
        """Property setter for protocol

        :param value: New value to set
        """
        self.scheme = value

    @property
    def is_http(self) -> bool:
        """Property returning True if protocol is HTTP"""
        return self.scheme == 'HTTP' or self.scheme == 'http'

    @property
    def is_localhost(self) -> bool:
        """Property returning True if BookMark points to localhost"""
        return self.hostname.startswith('192.168')

    @property
    def protocol_override(self) -> Optional[str]:
        """Property returning status of Protocol override

        :return: Current protocol override
        """
        return self.scheme_override

    @protocol_override.setter
    def protocol_override(self, value: str):
        """Property setter for protocol override

        :param value: New value to set
        """
        self.scheme_override = value

    @tested.setter
    def tested(self, value: bool):
        """Property setter - tested"""
        self._tested = value

    # ==========================================
    # Class support functions
    # ==========================================

    def add_attr(self, attr, value):
        """ add attribute 'attr' / 'value' to bookmark

        :param attr: Attribute designation
        :param value: Attribute value
        """
        if attr in self.attrs:
            self.attrs[attr] = value
            if attr == 'href':
                self.href_urlparts = urlparse(value)
                self.scheme = self.href_urlparts.scheme
                self.hostname = self.href_urlparts.hostname
                self.path = self.href_urlparts.path
        else:
            self.attrs['attrs'].append({attr: value})


class Heading:
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
        self.structures_list = None


class HeadingLabel:
    """ Bookmark heading label """

    def __init__(self, label, level, stack):
        """ Constructor

        :param label: label text
        :param level: current heading level
        :param stack: current heading stack
        """
        self.label = label
        self.levels = [level]
        self.stack = [stack]
        self.count = 1

    def add_label(self, level, stack):
        """ Add a label to the collection

        :param level: current heading level
        :param stack: current heading stack
        """
        self.count += 1
        if level not in self.levels:
            self.levels.append(level)
            self.stack.append(stack)


class HeadingLabels:
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


class Borg:
    """There can only be one"""

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class BookMarks(Borg):
    """ Class implementing a multi-level list """

    # =================================================================
    def __init__(self):
        Borg.__init__(self)
        if self._shared_state:
            return

        logger.info('INIT (%s)', __name__)

        self.level = 0  #: Current level
        self.heading = None  #: Heading for current level

        #: Heading labels, used in post-processing
        self.heading_labels = HeadingLabels()

        self.headings_dict = {}     #: Headings: Dict
        self.headings_stack = []    #: Headings: Stack (first-in, last-out)
        self.headings_dups = []     #: Headings: Duplicates
        self.bookmarks = {}         #: Dictionary of bookmarks

        #: bookmark currently being processed / created
        self.bookmark = None

    # =================================================================
    def start_list(self):
        """ Start a new list

        The last header passed to us will be used as the heading

        :raises: DuplicateKey
        """
        if not self.heading:
            raise MyException("No heading for list")
        if self.heading.structures_list:
            raise MyException("List already active")

        self.level += 1
        self.debug(f'LIST: {self.level} {self.heading.label}')

        # keep a list of all headings passed to us
        self.heading_labels.add_label(self.heading)

        # create a key for this heading
        key = self.bookmarks_key(self.level, self.heading.label)
        for try_count in range(50):
            if key not in self.headings_dict:
                # create a new list, add it to our dictionary and push it onto the stack
                self.heading.structures_list = StructuresList(self.level, self.heading.label)
                self.headings_dict[key] = self.heading.structures_list
                self.headings_stack.append(self.heading)
                return
            else:
                # add the key to our DUPs list, append 'DUP' to the key and try again
                self.headings_dups.append(key)
                key = f'{key}' + '+' * try_count
        raise MyException(f'DUPLICATE KEY: {key}')

    # =================================================================
    def end_list(self):
        """ End currently active list

        :raises: NoList
        """
        if not self.level:
            raise MyException("NoList")
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
            raise MyException(f'Overwriting bookmark {self.bookmark}')
        self.bookmark = BookMark(label=None, heading=None, href=None, add_date=None, icon=None)
        self.debug(f'BookMark: {self.bookmark.id:04d} NEW')

    # =================================================================
    def add_bookmark(self, label, attrs):
        """ Add a new bookmark to the dictionary

        :param label: Bookmark label
        :param attrs: Bookmark attrs
        """
        self.debug(f'BookMark: {self.bookmark.id:04d} {label}:{attrs}')
        self.bookmark.label = label
        self.bookmark.heading = self.heading
        # process all attributes passed to us
        for attr, value in attrs:
            if attr in self.bookmark.attrs:
                self.bookmark.add_attr(attr, value)

        # add new bookmark to the list associated with the current heading
        self.heading.structures_list.list.append(self.bookmark)

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
        level_plus = '+' * self.level
        logger.debug('%02d%s %s', self.level, level_plus, clean_text(text))
