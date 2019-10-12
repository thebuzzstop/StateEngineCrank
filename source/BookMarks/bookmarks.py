""" BookMarks main module

The BookMarks module processes bookmarks exported from Google Chrome.

.. code-block:: rest
    :caption **BookMarks UML**
    :name: BookMarksUml

    @startuml

    [*] --> StartUp
    StartUp --> ReadBookMarks : EvStart
    StartUp : enter : BookMarksStart

    ReadBookMarks --> Finish : EvFileDone
    ReadBookMarks --> Finish : EvStop
    ReadBookMarks --> AddTopicHeader : EvTopicHeaderTag
    ReadBookMarks --> AddTopicLink : EvTopicLinkTag
    ReadBookMarks --> StartList : EvListTag
    ReadBookMarks --> EndList : EvListEndTag
    ReadBookMarks --> AddMeta : EvMetaTag
    ReadBookMarks --> AddTitle : EvTitleTag
    ReadBookMarks --> pTag : EvPTag
    ReadBookMarks : do : ReadLine

    StartList --> ReadBookMarks : EvTick
    StartList : enter : StartList
    EndList --> ReadBookMarks : EvTick
    EndList : enter : EndList
    AddMeta --> ReadBookMarks : EvTick
    AddMeta : enter : AddMeta
    AddTitle --> ReadBookMarks : EvTick
    AddTitle : enter : AddTitle
    AddTopicLink --> ReadBookMarks : EvTick
    AddTopicLink : enter : AddTopicLink
    AddTopicHeader --> ReadBookMarks : EvTick
    AddTopicHeader : enter : AddTopicHeader
    pTag --> ReadBookMarks : EvTick
    pTag : enter : Ignore

    Finish : enter : BookMarksDone
    Finish --> [*]

    @enduml
"""

# System Imports
from abc import ABC
from html.parser import HTMLParser
from enum import Enum
import sys
import os
import logging.handlers

# StateEngineCrank Imports
from StateEngineCrank.modules.PyState import StateMachine

# Project Imports

logger = logging.getLogger('bookmarks')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(stream=sys.stdout)
ch.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
ch.setLevel(logging.INFO)
logger.addHandler(ch)

if not os.path.exists('logs'):
    os.makedirs('logs')

fh = logging.handlers.RotatingFileHandler('logs/bookmarks.log', backupCount=5, delay=True)
fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    StartUp = 1
    ReadBookMarks = 2
    Finish = 3
    AddTopicHeader = 4
    AddTopicLink = 5
    StartList = 6
    EndList = 7
    AddMeta = 8
    AddTitle = 9
    pTag = 10


class Events(Enum):
    EvTick = 1
    EvStart = 2
    EvFileDone = 3
    EvStop = 4
    EvTopicHeaderTag = 5
    EvTopicLinkTag = 6
    EvListTag = 7
    EvListEndTag = 8
    EvMetaTag = 9
    EvTitleTag = 10
    EvPTag = 11


class StateTables(object):
    state_transition_table = {}
    state_function_table = {}

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = END = DO NOT MODIFY =========
# ==============================================================================

# ==============================================================================
# ===== USER STATE CODE = BEGIN ================================================
# ==============================================================================


class UserCode(StateMachine):

    def __init__(self, id_=None):
        StateMachine.__init__(self, id=id_, startup_state=States.StartUp,
                              function_table=StateTables.state_function_table,
                              transition_table=StateTables.state_transition_table)

    # ===========================================================================
    def Finish_BookMarksDone(self):
        """ Enter function processing for *Finish* state.

        State machine enter function processing for the *Finish* state.
        This function is called when the *Finish* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def StartUp_BookMarksStartUp(self):
        """ Enter function processing for *StartUp* state.

        State machine enter function processing for the *StartUp* state.
        This function is called when the *StartUp* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def AddMeta_AddMeta(self):
        """ Enter function processing for *AddMeta* state.

        State machine enter function processing for the *AddMeta* state.
        This function is called when the *AddMeta* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def AddTitle_AddTitle(self):
        """ Enter function processing for *AddTitle* state.

        State machine enter function processing for the *AddTitle* state.
        This function is called when the *AddTitle* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def AddTopicHeader_AddTopicHeader(self):
        """ Enter function processing for *AddTopicHeader* state.

        State machine enter function processing for the *AddTopicHeader* state.
        This function is called when the *AddTopicHeader* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def AddTopicLink_AddTopicLink(self):
        """ Enter function processing for *AddTopicLink* state.

        State machine enter function processing for the *AddTopicLink* state.
        This function is called when the *AddTopicLink* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def EndList_EndList(self):
        """ Enter function processing for *EndList* state.

        State machine enter function processing for the *EndList* state.
        This function is called when the *EndList* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def ReadBookMarks_ReadLine(self):
        """ *Do* function processing for the *ReadBookMarks* state

        State machine *do* function processing for the *ReadBookMarks* state.
        This function is called once every state machine iteration to perform processing
        for the *ReadBookMarks* state.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def StartList_StartList(self):
        """ Enter function processing for *StartList* state.

        State machine enter function processing for the *StartList* state.
        This function is called when the *StartList* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def StartUp_BookMarksStart(self):
        """ Enter function processing for *StartUp* state.

        State machine enter function processing for the *StartUp* state.
        This function is called when the *StartUp* state is entered.

        :todo: FIXME
        """
        return

    # ===========================================================================
    def pTag_Ignore(self):
        """ Enter function processing for *pTag* state.

        State machine enter function processing for the *pTag* state.
        This function is called when the *pTag* state is entered.

        :todo: FIXME
        """
        return

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.ReadBookMarks] = {
    Events.EvFileDone: {'state2': States.Finish, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
    Events.EvTopicHeaderTag: {'state2': States.AddTopicHeader, 'guard': None, 'transition': None},
    Events.EvTopicLinkTag: {'state2': States.AddTopicLink, 'guard': None, 'transition': None},
    Events.EvListTag: {'state2': States.StartList, 'guard': None, 'transition': None},
    Events.EvListEndTag: {'state2': States.EndList, 'guard': None, 'transition': None},
    Events.EvMetaTag: {'state2': States.AddMeta, 'guard': None, 'transition': None},
    Events.EvTitleTag: {'state2': States.AddTitle, 'guard': None, 'transition': None},
    Events.EvPTag: {'state2': States.pTag, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Finish] = {
    Events.EvTick: {'state2': States.FinalState, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddTopicHeader] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddTopicLink] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.StartList] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.EndList] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddMeta] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddTitle] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.pTag] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_BookMarksStart, 'do': None, 'exit': None}

StateTables.state_function_table[States.ReadBookMarks] = \
    {'enter': None, 'do': UserCode.ReadBookMarks_ReadLine, 'exit': None}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_BookMarksDone, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTopicHeader] = \
    {'enter': UserCode.AddTopicHeader_AddTopicHeader, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTopicLink] = \
    {'enter': UserCode.AddTopicLink_AddTopicLink, 'do': None, 'exit': None}

StateTables.state_function_table[States.StartList] = \
    {'enter': UserCode.StartList_StartList, 'do': None, 'exit': None}

StateTables.state_function_table[States.EndList] = \
    {'enter': UserCode.EndList_EndList, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddMeta] = \
    {'enter': UserCode.AddMeta_AddMeta, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTitle] = \
    {'enter': UserCode.AddTitle_AddTitle, 'do': None, 'exit': None}

StateTables.state_function_table[States.pTag] = \
    {'enter': UserCode.pTag_Ignore, 'do': None, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================


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


class Bookmark(object):
    """ A bookmark """
    def __init__(self, text, href, add_date, icon=None):
        self.text = text
        self.link = href
        self.add_date = add_date
        self.icon = icon


class MyHTMLParser(HTMLParser, ABC):

    def __init__(self):
        super().__init__()
        self.open_tag_handlers = {
            'meta': self.meta_handler,
            'title': self.title_handler,
            'h1': self.h1_handler,
            'h3': self.h3_handler,
            'dl': self.dl_handler,
            'dt': self.dt_handler,
            'p': self.p_handler,
            'a': self.a_handler,
        }
        self.close_tag_handlers = {
            'meta': self.meta_handler_close,
            'title': self.title_handler_close,
            'h1': self.h1_handler_close,
            'h3': self.h3_handler_close,
            'dl': self.dl_handler_close,
            'dt': self.dt_handler_close,
            'p': self.p_handler_close,
            'a': self.a_handler_close,
        }

        self.bookmarks = {}         #: a dictionary of bookmarks that we create from HTML
        self.parents = []           #: a list of parents

        self.title = None           #: title of this collection of bookmarks
        self.title_attrs = None     #: :todo: title attrs (is this really needed)
        self.html_data = None       #: data for current html item
        self.meta_attrs = None      #: attrs for meta tag
        self.meta_data = None       #: :todo: data for meta tag (is this really needed)
        self.h1_data = None         #: capture H1 data (there is only one)
        self.h3_data = []           #: capture H3 data (there are many)

        self.list_level = None      #: current list level

    def handle_starttag(self, tag, attrs):
        """ Handle start tags

            :param tag: html tag being processed
            :param attrs: html attributes associated with tag
        """
        logger.debug(f'start tag: {tag}')
        if tag in self.open_tag_handlers:
            self.open_tag_handlers[tag](attrs)
        else:
            msg = f'no handler for tag [{tag}]'
            logger.error(msg)
            raise Exception(msg)

    def handle_endtag(self, tag):
        """ Handle end tags """
        logger.debug(f'end tag: {tag}')
        if tag in self.close_tag_handlers:
            self.close_tag_handlers[tag]()
        else:
            logger.exception(f'no handler for tag {tag}')

    def handle_data(self, data):
        """ Handle data """
        self.html_data = data.strip()
        if self.html_data:
            logger.info(f'data: {self.html_data}')

    def meta_handler(self, attrs):
        """ Handle <META> tag """
        self.meta_attrs = attrs
        if not self.meta_attrs:
            return
        logger.info(f'meta: {self.meta_attrs}')

    def title_handler(self, attrs):
        """ Handle <TITLE> tag """
        if not attrs:
            return
        logger.info(f'title: {attrs}')

    def a_handler(self, attrs):
        """ Handle <A> tag """
        if not attrs:
            return
        logger.info(f'a: {attrs}')

    def dl_handler(self, attrs):
        """ Handle <DL> tag - starts a list """
        if self.list_level is None:
            self.list_level = 0
        else:
            self.list_level += 1
        if not attrs:
            return
        logger.info(f'dl: {attrs}')

    def dt_handler(self, attrs):
        """ Handle <DT> tag - adds an entry into current list """
        if not attrs:
            return
        logger.info(f'dt: {attrs}')

    def p_handler(self, attrs):
        """ Handle <P> tag """
        if not attrs:
            return
        logger.info(f'p: {attrs}')

    def h1_handler(self, attrs):
        """ Handle <H1> tag """
        if not attrs:
            return
        logger.info(f'h1: {attrs}')

    def h3_handler(self, attrs):
        """ Handle <H3> tag """
        self.h3_level += 1
        if not attrs:
            return
        logger.info(f'h3: {attrs}')

    def meta_handler_close(self):
        """ Handle <META> tag """
        self.meta_data = self.html_data
        logger.debug(f'meta: close')

    def title_handler_close(self):
        """ Handle <TITLE> tag """
        self.title = self.html_data
        logger.debug(f'title: {self.title} [close]')

    def a_handler_close(self):
        """ Handle <A> tag """
        logger.debug(f'a: close')

    def dt_handler_close(self):
        """ Handle <DT> tag - adds an entry into current list """
        logger.debug(f'dt: close')

    def dl_handler_close(self):
        """ Handle <DL> tag - starts a list """
        logger.debug(f'dl: close')

    def p_handler_close(self):
        """ Handle <P> tag """
        logger.debug(f'p: close')

    def h1_handler_close(self):
        """ Handle <H1> tag """
        self.h1_data = self.html_data
        logger.debug(f'h1: close')

    def h3_handler_close(self):
        """ Handle <H3> tag """
        self.h3_data = self.html_data
        logger.debug(f'h3: close')


def main():
    parser = MyHTMLParser()
    try:
        with open(r'bookmarks_10_5_19.html', mode='r', encoding='utf-8') as html:
            bookmarks_html = html.read()
        parser.feed(bookmarks_html)
        pass
    except Exception as e:
        print(f'Exception reading file: {e}')
    finally:
        fh.doRollover()


if __name__ == '__main__':

    main()
