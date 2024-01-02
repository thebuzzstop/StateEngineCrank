""" BookMarks Reformat module

The BookMarks reformat module reorders and reorganizes the bookmarks.

"""

# System imports
import datetime
from typing import List, Union

# Project imports
from analyze import Analyze
from config import TheConfig
from defines import UrlType
from structures import BookMark
from exceptions import MyException
from verify_urls import VerifyUrls, BadUrlStatus

from logger import Logger
logger = Logger(name=__name__).logger

class Reformat:
    """ Class to reformat bookmarks """

    def __init__(self):
        """ Reformat constructor"""
        logger.info('INIT (%s)', __name__)

        self.headings = TheConfig.headings                  #: users headings configuration
        self.menubar_spec = TheConfig.menubar               #: user menubar configuration
        self.menubar_data = Analyze.menubar_bookmarks()     #: menubar scanned data
        self.indent = 0                                     #: level to indent
        self._output: List[str] = [TheConfig.HEADER_HTML]   #: start with bookmarks file header

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

    @property
    def output(self) -> List[str]:
        """HTML output"""
        return self._output

    def write_section(self, section):
        """ write entire section to output string

            :param section: bookmarks section to output
        """
        # see if current section has a heading
        if section in self.headings:
            self.write_heading(section)
            self.begin_list()
            deferred = []
            # process each subsection in the current menubar section
            if section == 'speed-dials':
                subsection_list = TheConfig.speed_dial_output_order
            else:
                subsection_list = sorted(self.menubar_spec[section])

            for subsection in subsection_list:
                # add to deferred list if subsection does not have a heading
                if not self.has_heading(section, subsection):
                    deferred.append(subsection)
                    continue
                # create a heading and start a list for this subsection
                self.write_heading(subsection)
                self.begin_list()
                self.output_subsection(section, subsection)
                self.end_list()
            # output any subsection(s) that were deferred
            for subsection in deferred:
                self.output_subsection(section, subsection)
            self.end_list()
        else:
            for bm in self.menubar_data[section]:
                self.write_bm(bm)

    def output_subsection(self, section, subsection):
        """ output bookmarks for section.subsection

            Special case processing for *www* section.

            :param section: Active section name
            :param subsection: Active subsection name
        """
        # special case of 'www' section
        if section == 'www':
            if subsection == 'hosts':
                # create a list of all hosts (domains)
                sorted_list = sorted(Analyze.domains())
            elif subsection == 'types':
                # create a list of all host sites
                sorted_list = sorted(Analyze.domain_types())
            elif subsection == 'protocols':
                # create a list of protocols
                sorted_list = sorted(Analyze.schemes())
            elif subsection == 'bad_hosts':
                # create a list of bad hosts
                sorted_list = sorted(VerifyUrls.bad_hostnames())
            elif subsection == 'bad_dns':
                # create a list of bad hosts - DNS entries
                sorted_list = sorted(VerifyUrls.bad_hostnames_dns())
            elif subsection == 'bad_ping':
                # create a list of bad hosts - PING entries
                sorted_list = sorted(VerifyUrls.bad_hostnames_ping())
            elif subsection == 'bad_urls':
                # create a list of bad URL's
                bad_url_list: List[str] = []
                for bad_urls_key in list(VerifyUrls.bad_urls_dict().keys()):
                    bad_url_status_list: List[BadUrlStatus] = VerifyUrls.bad_urls_dict()[bad_urls_key]
                    if bad_urls_key == UrlType.HOSTNAME:
                        bad_url_list.extend([bad_url.hostname for bad_url in bad_url_status_list])
                    else:
                        bad_url_list.extend([bad_url.url for bad_url in bad_url_status_list])
                sorted_list = sorted(bad_url_list)
                pass

            else:
                raise ValueError('Unknown subsection: %s', subsection)
            # write out sorted list
            # :FixMe: Writing 'www' section is broken, subsections are empty
            for item in sorted_list:
                text = TheConfig.LIST_HTML_TEXT_FORMAT.format(item)
                self._output.append('    ' * self.indent + text)
        else:
            # create sorted list of section/subsection bookmarks
            sorted_bm = sorted(self.menubar_data[section][subsection],
                               key=lambda x: (getattr(x, 'label').lower(), getattr(x, 'hostname'), getattr(x, 'path')))
            # write sorted bookmarks
            for bm in sorted_bm:
                self.write_bm(bm)

    @staticmethod
    def has_heading(section, subsection):
        """ function to determine if subsection has a heading

            :param section: Active section name
            :param subsection: Active subsection name
            :return: True if section.subsection has a heading
        """
        return f'{section}.{subsection}' not in TheConfig.noheadings

    def write_bm(self, bm: BookMark, has_label=True):
        """ write a single bookmark to output string

            :param bm: Bookmark to output
            :param has_label: Bookmark has a label
        """
        if has_label:
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
        else:
            if 'icon' in bm.attrs:
                self.write(
                    TheConfig.BOOKMARK_HTML_ICON_FORMAT_NO_LABEL.format(
                        bm.attrs['href'],
                        bm.attrs['add_date'],
                        bm.attrs['icon']
                    )
                )
            else:
                raise MyException("Can't output BM with no LABEL and no ICON")
        pass

    def write_heading(self, heading: str):
        """ write heading data to output string

            :param heading: heading text
        """
        self.write(TheConfig.HEADING_HTML_FORMAT.format(self.datestamp, self.datestamp, self.my_title(heading)))

    def write_toolbar_heading(self, heading: str):
        """ write heading data to output string

            :param heading: heading text
        """
        self.write(TheConfig.TOOLBAR_HTML_FORMAT.format(self.datestamp, self.datestamp, self.my_title(heading)))

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
        self._output.append('    '*self.indent + html.strip())
        pass

    @staticmethod
    def my_title(heading):
        """ format a heading string the way we like it

            :param heading: Heading string to format
            :return: Heading formatted as we like it
        """
        heading = heading.title()
        for original, replacement in TheConfig.capitalized:
            heading = str.replace(heading, original, replacement)
        return heading
