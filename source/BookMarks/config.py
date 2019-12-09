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
    BOOKMARK_HTML_ICON_FORMAT_NO_LABEL = '<DT><A HREF="{0}" ADD_DATE="{1}" ICON="{2}"></A>'

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
    noheadings = None       #: section.subsection combinations not to have a heading
    menubar = None          #: menubar constructed by config parser
    scanning_order = None   #: order in which scanning processing will occur
    sections = None         #: menutab sections (topic groups)
    head = None             #: menutab 'head' section
    tail = None             #: menutab 'tail' section
    capitalized = None      #: menubar capitalized label words
    input_file = None       #: bookmarks input file to be processed
    output_file = None      #: bookmarks output file (after processing)


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

        # get files to be processed
        TheConfig.input_file = config['files']['input']
        TheConfig.output_file = config['files']['output']

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
        TheConfig.noheadings = self.get_list(config['menubar']['noheadings'])
        TheConfig.menubar = menubar
        TheConfig.capitalized = self.get_list_tuples(config['menubar']['capitalized'])
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
        items0 = config_item.replace('\\,', '&&')
        items1 = items0.lower().replace('\n', '').replace(', ', ',').split(',')
        for i in range(len(items1)):
            items1[i] = items1[i].replace('&&', ',')
            if not items1[i]:
                del items1[i]
        return items1

    @staticmethod
    def get_list_tuples(config_item: str):
        """ Return a [list] of configuration items which are parsed as tuples

            Do not return an empty/null/'' item
            :param config_item: Configuration file item
        """
        items = config_item.replace('\n', '').replace(', ', ',').split(',')
        tuples = []
        for i in range(0, len(items), 2):
            if items[i]:
                tuples.append((items[i], items[i+1]))
            else:
                del items[i]
        return tuples
