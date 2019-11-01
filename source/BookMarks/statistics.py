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

    def __init__(self, bookmarks, headings_labels, headings_dict):
        """ Statistics constructor """
        self.bookmarks = bookmarks
        self.schemes = []
        self.hostnames = []
        self.pathnames = {}
        self.domains = {}
        self.subdomains = {}
        self.domain_types = {}
        self.duplicates = {}

        # process all bookmarks
        for bm_key, bm_value in bookmarks.items():
            for bm in bm_value:
                url_parts = urlparse(bm.attrs['href'])

                # ============================================
                # scheme (http, https, etc)
                # ============================================
                if url_parts.scheme and not url_parts.scheme in self.schemes:
                    self.schemes.append(url_parts.scheme)

                # ============================================
                # hostnames (target pages)
                # ============================================
                if url_parts.hostname and url_parts.hostname not in self.hostnames:
                    self.hostnames.append(url_parts.hostname)

                    # primary domains
                    parts = url_parts.hostname.split('.')
                    if len(parts) >= 1:
                        dom = parts[-1]
                        if dom not in self.domain_types:
                            self.domain_types[dom] = 1
                        else:
                            self.domain_types[dom] += 1

                    # sub-domains (primary)
                    if len(parts) >= 2:
                        dom = f'{parts[-2]}.{parts[-1]}'
                        if dom not in self.domains:
                            self.domains[dom] = 1
                        else:
                            self.domains[dom] += 1

                    # sub-domains (secondary)
                    if len(parts) >= 3 and parts[-3] != 'www':
                        dom = f'{parts[-3]}.{parts[-2]}.{parts[-1]}'
                        if dom not in self.subdomains:
                            self.subdomains[dom] = 1
                        else:
                            self.subdomains[dom] += 1

                # ============================================
                # check for duplicates
                # ============================================
                if not (url_parts.hostname and url_parts.path):
                    continue
                if url_parts.hostname not in self.pathnames.keys():
                    self.pathnames[url_parts.hostname] = [url_parts.path]
                elif url_parts.path not in self.pathnames[url_parts.hostname]:
                    self.pathnames[url_parts.hostname].append(url_parts.path)
                else:
                    self.duplicates[url_parts.hostname] = [url_parts.path]

        pass
