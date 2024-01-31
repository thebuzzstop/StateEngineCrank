"""BookMarks Configuration Data - TheConfig"""

# Sustem imports
from typing import Dict, List, Tuple
import logging

# Project imports
import localhost

class TheConfig:
    """Global Configuration Data

    Contents are::

       + configuration constants
       + configuration file settings
       + command line switches
    """

    HEADER_HTML = [
        '<!DOCTYPE NETSCAPE-Bookmark-file-1>',
        '<!-- This is an automatically generated file.',
        'It will be read and overwritten.',
        'DO NOT EDIT! -->',
        '<META HTTP - EQUIV = "Content-Type" CONTENT = "text/html; charset=UTF-8">',
        '<TITLE>Bookmarks</TITLE>',
        '<H1>Bookmarks</H1>',
    ]
    LIST_HTML = '<DL><p>'
    LIST_HTML_END = '</DL><p>'
    TOOLBAR_HTML_FORMAT = '<DT><H2 ADD_DATE="{0}" LAST_MODIFIED="{1}" PERSONAL_TOOLBAR_FOLDER="true">{2}</H2>'
    HEADING_HTML_FORMAT = '<DT><H3 ADD_DATE="{0}" LAST_MODIFIED="{1}">{2}</H3>'
    BOOKMARK_HTML_FORMAT = '<DT><A HREF="{0}" ADD_DATE="{1}">{2}</A>'
    BOOKMARK_HTML_ICON_FORMAT = '<DT><A HREF="{0}" ADD_DATE="{1}" ICON="{2}">{3}</A>'
    BOOKMARK_HTML_ICON_FORMAT_NO_LABEL = '<DT><A HREF="{0}" ADD_DATE="{1}" ICON="{2}"></A>'
    BOOKMARK_HTML_TEXT_FORMAT = '<DT><A HREF="{0}">{1}</A>'
    LIST_HTML_TEXT_FORMAT = '<DT>{0}'
    LIST_HTML_LINK_FORMAT = '<DT><A HREF="{0}">{0}</A>'
    NO_SECTION_HEADING = {
        'reference': 'reference',
        'projects': 'sites',
        'ford': 'sites',
        'personal': 'sites',
        'tools': 'tools',
        'misc': 'misc',
    }

    # global configuration variables initialized to default values
    LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

    #: Text used to search for Opera SpeedDial bookmarks
    #: Text being searched must be forced to lowercase
    OPERA_SPEED_DIAL: str = 'speeddial'

    # configuration items initialized by config parser
    # :todo: add type hints
    config = None                       #: configuration items
    headings = None                     #: headings declared in config_ford.ini
    noheadings = None                   #: section.subsection combinations not to have a heading
    menubar = None                      #: menubar constructed by config parser
    scanning_order = None               #: order in which scanning processing will occur
    speed_dial_scan_order = None        #: order to scan speed-dials
    speed_dial_output_order = None      #: order to output speed-dials
    sections = None                     #: menutab sections (topic groups)
    head = None                         #: menutab 'head' section
    tail = None                         #: menutab 'tail' section
    capitalized = None                  #: menubar capitalized label words
    config_file = None                  #: configuration file to be read
    input_file = None                   #: bookmarks input file to be processed
    output_file = None                  #: bookmarks output file (after processing)
    debug: bool = False                 #: True/False - debug output enabled
    test_mode: bool = False             #: True/False - test mode enabled
    http2https: bool = False            #: True/False - convert HTTP to HTTPS when possible
    verbosity: bool = False             #: True/False - verbose output enabled
    verbosity_level: int = 0            #: verbosity level
    verify_urls: bool = False           #: verify URL's are reachable as they are processed
    verify_prune: bool = False          #: prune bad URL's and bookmarks
    prune_bad_dns: bool = False         #: prune bookmarks with bad DNS entries
    request_get_timeout: float = 0.5    #: default timeout for verifying URL's

    #: should return local ip-address, e.g. '192.168.1.101'
    my_ip_address: str = localhost.get_ip()
    #: should return local hostname, e.g. 'mark-linux'
    my_hostname: str = localhost.get_hostname()

    #: specific local hosts (private network) - key == name
    local_hosts_by_name: Dict[str, str] = {}

    #: specific local hosts (private network) - key == ip
    local_hosts_by_ip: Dict[str, str] = {}

    #: host bookmarks for which multiple entries are allowed
    allow_multiple_bookmarks: List[Tuple[str, str]] = []

    #: bad hosts ping cache file
    bad_hosts_ping_cache_file: str = 'bad_hosts_ping.cache'
    #: bad hosts dns-lookup cache file
    bad_hosts_dns_cache_file: str = 'bad_hosts_dns.cache'
    #: use bad hosts cache file - set True with command line switch
    use_bad_hosts_cache: bool = False
    #: bad URL's cache file
    bad_urls_cache_file: str = 'bad_urls.cache'
    #: use bad URL's cache file - set True with command line switch
    use_bad_urls_cache: bool = False

    @classmethod
    def hostname_from_ip(cls, host_ip: str) -> str:
        """Returns host name from local-hosts

        :param host_ip: Local host IP to lookup
        :returns: Local host name (empty string if not found)
        """
        if host_ip in cls.local_hosts_by_ip.keys():
            return cls.local_hosts_by_ip[host_ip]
        return ''

    @classmethod
    def hostip_from_name(cls, host_name: str) -> str:
        """Returns host ip from local-hosts

        :param host_name: Local host name to lookup
        :returns: Local host ip (empty string if not found)
        """
        if host_name in cls.local_hosts_by_name.keys():
            return cls.local_hosts_by_name[host_name]
        return ''


    @staticmethod
    def is_local_host(**kwargs) -> bool:
        """Return boolean True if host/bookmark belongs to a local host

        :param kwargs: Union[Bookmark, str] to process
        :returns: True/False if a local host name or BookMark
        """
        host = None
        if 'host' in kwargs.keys():
            host = kwargs['host']
        elif 'bm' in kwargs.keys():
            host = kwargs['bm'].hostname
        return host in TheConfig.local_hosts_by_name.keys() or host in TheConfig.local_hosts_by_ip.keys()

    @staticmethod
    def logging_level() -> int:
        """Return logging level"""
        if TheConfig.debug:
            return logging.DEBUG
        return logging.INFO
