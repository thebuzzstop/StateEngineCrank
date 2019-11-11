""" Configuration File Processing """

# System imports
import configparser
import os

# 3rd party imports

# Project imports


class TheConfig:
    """ Global Configuration Parsing for Command Line and Configuration File """

    # global configuration variables initialized to default values
    LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

    # configuration items initialized by config parser
    config = None       #: configuration items
    headings = None     #: headings declared in config.ini
    menubar = None      #: menubar constructed by config parser


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
            'head': self.get_list(config['menubar structure']['head']),
            'tail': self.get_list(config['menubar structure']['tail'])
        }
        # enumerate menubar heading topics
        headings = self.get_list(config['menubar structure']['headings'])
        for heading in headings:
            menubar[heading] = {topic: None for topic in config.options(heading)}

        # enumerate menubar heading sub-topics
        for heading in headings:
            for topic in config[heading]:
                menubar[heading][topic] = {
                    topic: None for topic in self.get_list(config[heading][topic])
                }

        TheConfig.config = config
        TheConfig.headings = headings
        TheConfig.menubar = menubar

    @staticmethod
    def get_list(config_item: str):
        """ Return a [list] of configuration items

            Do not return an empty/null/'' item
            :param config_item: Configuration file item
        """
        items = config_item.replace('\n', '').split(',')
        for i in range(len(items)):
            if not items[i]:
                del items[i]
        return items
