""" Configuration File Processing """

# System imports
import argparse
import configparser
import logging
import os
from typing import Dict, List, Tuple

# 3rd party imports

# Project imports
from structures import BookMark
from exceptions import MyException
from logger import Logger


class TheConfig:
    """ Global Configuration Parsing for Command Line and Configuration File """

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
    LIST_HTML_TEXT_FORMAT = '<DT><p>{0}</p>'
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
    verbosity: bool = False             #: True/False - verbose output enabled
    verbosity_level: int = 0            #: verbosity level
    verify_urls: bool = False           #: verify URL's are reachable as they are processed
    request_get_timeout: float = 0.5    #: default timeout for verifying URL's

    #: specific local hosts (private network) - key == name
    local_hosts_by_name: Dict[str, str] = {}

    #: specific local hosts (private network) - key == ip
    local_hosts_by_ip: Dict[str, str] = {}

    #: host bookmarks for which multiple entries are allowed
    allow_multiple_bookmarks: List[Tuple[str, str]] = []

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
    def allow_multiple(bm: BookMark) -> bool:
        """Return boolean True/False if multiple entries allowed

            :param bm: Bookmark being processed
            :returns: True/False if multiple entries allowed
        """
        host_name = bm.hostname
        friendly_host_name = bm.friendly_host_name
        for allow in TheConfig.config['allow-multiple']:
            host, path = TheConfig.config['allow-multiple'][allow].replace(' ', '').split(',')
            if host == host_name or host == friendly_host_name:
                if path == bm.path:
                    return True
        return False

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


class ArgParser(argparse.ArgumentParser):
    """Command line argument parsing"""

    def __init__(self):
        super().__init__()

        # establish parser
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--debug", help="enable debug output", action="store_true")
        parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="count")
        parser.add_argument("-c", "--config", type=str, help="configuration file")
        parser.add_argument("-i", "--input", type=str, help="bookmarks input html file")
        parser.add_argument("-o", "--output", type=str, help="bookmarks output html file")
        parser.add_argument("-V", "--verify", help="verify URL's during processing", action="store_true")
        parser.add_argument("--timeout", type=float, help="timeout in seconds (float) for verifying URL's")

        # parse command line arguments
        args = parser.parse_args()
        if args.debug:
            TheConfig.debug = True
            Logger().set_level(logger_level=logging.DEBUG, console_level=logging.DEBUG, file_level=logging.DEBUG)
        if args.verbosity:
            TheConfig.verbosity = True
            TheConfig.verbosity_level = args.verbosity
        if args.config:
            TheConfig.config_file = self.substitute_tilde(args.config)
        if args.input:
            TheConfig.input_file = self.substitute_tilde(args.input)
        if args.output:
            TheConfig.output_file = self.substitute_tilde(args.output)
        if args.verify:
            TheConfig.verify_urls = True
        if args.timeout:
            TheConfig.request_get_timeout = args.timeout

    @staticmethod
    def substitute_tilde(path: str):
        """Substitute $HOME for leading tilde '~'"""
        if path.startswith('~'):
            home = os.environ.get('HOME')
            return home + path[1:]
        return path


class CfgParser(configparser.ConfigParser):
    """ Configuration File Parsing using the Python standard ConfigParser """

    def __init__(self):
        super().__init__()

        the_config = TheConfig

        # see if user provided a configuration file on command line
        if TheConfig.config_file is not None:
            cfg_file = TheConfig.config_file
        else:
            cur_dir = os.path.dirname(os.path.abspath(__file__))
            cfg_file = f"{cur_dir}/config_mbs.ini"

        # see if the configuration file exists before attempting to parse
        if not os.path.isfile(cfg_file):
            raise MyException(f'Configuration file not found: {cfg_file}')

        config = configparser.ConfigParser()
        config.read(cfg_file)

        # establish menubar structure
        menubar = {
            'head': self.get_list_tuples(config['menubar']['head'], tuple_size=3),
            'tail': self.get_list_tuples(config['menubar']['tail'], tuple_size=3)
        }
        # enumerate menubar heading topics
        headings = self.get_list(config['menubar']['headings'])
        for heading in headings:
            try:
                menubar[heading] = {topic: None for topic in config.options(heading)}
            except Exception as e:
                print(e)

        # get files to be processed - check for command line overrides
        if TheConfig.input_file is None:
            TheConfig.input_file = config['files']['input']
        if TheConfig.output_file is None:
            TheConfig.output_file = config['files']['output']

        # verify input file exists
        if not os.path.isfile(TheConfig.input_file):
            raise MyException('Input file not found: %s' % TheConfig.input_file)

        # enumerate menubar heading sub-topics
        for heading in headings:
            for topic in config[heading]:
                menubar[heading][topic] = {
                    topic: None for topic in self.get_list(config[heading][topic])
                }

        # check for private hosts
        if 'hosts' in config:
            hosts = config['hosts']
            for host in hosts:
                ip = config['hosts'][host].strip(',')
                TheConfig.local_hosts_by_name[host] = ip
                TheConfig.local_hosts_by_ip[ip] = host

        # check for allowing multiple host/bookmarks
        if 'allow-multiple' in config:
            for host in config['allow-multiple']:
                hostname, bookmark = config['allow-multiple'][host].replace(' ', '').split(',')
                TheConfig.allow_multiple_bookmarks.append((hostname, bookmark))

        # get scanning order
        TheConfig.scanning_order = self.get_list(config['scanning']['order'])
        TheConfig.speed_dial_order = self.get_list(config['scanning']['speed-dial-order'])
        TheConfig.config = config
        TheConfig.headings = headings
        TheConfig.noheadings = self.get_list(config['menubar']['noheadings'])
        TheConfig.menubar = menubar
        TheConfig.capitalized = self.get_list_tuples(config['menubar']['capitalized'], tuple_size=2)
        TheConfig.sections = {}
        for menubar in self.get_list(config['menubar']['headings']):
            TheConfig.sections[menubar] = {}
            for section in config.options(menubar):
                TheConfig.sections[menubar][section] = self.get_list(config[menubar][section])
        # determine speed-dial scan order
        TheConfig.speed_dial_scan_order = self.get_list(config['scanning']['speed-dial-order'])
        # determine speed-dial output order
        TheConfig.speed_dial_output_order = self.get_list(config['speed-dial-output']['order'])
        pass

    @staticmethod
    def get_list(config_item: str):
        """ Return a [list] of configuration items

            Do not return an empty/null/'' item

            :param config_item: Configuration file item
        """
        items0 = config_item.replace('\\,', '&&')
        items1 = items0.lower().replace('\n', '').replace(', ', ',').split(',')
        for i in range(len(items1)):
            items1[i] = items1[i].replace('&&', ',')
            if not items1[i]:
                del items1[i]
        return items1

    @staticmethod
    def get_list_tuples(config_item: str, tuple_size: int):
        """ Return a [list] of configuration items which are parsed as tuples

            Do not return an empty/null/'' item

            :param config_item: Configuration file item
            :param tuple_size: Number of items in a tuple
        """
        items = config_item.replace('\n', '').replace(', ', ',').split(',')
        tuples = []
        for i in range(0, len(items), tuple_size):
            if items[i]:
                if tuple_size == 2:
                    tuples.append((items[i], items[i + 1]))
                elif tuple_size == 3:
                    tuples.append((items[i], items[i + 1], items[i + 2]))
            else:
                del items[i]
        return tuples
