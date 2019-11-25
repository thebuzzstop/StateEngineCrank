""" Configuration File Processing """

# System imports
import configparser
import os

# 3rd party imports

# Project imports


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

    # configuration items initialized by config parser
    config = None           #: configuration items
    headings = None         #: headings declared in config.ini
    menubar = None          #: menubar constructed by config parser
    scanning_order = None   #: order in which scanning processing will occur
    sections = None         #: menutab sections (topic groups)
    head = None             #: menutab 'head' section
    tail = None             #: menutab 'tail' section


class CfgParser(configparser.ConfigParser):
    """ Configuration File Parsing using the Python standard ConfigParser """

    def __init__(self):
        super().__init__()

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        cfg_file = f"{cur_dir}/config.ini"

        # see if the configuration file exists before attempting to parse
        if not os.path.isfile(cfg_file):
            raise Exception(f'Configuration file {cfg_file} not found.')

        config = configparser.ConfigParser()
        config.read(cfg_file)

        # establish menubar structure
        menubar = {
            'head': self.get_list(config['menubar']['head']),
            'tail': self.get_list(config['menubar']['tail'])
        }
        # enumerate menubar heading topics
        headings = self.get_list(config['menubar']['headings'])
        for heading in headings:
            menubar[heading] = {topic: None for topic in config.options(heading)}

        # enumerate menubar heading sub-topics
        for heading in headings:
            for topic in config[heading]:
                menubar[heading][topic] = {
                    topic: None for topic in self.get_list(config[heading][topic])
                }

        # get scanning order
        TheConfig.scanning_order = self.get_list(config['scanning']['order'])
        TheConfig.config = config
        TheConfig.headings = headings
        TheConfig.menubar = menubar
        TheConfig.sections = {}
        for menubar in self.get_list(config['menubar']['headings']):
            TheConfig.sections[menubar] = {}
            for section in config.options(menubar):
                TheConfig.sections[menubar][section] = self.get_list(config[menubar][section])
        pass

    @staticmethod
    def get_list(config_item: str):
        """ Return a [list] of configuration items

            Do not return an empty/null/'' item
            :param config_item: Configuration file item
        """
        items = config_item.lower().replace('\n', '').replace(', ', ',').split(',')
        for i in range(len(items)):
            if not items[i]:
                del items[i]
        return items
