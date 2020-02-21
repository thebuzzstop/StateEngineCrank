""" BookMarks Analysis module

The BookMarks Analysis module scans and categorizes bookmarks.

The various bookmark elements have already been determined during bookmark parsing.
Dictionaries are compiled for bookmark attributes, e.g. domains, host names, paths, etc.
A of keywords is compiled.
Duplicate bookmarks are detected and deleted.

"""

# System imports
import re

# Project imports
from BookMarks.config import TheConfig
from BookMarks.structures import BookMark

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


class Analyze(object):
    """ Class to analyze and categorize bookmarks """

    #: hex representations to convert to chars
    hex2char = [
        ('%20', ' '), ('%21', '!'), ('%22', '"'), ('%23', '#'),
        ('%24', '$'), ('%25', '%'), ('%26', '&'), ('%27', "'"),
        ('%28', '('), ('%29', ')'), ('%2A', '*'), ('%2B', '+'),
        ('%2C', ','), ('%2D', '-'), ('%2E', '.'), ('%2F', '/'),
        ('%3A', ':'), ('%3B', ';'), ('%3C', '<'), ('%3D', '='),
        ('%3E', '>'), ('%3F', '?'), ('%40', '@')
    ]

    #: characters to strip from strings when parsing
    strip_chars = '~!@#$%^&*()_+-=`:;<>,.?/[]{}|"\"\\'

    def __init__(self, bookmarks):
        """ Analyze constructor """
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
        self.processed_bookmarks = []
        self.file_bookmarks = {}
        self.keyword_database = Keywords()
        self.href_database = Keywords()
        #: restricted section.topic values
        self.restricted_hosts = TheConfig.restricted_hosts
        self.restricted_text = TheConfig.restricted_text

        #: a local copy of 'TheConfig' for ease of debugging
        self.the_config = TheConfig

        #: populated as we discover various sites
        self.host_sites = {section: [] for section in TheConfig.sections}

        #: bookmark menubar, populated as we parse the various sections
        self.menubar_ = {section: {
            topic: [] for topic in TheConfig.sections[section].keys()
        } for section in TheConfig.sections}
        # bookmarks that appear at the head of the bookmark menubar
        self.menubar_['head'] = []
        # bookmarks that appear at the tail (end) of the bookmark menubar
        self.menubar_['tail'] = []

        self.scan_bookmarks()
        self.delete_empty_bookmarks()
        self.build_keyword_dictionary()

        # build a list of bookmark hosts for all of the sections
        self.scan_bookmark_hosts()

        # build a list of bookmarks that reference a file
        self.scan_bookmarks_files()

        # scan bookmarks - head/tail items
        for site in TheConfig.menubar['head']:
            self.scan_bookmarks_site(site, self.menubar_['head'])
        for site in TheConfig.menubar['tail']:
            self.scan_bookmarks_site(site, self.menubar_['tail'])

        # scan bookmarks in the order specified in the configuration file
        for section in TheConfig.scanning_order:
            for topic in self.menubar_[section].keys():
                logger.logger.debug(f'Scanning: {section}/{topic}')
                config_list = TheConfig.sections[section][topic]
                scan_list = self.menubar_[section][topic]
                section_topic = f'{section}.{topic}'
                self.scan_bookmarks_section(config_list, scan_list, section_topic)
            pass

        # add any unscanned bookmarks to the miscellaneous section
        self.menubar_['misc']['misc'] = []
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            for bm in bm_value:
                if not bm.scanned:
                    self.menubar_['misc']['misc'].append(bm)
                    bm.scanned = True
                    bm.match = BookMark.BookMarkMatch.eMISC

        self.delete_empty_icons()
        self.delete_empty_attrs()
        self.delete_scanned_bookmarks()
        pass

    # =========================================================================
    def menubar(self):
        """ returns menubar constructed during analysis """
        return self.menubar_

    # =========================================================================
    def scan_bookmarks_files(self):
        """ scan bookmarks for any with a 'file' scheme """
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all book marks for current value
            bm_values = len(bm_value)
            for i in range(bm_values, 0, -1):
                bm = bm_value[i-1]
                if bm.href_urlparts.scheme == 'file':
                    bm_key = self.bookmark_key(bm)
                    if bm_key not in self.file_bookmarks:
                        self.file_bookmarks[bm_key] = [bm]
                    else:
                        bm_path = self.href_path(bm)
                        for bm_ in self.file_bookmarks[bm_key]:
                            if self.href_path(bm_) != bm_path:
                                self.file_bookmarks[bm_key].append(bm)
                    bm.scanned = True
                    bm.match = BookMark.BookMarkMatch.eFILE

        pass

    @staticmethod
    def href_path(bookmark):
        """ Returns the href path for given bookmark

            :param bookmark: bookmark to process
            :return: path component for given href
        """
        return bookmark.href_urlparts.path

    @staticmethod
    def bookmark_key(bookmark):
        """ Returns a bookmark key

            :param bookmark: bookmark for which to generate a key
            :return: bookmark key
        """
        return f'{bookmark.heading.label}'

    # =========================================================================
    def scan_bookmarks_site(self, site: str, scan_list):
        """ scan all bookmarks for section match

            :param site: BookMark site to scan for
            :param scan_list: Section/topic target scan list
        """
        site_ = site.lower()
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all book marks for current value
            for bm in bm_value:
                # check for hostname match
                hostname = bm.href_urlparts.hostname
                if hostname is not None:
                    hostname = hostname.lower()
                path = bm.href_urlparts.path.lower()
                if not bm.scanned:
                    if hostname is not None and len(hostname):
                        # if hostname.endswith(site_) and path == '/':
                        if self.re_str_check(site_, hostname+path):
                            scan_list.append(bm)
                            bm.scanned = True
                            bm.match = BookMark.BookMarkMatch.eSITE
                pass

    # =========================================================================
    def scan_bookmarks_section(self, config_list, scan_list, section_topic):
        """ scan all bookmarks for section match

            :param config_list: Section/topic configuration list to scan for
            :param scan_list: Section/topic target scan list
            :param section_topic: Section/topic string
        """
        # scan all book marks - check for hostname match
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all book marks
            for bm in bm_value:
                # continue if already scanned
                if bm.scanned:
                    continue

                # check for restrictions
                hostname = bm.href_urlparts.hostname.lower()
                label = bm.label.lower()
                if self.is_restricted(hostname, label, section_topic):
                    continue

                if label.startswith('protocol buffer') and section_topic == 'soa.soa':
                    print('hello, sailor')

                # check for a hostname match
                if not bm.scanned and hostname is not None and len(hostname):
                    for item in config_list:
                        if item in hostname and hostname not in scan_list:
                            scan_list.append(bm)
                            bm.scanned = True
                            bm.match = BookMark.BookMarkMatch.eHOSTNAME
                            break

                # check for a label match
                if not bm.scanned and label is not None and len(label):
                    for item in config_list:
                        check = self.re_str_check(item, label)
                        scanlist = self.re_str_check(label, scan_list)
                        if self.re_str_check(item, label) and label not in scan_list:
                            scan_list.append(bm)
                            bm.scanned = True
                            bm.match = BookMark.BookMarkMatch.eLABEL
                            break

                # check for a path match
                path = bm.href_urlparts.path.lower()
                if not bm.scanned and path is not None and len(path):
                    for item in config_list:
                        if item in path and path not in scan_list:
                            scan_list.append(bm)
                            bm.scanned = True
                            bm.match = BookMark.BookMarkMatch.ePATH
                            break
        pass

    def is_restricted(self, bm_hostname, bm_label, section_topic):
        """ See if bookmark hostname is restricted

            :param bm_hostname: Bookmark hostname
            :param bm_label: Bookmark label
            :param section_topic: Section/Topic being processed
            :return: Boolean True if hostname matches a section/topic restriction
        """
        # check for a match with a restricted host
        restricted_host = None
        for host in self.restricted_hosts:
            if re.search(bm_hostname, host, re.IGNORECASE):
                restricted_host = host
                break
        # check for a match with restricted text
        restricted_text = None
        bm_text = ''.join(c for c in bm_label if c.isalnum() or c == '.')
        if bm_text:
            for text in self.restricted_text:
                if re.search(text, bm_text, re.IGNORECASE):
                    restricted_text = text
                    break

        if not restricted_host and not restricted_text:
            return False
        if restricted_host and self.restricted_hosts[restricted_host] == section_topic:
            return False
        if restricted_text and self.restricted_text[restricted_text] == section_topic:
            return False
        if restricted_host and self.restricted_hosts[restricted_host] != section_topic:
            return True
        if restricted_text and self.restricted_text[restricted_text] != section_topic:
            return True
        raise Exception(f'Unhandled logic condition: HOST[{restricted_host}] TEXT[{restricted_text}] TOPIC[{section_topic}]')

    # =========================================================================
    def scan_bookmark_hosts(self):
        """ scan all bookmarks for known previously identified hostnames """
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            for bm in bm_value:
                hostname = bm.href_urlparts.hostname
                if not hostname:
                    continue
                hostname = hostname.lower()
                # loop through all menubar sections
                for section in TheConfig.sections:
                    for key in TheConfig.sections[section].keys():
                        for host in TheConfig.sections[section][key]:
                            if host in hostname and hostname not in self.host_sites[section]:
                                self.host_sites[section].append(hostname)
                                logger.logger.debug(f'{section}: {host}/{hostname}')
        pass

    # =========================================================================
    def scan_bookmarks(self):
        """ scan all bookmarks and categorize """
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
                # strip any trailing slash from path before processing
                path = bm.href_urlparts.path.rstrip('/')
                if bm.href_urlparts.hostname not in self.pathnames.keys():
                    self.pathnames[bm.href_urlparts.hostname] = [path]
                elif path not in self.pathnames[bm.href_urlparts.hostname]:
                    self.pathnames[bm.href_urlparts.hostname].append(path)
                elif bm.href_urlparts.hostname not in self.duplicates:
                    self.duplicates[bm.href_urlparts.hostname] = [(path, bm)]
                    del bm_value[i-1]
                else:
                    self.duplicates[bm.href_urlparts.hostname].append((path, bm))
                    del bm_value[i-1]

            # see if all bookmarks for this list were deleted
            if not len(self.bookmarks[bm_key]):
                self.empty_bookmarks.append(bm_key)
        pass

    # =========================================================================
    def delete_scanned_bookmarks(self):
        """ rescan bookmarks and delete any that were identified (e.g. projects, personal) """
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all book marks for current value
            bm_values = len(bm_value)
            for i in range(bm_values, 0, -1):
                bm = bm_value[i-1]
                if bm.scanned:
                    del bm_value[i-1]
            # see if any bookmarks remain for this key
            if not len(bm_value):
                self.processed_bookmarks.append(bm_key)
        # delete all bookmarks marked 'scanned'
        for bm_key in self.processed_bookmarks:
            if bm_key in self.bookmarks:
                del self.bookmarks[bm_key]
        pass

    # =========================================================================
    def delete_empty_bookmarks(self):
        """ delete any empty bookmarks """
        for bm_key in self.empty_bookmarks:
            logger.logger.info(f'Deleting {logger.clean(bm_key)}')
            if bm_key not in self.deleted_bookmarks:
                self.deleted_bookmarks.append(bm_key)
            del self.bookmarks[bm_key]
        pass

    # =========================================================================
    def delete_empty_icons(self):
        """ delete any icons that are 'None' """
        for bm_key, bm_value in self.bookmarks.items():
            for bm in bm_value:
                if not bm.attrs['icon']:
                    del bm.attrs['icon']
        pass

    # =========================================================================
    def delete_empty_attrs(self):
        """ delete any attrs[] that are empty """
        for bm_key, bm_value in self.bookmarks.items():
            for bm in bm_value:
                if not bm.attrs['attrs']:
                    del bm.attrs['attrs']
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

    def re_str_check(self, pattern: str, strings: [list, str, BookMark]):
        """ Perform regular expression scan of a list

            :param pattern: string pattern to search for
            :param strings: BookMark, string or list of strings to scan
            :return: boolean True if 'pattern' is in 'strings'
        """
        try:
            if isinstance(strings, str):
                return re.compile(pattern, re.IGNORECASE).search(strings)
            elif isinstance(strings, list):
                if not strings:
                    return False
                if isinstance(strings[0], BookMark):
                    bm_list_strings = []
                    for bm in strings:
                        bm_list_strings.extend(bm.strings())
                    return self.re_str_check(pattern, bm_list_strings)
            elif isinstance(strings, BookMark):
                return self.re_str_check(pattern, strings.strings())

            pattern_re = re.compile(pattern, re.IGNORECASE)
            for s in strings:
                if pattern_re.search(s):
                    return True
            return False
        except Exception as e:
            print(f'Oops: {e}')
            return False
