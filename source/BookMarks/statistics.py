""" BookMarks Statistics module

The BookMarks Statistics module performs calculations on the bookmarks::

 + Protocols
 + Domains
 + Subdomains
 + Headings

"""

# System imports

# Project imports
import logger
logger = logger.Logger(__name__)
my_logger = logger.logger


class Keywords(object):
    """ Keywords from bookmarks """

    def __init__(self):
        self.keywords = {}

    def add_word(self, word, bookmark):
        if word == b'':
            return
        if word not in self.keywords:
            self.keywords[word] = [bookmark]
        else:
            self.keywords[word].append(bookmark)


class Statistics(object):
    """ Class to gather statistics on bookmarks """

    #: hex representations to convert to chars
    hex2char = [
        ('%20', ' '), ('%21', '!'), ('%22', '"'), ('%23', '#'),
        ('%24', '$'), ('%25', '%'), ('%26', '&'), ('%27', "'"),
        ('%28', '('), ('%29', ')'), ('%2A', '*'), ('%2B', '+'),
        ('%2C', ','), ('%2D', '-'), ('%2E', '.'), ('%2F', '/'),
        ('%3A', ':'), ('%3B', ';'), ('%3C', '<'), ('%3D', '='),
        ('%3E', '>'), ('%3F', '?'), ('%40', '@')
    ]

    #: characters to strip from strings when gathering statistics
    strip_chars = '~!@#$%^&*()_+-=`:;<>,.?/[]{}|"\"\\'

    def __init__(self, bookmarks):
        """ Statistics constructor """
        self.bookmarks = bookmarks
        self.schemes = []
        self.hostnames = []
        self.pathnames = {}
        self.domains = {}
        self.subdomains = {}
        self.domain_types = {}
        self.duplicates = {}
        self.deleted_bookmarks = []
        self.empty_bookmarks = []

        self.keyword_database = Keywords()
        self.href_database = Keywords()

        self.scan_bookmarks()
        self.delete_empty_bookmarks()
        self.build_keyword_dictionary()
        pass

    # =========================================================================
    def scan_bookmarks(self):
        """ scan all bookmarks, gather some statistics """
        for bm_key, bm_value in self.bookmarks.items():
            bm_values = len(bm_value)
            for i in range(bm_values, 0, -1):
                bm = bm_value[i-1]

                # ============================================
                # scheme (http, https, etc)
                # ============================================
                if bm.href_urlparts.scheme and bm.href_urlparts.scheme not in self.schemes:
                    self.schemes.append(bm.href_urlparts.scheme)

                # ============================================
                # hostnames (target pages)
                # ============================================
                if bm.href_urlparts.hostname and bm.href_urlparts.hostname not in self.hostnames:
                    self.hostnames.append(bm.href_urlparts.hostname)

                    # primary domains
                    parts = bm.href_urlparts.hostname.split('.')
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
                # delete any duplicates
                # ============================================
                if not (bm.href_urlparts.hostname and bm.href_urlparts.path):
                    continue
                if bm.href_urlparts.hostname not in self.pathnames.keys():
                    self.pathnames[bm.href_urlparts.hostname] = [bm.href_urlparts.path]
                elif bm.href_urlparts.path not in self.pathnames[bm.href_urlparts.hostname]:
                    self.pathnames[bm.href_urlparts.hostname].append(bm.href_urlparts.path)
                elif bm.href_urlparts.hostname not in self.duplicates:
                    self.duplicates[bm.href_urlparts.hostname] = [(bm.href_urlparts.path, bm)]
                    if len(bm_value) == 1:
                        pass
                    del bm_value[i-1]
                else:
                    self.duplicates[bm.href_urlparts.hostname].append((bm.href_urlparts.path, bm))
                    if len(bm_value) == 1:
                        pass
                    del bm_value[i-1]

            # see if all bookmarks for this list were deleted
            if not len(self.bookmarks[bm_key]):
                self.empty_bookmarks.append(bm_key)
        pass

    # =========================================================================
    def delete_empty_bookmarks(self):
        """ delete any empty bookmarks """
        for bm_key in self.empty_bookmarks:
            logger.logger.info(f'Deleting {bm_key}')
            if bm_key not in self.deleted_bookmarks:
                self.deleted_bookmarks.append(bm_key)
            del self.bookmarks[bm_key]
        pass

    # =========================================================================
    def build_keyword_dictionary(self):
        """ build keywords dictionary """
        for bm_key, bm_value in self.bookmarks.items():
            for bm in bm_value:
                self.add_keywords(bm)
                self.add_href_parts(bm)
        pass

    # =========================================================================
    def add_keywords(self, bookmark):
        """ Add bookmark text to dictionary
            :param bookmark: Bookmark associated with text
        """
        text = bookmark.label
        for ch in self.strip_chars:
            text = text.replace(ch, ' ')
        for word in text.split(' '):
            if word:
                self.keyword_database.add_word(word, bookmark)

    # =========================================================================
    def add_href_parts(self, bookmark):
        """ Add link parts to dictionary
            :param bookmark: Bookmark associated with link
        """
        if not bookmark.attrs['href']:
            return
        # href parts that go into the database
        href_parts = [
            bookmark.href_urlparts.scheme,
            bookmark.href_urlparts.hostname,
            bookmark.href_urlparts.path,
            bookmark.href_urlparts.port,
        ]
        # process all bookmark href parts
        for parts in href_parts:
            if not parts:
                continue
            if isinstance(parts, int):
                parts = f'{parts}'
            # convert hex encodings to chars
            for hx, ch in self.hex2char:
                parts = parts.replace(hx, ch)
            # strip special characters
            for ch in self.strip_chars:
                parts = parts.replace(ch, ' ')
            # split into the parts and add to the database
            for part in parts.split(' '):
                if len(part):
                    self.href_database.add_word(part, bookmark)
