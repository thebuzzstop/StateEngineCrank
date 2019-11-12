""" BookMarks Reformat module

The BookMarks reformat module reorders and reorganizes the bookmarks::

 + Protocols
 + Domains
 + Subdomains
 + Headings

"""

# System imports
import typing

# Project imports
from analyze import Analyze
from structures import HeadingLabels

from config import TheConfig

import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class Reformat(object):
    """ Class to reformat bookmarks """

    def __init__(self, analysis: Analyze, headings_data: dict):
        """ Analyze constructor

            :param analysis: Analize object after processing
            :param headings_data: Dictionary of headings data
        """
        self.analysis = analysis
        self.headings_dict = headings_data['dict']
        self.headings_labels = headings_data['labels']
        self.headings_dups = headings_data['dups']

        self.headings = TheConfig.headings  #: users headings configuration
        self.menubar = TheConfig.menubar    #: user menubar configuration
        self.output = None

        self.scan_bookmarks()
        pass

    def scan_bookmarks(self):
        """ Scan bookmarks database and match with headings & topics """
        pass
