""" BookMarks Analysis module

The BookMarks Analysis module scans and categorizes bookmarks.

The various bookmark elements have already been determined during bookmark parsing.
Dictionaries are compiled for bookmark attributes, e.g. domains, host names, paths, etc.
A dictionary of keywords is compiled.
Duplicate bookmarks are detected and deleted.
"""

# System imports
from typing import Dict, List, Tuple

# Project imports
from config import TheConfig
from structures import BookMark, BookMarks, StructuresList as StructuresList
from logger import Logger
logger = Logger(name=__name__).logger

class Keywords:
    """ Keywords from bookmarks """

    def __init__(self):
        self.keyword_dict: Dict = {}

    def add_word(self, word, bookmark):
        if word == b'':
            return
        if word not in self.keyword_dict.keys():
            self.keyword_dict[word] = [bookmark]
        else:
            self.keyword_dict[word].append(bookmark)


class Analyze:
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

    def __init__(self, bookmarks: BookMarks):
        """ Analyze constructor """

        logger.info(f'INIT ({__name__})')

        self._bookmarks: BookMarks = bookmarks
        self.bookmarks: Dict[str, List] = bookmarks.bookmarks
        self.headings: Dict[str] = bookmarks.headings_dict
        self.schemes: List[str] = []
        self.hostnames: List[str] = []
        self.pathnames: Dict[str, List[str]] = {}
        self.domains: Dict[str, int] = {}
        self.subdomains: Dict[str, int] = {}
        self.domain_types: Dict[str, int] = {}
        self.duplicates: Dict[str, List[Tuple]] = {}
        self.deleted_bookmarks: List[str] = []
        self.empty_bookmarks: List[str] = []
        self.mobile_bookmarks: List[BookMark] = []
        self.processed_bookmarks: List = []
        self.file_bookmarks: Dict = {}
        self.keyword_database: Keywords = Keywords()
        self.href_database: Keywords = Keywords()
        self.localhost_bookmarks: Dict[str, Dict[str, List[BookMark]]] = {}
        self.pinboard: Dict = {}
        #: bookmarks that are speed dials in current input bookmarks file
        self.speed_dial_list_current: List[BookMark] = []
        #: bookmarks that are speed dials by current configuration
        self.speed_dial_list_config: List[BookMark] = []
        #: final dictionary of speed dials after all speed dial processing
        self.speed_dials: Dict[str, Dict[str, List[BookMark]]] = {}
        #: a local copy of 'TheConfig' for ease of debugging
        self.the_config = TheConfig
        #: populated as we discover various sites
        self.host_sites = {section: [] for section in TheConfig.sections}
        #: bookmark menubar, populated as we parse the various sections
        self.menubar_ = {section: {
            topic: [] for topic in TheConfig.sections[section].keys()
        } for section in TheConfig.sections}
        # bookmarks that appear at the head of the bookmark menubar
        self.menubar_['head']: List[BookMark] = []
        # bookmarks that appear at the tail (end) of the bookmark menubar
        self.menubar_['tail']: List[BookMark] = []

        self.scan_bookmarks()
        self.delete_empty_bookmarks()
        self.build_keyword_dictionary()

        # build a list of bookmark hosts for all sections
        self.scan_bookmark_hosts()

        # build a list of bookmarks that reference a localhost
        self.scan_bookmarks_localhosts()

        # build a list of bookmarks that reference a file
        self.scan_bookmarks_files()

        # build a list of speed-dials from current speed-dials
        self.scan_bookmarks_speed_dials_current()

        # build a list of speed-dials from all bookmarks based on config file
        self.scan_bookmarks_speed_dials_config()

        # scan bookmarks - head/tail items
        for site in TheConfig.menubar['head']:
            self.scan_bookmarks_site(site, self.menubar_['head'], head=True)
        for site in TheConfig.menubar['tail']:
            self.scan_bookmarks_site(site, self.menubar_['tail'], tail=True)

        # scan bookmarks in the order specified in the configuration file
        try:
            for section in TheConfig.scanning_order:
                if section not in self.menubar_.keys():
                    logger.info('Skipping empty section: %s', section)
                    continue
                for topic in self.menubar_[section].keys():
                    logger.debug('Scanning: %s/%s', section, topic)
                    config_list = TheConfig.sections[section][topic]
                    scan_list = self.menubar_[section][topic]
                    self.scan_bookmarks_section(config_list, scan_list)
                pass
        except Exception as e:
            logger.exception('UNHANDLED EXCEPTION', exc_info=e)

        # remove any mobile bookmarks if a desktop site exists
        mobile_bookmark_values = len(self.mobile_bookmarks)
        for mobile_index in range(mobile_bookmark_values, 0, -1):
            bm_mobile = self.mobile_bookmarks[mobile_index - 1]
            # break bookmark url into parts and remove any 'm'
            bm_mobile_parts = bm_mobile.href_urlparts.hostname.split('.')
            bm_desktop = '.'.join([bm_part for bm_part in bm_mobile_parts if bm_part != 'm'])
            # scan all bookmarks and check for a 'desktop' equivalent of the 'mobile' site
            for bm_desktop_key, bm_desktop_value in self.bookmarks.items():
                if not bm_desktop_value:
                    continue
                if mobile_index > len(self.mobile_bookmarks):
                    break
                # scan all bookmarks for bookmark desktop site
                bm_desktop_values = len(bm_desktop_value)
                for desktop_index in range(bm_desktop_values, 0, -1):
                    bm = bm_desktop_value[desktop_index - 1]
                    if bm.hostname == bm_desktop:
                        if bm.href_urlparts.hostname not in self.duplicates:
                            self.duplicates[bm.href_urlparts.hostname] = [(bm.href_urlparts.path, bm)]
                            del self.mobile_bookmarks[mobile_index - 1]
                            break
                        else:
                            self.duplicates[bm.href_urlparts.hostname].append((bm.href_urlparts.path, bm))
                            del self.mobile_bookmarks[mobile_index - 1]
                            break

        # add any unscanned bookmarks to the miscellaneous section
        self.menubar_['misc']['misc'] = []
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            for bm in bm_value:
                if not bm.scanned:
                    self.menubar_['misc']['misc'].append(bm)
                    bm.scanned = True

        self.delete_scanned_bookmarks()
        pass

    # =========================================================================
    def menubar(self):
        """ returns menubar constructed during analysis """
        return self.menubar_

    # =========================================================================
    def scan_bookmarks_speed_dials_config(self):
        """scan bookmarks for config designated speed-dials"""

        # scan speed-dials in the order specified in the configuration file
        try:
            for section in TheConfig.speed_dial_scan_order:
                if section not in self.menubar_.keys():
                    logger.info('Skipping empty section: %s', section)
                    continue
                for topic in self.menubar_[section].keys():
                    logger.debug('Scanning: %s/%s', section, topic)
                    config_list = TheConfig.sections[section][topic]
                    scan_list = self.menubar_[section][topic]
                    self.scan_bookmarks_section(config_list, scan_list)
        except Exception as e:
            logger.exception('UNHANDLED EXCEPTION', exc_info=e)
        pass

    # =========================================================================
    def scan_bookmarks_speed_dials_current(self):
        """scan bookmarks for current speed-dials"""
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all bookmarks for current value
            bm_values = len(bm_value)
            for i in range(bm_values, 0, -1):
                bm: BookMark = bm_value[i-1]
                if TheConfig.OPERA_SPEED_DIAL in bm.heading.label.lower():
                    if not isinstance(bm.heading.structures_list, StructuresList):
                        continue
                    self.speed_dial_list_current.extend(bm.heading.structures_list.list)
                pass
        pass

    # =========================================================================
    def scan_bookmarks_localhosts(self):
        """scan bookmarks for any with a local host identified in the config"""
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all bookmarks for current value
            bm_values = len(bm_value)
            for i in range(bm_values, 0, -1):
                bm = bm_value[i-1]
                if bm.hostname in TheConfig.local_hosts_by_ip.keys():
                    host_friendly_name = TheConfig.hostname_from_ip(bm.hostname)
                    bm.friendly_host_name = host_friendly_name
                    if host_friendly_name not in self.localhost_bookmarks.keys():
                        self.localhost_bookmarks[host_friendly_name] = {}
                    bm_key = self.bookmark_key(bm)
                    if bm_key not in self.localhost_bookmarks[host_friendly_name]:
                        self.localhost_bookmarks[host_friendly_name][bm_key] = [bm]
                    else:
                        bm_path = self.href_path(bm)
                        for bm_ in self.localhost_bookmarks[host_friendly_name][bm_key]:
                            if self.href_path(bm_) != bm_path:
                                self.localhost_bookmarks[host_friendly_name][bm_key].append(bm)
                    # bookmark has not been scanned, just noted as belonging to a local host
                    # bm.scanned = True

    # =========================================================================
    def scan_bookmarks_files(self):
        """ scan bookmarks for any with a 'file' scheme """
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all bookmarks for current value
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
                    bm.scanned = not TheConfig.allow_multiple(bm)

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
    def scan_bookmarks_site(self, site: Tuple[str, str, str], scan_list, head: bool = False, tail: bool = False):
        """Scan all bookmarks for site/section match

        Used when parsing the "head" and "tail" sections.

        :param site: Tuple[BookMark site to scan for [hostname, path, label]
        :param scan_list: Section/topic target scan list
        :param head: Boolean indicating we are parsing the BookMark's "head"
        :param tail: Boolean indicating we are parsinh the BookMark's "tail"
        """
        def parse_bm(_bm, _site_host) -> Tuple[str, str, str]:
            """Parse a BM and extract hostname, path and site_host

            :param _bm: BookMark being parsed
            :param _site_host: Site host
            :returns: Tuple[str:hostname, str:path, str:site_host]
            """
            # check for hostname match
            _hostname = _bm.href_urlparts.hostname
            if _hostname is not None:
                _hostname = _hostname.lower()
            _path = _bm.href_urlparts.path
            if _path is not None:
                _path = _path.lower()
            # check if a match for a localhost
            if TheConfig.is_local_host(bm=_bm):
                # substitute the local hostname
                _site_host = _hostname
            if len(_path) > 1 and _path.endswith('/'):
                _path = _path[:-1]
            return _hostname, _path, _site_host

        # get site parts
        site_host = site[0].lower()
        site_path = site[1].lower()
        site_label = site[2]
        if TheConfig.is_local_host(host=site_host):
            site_host = TheConfig.local_hosts_by_name[site_host]
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all bookmarks for current value
            for bm in bm_value:
                hostname, path, site_host = parse_bm(bm, site_host)

                logger.debug(f'BM: hostname:{hostname}  path:{path}  site_host:{site_host}')

                # only process 'bm' if not already scanned and hostname is not empty
                if bm.scanned or hostname is None or not len(hostname):
                    continue
                # if processing head/tail section then hostname must be a match
                if (head or tail) and hostname != site_host:
                    continue
                # if processing head/tail section and path is specified then it must match
                if (head or tail) and path is not None and path != site_path:
                    continue

                # okay to process this BM
                bm.label = site_label
                scan_list.append(bm)
                # always mark scanned when not parsing the "head" or "tail" sections
                bm.scanned = not (head or tail) and not TheConfig.allow_multiple(bm)

    # =========================================================================
    def scan_bookmarks_section(self, config_list, scan_list):
        """Scan all bookmarks for section match

            :param config_list: Section/topic configuration list to scan for
            :param scan_list: Section/topic target scan list
        """
        for bm_key, bm_value in self.bookmarks.items():
            if not bm_value:
                continue
            # scan all bookmarks for current value
            for bm in bm_value:
                if bm.scanned:
                    continue
                # check for hostname match
                hostname = bm.href_urlparts.hostname.lower()
                if hostname is not None and len(hostname):
                    for item in config_list:
                        item_url_parts = item.split('/')
                        config_item_hostname = item_url_parts[0]
                        config_item_path = '/'
                        if len(item_url_parts) > 1:
                            config_item_path += '/'.join(item_url_parts[1:])
                        if config_item_hostname in hostname and \
                                bm.href_urlparts.path.lower().startswith(config_item_path) and \
                                hostname not in scan_list:
                            scan_list.append(bm)
                            bm.scanned = not TheConfig.allow_multiple(bm)
                            break
                # check for label match
                label = bm.label.lower()
                if not bm.scanned and label is not None and len(label):
                    for item in config_list:
                        if item in label and label not in scan_list:
                            scan_list.append(bm)
                            bm.scanned = not TheConfig.allow_multiple(bm)
                            break

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
                        # see if this is a site optimized for mobile
                        if 'm' in parts and bm not in self.mobile_bookmarks:
                            self.mobile_bookmarks.append(bm)

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
                    del bm_value[i-1]
                else:
                    self.duplicates[bm.href_urlparts.hostname].append((bm.href_urlparts.path, bm))
                    del bm_value[i-1]

            # see if all bookmarks for this list were deleted
            if not len(self.bookmarks[bm_key]):
                self.empty_bookmarks.append(bm_key)

    # =========================================================================
    def delete_empty_bookmarks(self):
        """ delete any empty bookmarks """
        for bm_key in self.empty_bookmarks:
            logger.info(f'Deleting {logger.clean(bm_key)}')
            if bm_key not in self.deleted_bookmarks:
                self.deleted_bookmarks.append(bm_key)
            del self.bookmarks[bm_key]

    # =========================================================================
    def build_keyword_dictionary(self):
        """ build keywords dictionary """
        for bm_key, bm_value in self.bookmarks.items():
            for bm in bm_value:
                self.add_keywords(bm)
                self.add_href_parts(bm)

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
                                logger.debug(f'{section}: {host}/{hostname}')
