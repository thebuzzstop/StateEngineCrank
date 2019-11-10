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
from config import TheConfig

import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class Reformat(object):
    """ Class to reformat bookmarks """

    def __init__(self, analysis: Analyze):
        """ Analyze constructor """
        self.analysis = analysis
        self.headings = TheConfig().headings

        self.create_template()
        self.populate_template()

        pass

    def create_template(self):
        """ Output bookmarks template based on configuration """
        pass

    def populate_template(self):
        """ Populate template with analysis data """
        pass
