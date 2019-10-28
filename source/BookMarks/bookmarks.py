""" BookMarks main module

The BookMarks module processes bookmarks exported from Google Chrome.

.. code-block:: rest
    :caption **BookMarks UML**
    :name: BookMarksUml

    @startuml

    [*] --> StartUp
    StartUp --> ReadBookMarks : EvStart
    StartUp : enter : BookMarksStart()

    ReadBookMarks --> Finish : EvFileDone
    ReadBookMarks --> Finish : EvStop

    ReadBookMarks --> AddMeta : EvMetaTag
    ReadBookMarks --> AddTitle : EvTitleTag
    ReadBookMarks --> AddHeader : EvHeaderTag
    ReadBookMarks --> AddTopic : EvTopicTag
    ReadBookMarks --> ReadBookMarks : EvPTag
    ReadBookMarks --> StartList : EvListTag
    ReadBookMarks --> EndList : EvEndListTag

    StartList --> ReadBookMarks : EvTick
    StartList : enter : StartNewList()

    EndList --> ReadBookMarks : EvTick
    EndList : enter : EndCurrentList()

    AddTopic --> AddTopicHeader : EvTopicHeaderTag
    AddTopic --> AddTopicLink : EvATag / NewBookMark()

    AddTopicHeader --> ReadBookMarks : EvTopicHeaderEndTag
    AddTopicHeader --> AddTopicHeader : EvData / SetTopicHeader()

    AddTopicLink --> ReadBookMarks : EvAEndTag / AddBookMark()
    AddTopicLink --> AddTopicLink : EvData / SetBookMarkData()

    AddMeta --> ReadBookMarks : EvTick
    AddMeta : enter : SetMeta()

    AddTitle --> ReadBookMarks : EvTitleEndTag
    AddTitle --> AddTitle : EvData / SetTitle()

    AddHeader --> ReadBookMarks : EvHeaderEndTag
    AddHeader --> AddHeader : EvData / SetHeader()

    Finish : enter : BookMarksDone()
    Finish --> [*]

    @enduml
"""

# System Imports
from abc import ABC
from html.parser import HTMLParser
from enum import Enum

# StateEngineCrank Imports
from StateEngineCrank.modules.PyState import StateMachine

# Project Imports
from structures import BookMarks
from statistics import Statistics

import logger
logger = logger.Logger(__name__)
my_logger = logger.logger

# ==============================================================================
# ===== MAIN STATE CODE = STATE DEFINES & TABLES = START = DO NOT MODIFY =======
# ==============================================================================


class States(Enum):
    InitialState = 1
    FinalState = 2
    StartUp = 3
    ReadBookMarks = 4
    Finish = 5
    AddMeta = 6
    AddTitle = 7
    AddHeader = 8
    AddTopic = 9
    StartList = 10
    EndList = 11
    AddTopicHeader = 12
    AddTopicLink = 13


class Events(Enum):
    EvTick = 1
    EvStart = 2
    EvFileDone = 3
    EvStop = 4
    EvMetaTag = 5
    EvTitleTag = 6
    EvHeaderTag = 7
    EvTopicTag = 8
    EvPTag = 9
    EvListTag = 10
    EvEndListTag = 11
    EvTopicHeaderTag = 12
    EvATag = 13
    EvTopicHeaderEndTag = 14
    EvData = 15
    EvAEndTag = 16
    EvTitleEndTag = 17
    EvHeaderEndTag = 18


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

        self.bookmarks = BookMarks()    #: bookmarks data collection
        self.title = None               #: title of this collection of bookmarks
        self.title_attrs = None         #: :todo: title attrs (is this really needed)
        self.header = None              #: header of this collection of bookmarks
        self.html_data = None           #: data for current html item
        self.html_attrs = None          #: 'attrs' associated with most recent tag
        self.meta_attrs = None          #: attrs for meta tag
        self.meta_data = None           #: :todo: data for meta tag (is this really needed)
        self.list_level = None          #: current list level

        my_logger.debug('UserCode: INIT done')

    def set_attrs(self, attrs):
        """ Function to set 'attrs' associated with most recent 'tag'
            :param attrs: Most recent attributes
        """
        self.html_attrs = attrs
        if self.html_attrs:
            my_logger.info(f'attrs: {self.html_attrs}')
            # self.event(Events.EvAttr)

    def set_html_data(self, data):
        """ Function to set 'html data' associated with most recent 'tag'
            :param data: Most recent attributes
        """
        self.html_data = data.strip()
        if self.html_data:
            my_logger.info(f'data: {self.html_data}')
            self.event(Events.EvData)

    # ===========================================================================
    def AddMeta_SetMeta(self):
        """ Enter function processing for *AddMeta* state.

        State machine enter function processing for the *AddMeta* state.
        This function is called when the *AddMeta* state is entered.
        """
        if self.meta_attrs:
            raise Exception(f'META already set:\n\r\t{self.meta_attrs}\n\r\t{self.html_attrs}')
        self.meta_attrs = self.html_attrs
        my_logger.info(f'META: {self.meta_attrs}')
        self.event(Events.EvTick)

    # ===========================================================================
    def Finish_BookMarksDone(self):
        """ Enter function processing for *Finish* state.

        State machine enter function processing for the *Finish* state.
        This function is called when the *Finish* state is entered.
        """
        my_logger.debug('BookMarksDone')

    # =========================================================
    def SetHeader(self):
        """ State transition processing for *SetHeader*

        State machine state transition processing for *SetHeader*.
        This function is called when the state transition *SetHeader* is taken.

        HTML *H1* tags are used to declare *TheHeader*.
        There is only one (1) HTML *H1* tag in a BookMark file.
        """
        if self.header:
            raise Exception(f'H1_DATA already defined: {self.header}/{self.html_data}')
        self.header = self.html_data
        my_logger.debug(f'HEADER: {self.header}')
        self.bookmarks.add_heading(self.header)

    # =========================================================
    def SetTitle(self):
        """ State transition processing for *SetTitle*

        State machine state transition processing for *SetTitle*.
        This function is called whenever the state transition *SetTitle* is taken.
        """
        if self.title:
            raise Exception(f'TITLE already defined: {self.title}/{self.html_data}')
        self.title = self.html_data
        my_logger.info(f'TITLE: {self.title}')

    # =========================================================
    def SetTopicHeader(self):
        """ State transition processing for *SetTopicHeader*

        State machine state transition processing for *SetTopicHeader*.
        This function is called whenever the state transition *SetTopicHeader* is taken.

        The HTML *H3* tag handler calls this function.
        """
        my_logger.info(f'HEADING: {self.html_data}')
        self.bookmarks.add_heading(self.html_data)

    # ===========================================================================
    def StartList_StartNewList(self):
        """ Enter function processing for *StartList* state.

        State machine enter function processing for the *StartList* state.
        This function is called when the *StartList* state is entered.
        """
        self.bookmarks.start_list()
        self.event(Events.EvTick)

    # ===========================================================================
    def EndList_EndCurrentList(self):
        """ Enter function processing for *EndList* state.

        State machine enter function processing for the *EndList* state.
        This function is called when the *EndList* state is entered.
        """
        self.bookmarks.end_list()
        self.event(Events.EvTick)

    # ===========================================================================
    def StartUp_BookMarksStart(self):
        """ Enter function processing for *StartUp* state.

        State machine enter function processing for the *StartUp* state.
        This function is called when the *StartUp* state is entered.
        We stay in this state until *EvStart* is received.
        """
        pass

    # =========================================================
    def NewBookMark(self):
        """ State transition processing for *NewBookMark*

        State machine state transition processing for *NewBookMark*.
        This function is called whenever the state transition *NewBookMark* is taken.
        """
        self.bookmarks.new_bookmark()

    # =========================================================
    def AddBookMark(self):
        """ State transition processing for *AddBookMark*

        State machine state transition processing for *AddBookMark*.
        This function is called whenever the state transition *AddBookMark* is taken.
        """
        self.bookmarks.add_bookmark(self.html_data, self.html_attrs)

    # =========================================================
    def SetBookMarkData(self):
        """ State transition processing for *SetBookMarkData*

        State machine state transition processing for *SetBookMarkData*.
        This function is called whenever the state transition *SetBookMarkData* is taken.
        """
        self.bookmarks.set_bookmark_data(self.html_data)

# ==============================================================================
# ===== USER STATE CODE = END ==================================================
# ==============================================================================

# ==============================================================================
# ===== MAIN STATE CODE TABLES = START = DO NOT MODIFY =========================
# ==============================================================================


StateTables.state_transition_table[States.InitialState] = {
    Events.EvTick: {'state2': States.StartUp, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.FinalState] = {
}

StateTables.state_transition_table[States.StartUp] = {
    Events.EvStart: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.ReadBookMarks] = {
    Events.EvFileDone: {'state2': States.Finish, 'guard': None, 'transition': None},
    Events.EvStop: {'state2': States.Finish, 'guard': None, 'transition': None},
    Events.EvMetaTag: {'state2': States.AddMeta, 'guard': None, 'transition': None},
    Events.EvTitleTag: {'state2': States.AddTitle, 'guard': None, 'transition': None},
    Events.EvHeaderTag: {'state2': States.AddHeader, 'guard': None, 'transition': None},
    Events.EvTopicTag: {'state2': States.AddTopic, 'guard': None, 'transition': None},
    Events.EvPTag: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
    Events.EvListTag: {'state2': States.StartList, 'guard': None, 'transition': None},
    Events.EvEndListTag: {'state2': States.EndList, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.Finish] = {
    Events.EvTick: {'state2': States.FinalState, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddMeta] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddTitle] = {
    Events.EvTitleEndTag: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
    Events.EvData: {'state2': States.AddTitle, 'guard': None, 'transition': UserCode.SetTitle},
}

StateTables.state_transition_table[States.AddHeader] = {
    Events.EvHeaderEndTag: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
    Events.EvData: {'state2': States.AddHeader, 'guard': None, 'transition': UserCode.SetHeader},
}

StateTables.state_transition_table[States.AddTopic] = {
    Events.EvTopicHeaderTag: {'state2': States.AddTopicHeader, 'guard': None, 'transition': None},
    Events.EvATag: {'state2': States.AddTopicLink, 'guard': None, 'transition': UserCode.NewBookMark},
}

StateTables.state_transition_table[States.StartList] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.EndList] = {
    Events.EvTick: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
}

StateTables.state_transition_table[States.AddTopicHeader] = {
    Events.EvTopicHeaderEndTag: {'state2': States.ReadBookMarks, 'guard': None, 'transition': None},
    Events.EvData: {'state2': States.AddTopicHeader, 'guard': None, 'transition': UserCode.SetTopicHeader},
}

StateTables.state_transition_table[States.AddTopicLink] = {
    Events.EvAEndTag: {'state2': States.ReadBookMarks, 'guard': None, 'transition': UserCode.AddBookMark},
    Events.EvData: {'state2': States.AddTopicLink, 'guard': None, 'transition': UserCode.SetBookMarkData},
}

StateTables.state_function_table[States.InitialState] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.FinalState] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.StartUp] = \
    {'enter': UserCode.StartUp_BookMarksStart, 'do': None, 'exit': None}

StateTables.state_function_table[States.ReadBookMarks] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.Finish] = \
    {'enter': UserCode.Finish_BookMarksDone, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddMeta] = \
    {'enter': UserCode.AddMeta_SetMeta, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTitle] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddHeader] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTopic] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.StartList] = \
    {'enter': UserCode.StartList_StartNewList, 'do': None, 'exit': None}

StateTables.state_function_table[States.EndList] = \
    {'enter': UserCode.EndList_EndCurrentList, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTopicHeader] = \
    {'enter': None, 'do': None, 'exit': None}

StateTables.state_function_table[States.AddTopicLink] = \
    {'enter': None, 'do': None, 'exit': None}

# ==============================================================================
# ===== MAIN STATE CODE TABLES = END = DO NOT MODIFY ===========================
# ==============================================================================


class MyHTMLParser(HTMLParser, ABC):
    """
        EvTick = 1
        EvStart = 2
        EvFileDone = 3
        EvStop = 4
        EvTopicLinkTag = 8
        EvListEndTag = 10
    """
    def __init__(self):
        super().__init__()
        self.open_tag_events = {
            'meta': Events.EvMetaTag,
            'title': Events.EvTitleTag,
            'h1': Events.EvHeaderTag,
            'h3': Events.EvTopicHeaderTag,
            'dl': Events.EvListTag,
            'dt': Events.EvTopicTag,
            'p': Events.EvPTag,
            'a': Events.EvATag,
        }
        self.close_tag_events = {
            'meta': Events.EvTick,
            'title': Events.EvTitleEndTag,
            'h1': Events.EvHeaderEndTag,
            'h3': Events.EvTopicHeaderEndTag,
            'dl': Events.EvEndListTag,
            'dt': Events.EvTick,
            'p': Events.EvTick,
            'a': Events.EvAEndTag,
        }

        # environment initialization is complete so start the parser engine
        self.parser = UserCode()
        self.parser.event(Events.EvStart)
        pass

    # =================================================
    # HTML Parser Base Class Methods
    # =================================================
    def handle_starttag(self, tag, attrs):
        """ ABC: Handle start tags

            :param tag: html tag being processed
            :param attrs: html attributes associated with tag
        """
        my_logger.debug(f'start tag: {tag}')
        if tag in self.open_tag_events:
            self.parser.event(self.open_tag_events[tag])
            self.parser.set_attrs(attrs)
            pass
        else:
            msg = f'no handler for tag [{tag}]'
            my_logger.error(msg)
            raise Exception(msg)

    def handle_endtag(self, tag):
        """ ABC: Handle end tags """
        my_logger.debug(f'end tag: {tag}')
        if tag in self.close_tag_events:
            self.parser.event(self.close_tag_events[tag])
            pass
        else:
            msg = f'no handler for tag [{tag}]'
            my_logger.error(msg)
            raise Exception(msg)

    def handle_data(self, data):
        """ ABC: Handle data """
        self.parser.set_html_data(data)
        pass


if __name__ == '__main__':

    parser = MyHTMLParser()
    try:
        with open(r'Bookmarks/bookmarks_10_5_19.html', mode='r', encoding='utf-8') as html:
            bookmarks_html = html.read()
        parser.feed(bookmarks_html)
        with parser.parser.bookmarks as b:
            statistics = Statistics(b.bookmarks, b.heading_labels, b.headings_dict)
        # grab the variables we want to post process
        pass
    except Exception as e:
        print(f'Exception reading file: {e}')
