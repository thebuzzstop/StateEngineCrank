""" BookMarks Reformat module

The BookMarks reformat module reorders and reorganizes the bookmarks::

 * Protocols
 * Domains
 * Subdomains
 * Headings

"""

# System imports
import datetime

# Project imports
from analyze import Analyze
from config import TheConfig

import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class Reformat(object):
    """ Class to reformat bookmarks """

    def __init__(self, analysis: Analyze):
        """ Analyze constructor

            :param analysis: Analize object after processing
        """
        self.analysis = analysis
        self.headings = TheConfig.headings      #: users headings configuration
        self.menubar = TheConfig.menubar        #: user menubar configuration
        self.output = [TheConfig.HEADER_HTML]   #: start with bookmarks file header

        #: date stamp for all html entities we create
        self.datestamp = int(datetime.datetime.now().timestamp())

        # create output structure
        self.write(TheConfig.LIST_HTML)
        self.write(
            TheConfig.TOOLBAR_HTML_FORMAT.format(self.datestamp, self.datestamp, 'Bookmarks Bar')
        )
        self.write_section('head')
        for section in self.headings:
            self.write_section(section)
        self.write_section('tail')
        self.write(TheConfig.LIST_HTML_END)
        pass

    def write(self, html):
        """ write html to output string
            :param html: html string(s) to output, may be a list
        """
        if isinstance(html, list):
            for h in html:
                self.write(h)
            return
        self.output.append(html)

    def write_section(self, section):
        """ write entire section to output string
            :param section: bookmarks section to output
        """
        self.write(TheConfig.LIST_HTML)
        for bm in self.menubar[section]:
            self.write(bm)
        self.write(TheConfig.LIST_HTML_END)
        pass
