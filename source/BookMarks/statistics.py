""" BookMarks Statistics module

The BookMarks Statistics module performs calculations on the bookmarks::

 + Protocols
 + Domains
 + Subdomains
 + Headings

"""

# System imports
import re
from urllib.parse import urlparse

# Project imports
import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class Statistics(object):

    DOMAIN_RE = re.compile(r"([a-zA-Z0-9]+\.[a-zA-Z0-9]+)$")

    def __init__(self, bookmarks, headings_labels, headings_dict):
        """ Statistics constructor """
        self.bookmarks = bookmarks
        self.schemes = []
        self.hosts = []
        self.domains = []
        self.subdomains = []

        # process all bookmarks
        for bm_key, bm_value in bookmarks.items():
            for bm in bm_value:
                url_parts = urlparse(bm.attrs['href'])
                if url_parts.scheme and not url_parts.scheme in self.schemes:
                    self.schemes.append(url_parts.scheme)
                if url_parts.hostname and not url_parts.hostname in self.hosts:
                    self.hosts.append(url_parts.hostname)
                groups = self.DOMAIN_RE
                domain = self.DOMAIN_RE.match(url_parts.hostname)
                pass
