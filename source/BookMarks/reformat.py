""" BookMarks Reformat module

The BookMarks reformat module reorders and reorganizes the bookmarks::

 * Protocols
 * Domains
 * Subdomains
 * Headings

"""

# System imports
import datetime
from typing import Union

# Project imports
from analyze import Analyze
from config import TheConfig
from structures import BookMark

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
        self.menubar_spec = TheConfig.menubar   #: user menubar configuration
        self.menubar_data = analysis.menubar()  #: menubar scanned data
        self.output = [TheConfig.HEADER_HTML]   #: start with bookmarks file header
        self.indent = 0                         #: level to indent

        #: date stamp for all html entities we create
        self.datestamp = int(datetime.datetime.now().timestamp())

        # create output structure
        self.write(TheConfig.LIST_HTML)
        self.write_toolbar_heading('Bookmarks Bar')
        self.begin_list()
        self.write_section('head')
        for section in self.headings:
            self.write_section(section)
        self.write_section('tail')
        self.end_list()
        pass

    def write_section(self, section):
        """ write entire section to output string
            :param section: bookmarks section to output
        """
        if section in self.headings:
            self.write_heading(section)
            self.begin_list()
            for subsection in self.menubar_spec[section]:
                self.write_heading(subsection)
                self.begin_list()
                sorted_bm = sorted(self.menubar_data[section][subsection], key=lambda x: getattr(x, 'label'))
                for bm in sorted_bm:
                    self.write_bm(bm)
                self.end_list()
            self.end_list()
        else:
            for bm in self.menubar_data[section]:
                self.write_bm(bm)

    def write_bm(self, bm: BookMark):
        """ write a single bookmark to output string
            :param bm: Bookmark to output
        """
        if 'icon' in bm.attrs:
            self.write(
                TheConfig.BOOKMARK_HTML_ICON_FORMAT.format(
                    bm.attrs['href'],
                    bm.attrs['add_date'],
                    bm.attrs['icon'],
                    bm.label
                )
            )
        else:
            self.write(
                TheConfig.BOOKMARK_HTML_FORMAT.format(
                    bm.attrs['href'],
                    bm.attrs['add_date'],
                    bm.label
                )
            )
        pass

    def write_heading(self, heading: str):
        """ write heading data to output string
            :param heading: heading text
        """
        self.write(TheConfig.HEADING_HTML_FORMAT.format(self.datestamp, self.datestamp, heading.title()))

    def write_toolbar_heading(self, heading: str):
        """ write heading data to output string
            :param heading: heading text
        """
        self.write(TheConfig.TOOLBAR_HTML_FORMAT.format(self.datestamp, self.datestamp, heading.title()))

    def begin_list(self):
        """ starts an HTML list and bumps the indent level """
        self.write(TheConfig.LIST_HTML)
        self.indent += 1

    def end_list(self):
        """ decrements the indent level and ends an HTML list """
        self.indent -= 1
        self.write(TheConfig.LIST_HTML_END)

    def write(self, html: Union[str, list]):
        """ write html to output string
            :param html: html string(s) to output, may be a list
        """
        if isinstance(html, list):
            for h in html:
                self.write(h)
            return
        self.output.append('    '*self.indent + html.strip())
        pass
