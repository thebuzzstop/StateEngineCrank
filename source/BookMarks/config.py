""" Configuration File Processing """

# System imports
import configparser
import os

# 3rd party imports

# Project imports


class Borg:

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        pass


class TheConfig(Borg):
    """ Global Configuration Parsing for Command Line and Configuration File """

    # global configuration variables initialized to default values
    LOG_LEVEL_STRINGS = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']

    def __init__(self):
        Borg.__init__(self)
        if self._shared_state:
            return
        self.headings = None  #: initialized by config parser


class CfgParser(configparser.ConfigParser):
    """ Configuration File Parsing using the Python standard ConfigParser """

    def __init__(self, **kwargs):
        super().__init__()

        cur_dir = os.path.dirname(os.path.abspath(__file__))
        cfg_file = f"{cur_dir}/config.ini"
        config_items = {
            'personal': ['sites'],
            'ford': ['sites'],
            'projects': ['projects', 'sites', 'partners', 'support'],
            'reference': ['reference', 'courses',],
            'tools': ['tools']
        }

        # see if the configuration file exists before attempting to parse
        if not os.path.isfile(cfg_file):
            raise Exception(f'Configuration file {cfg_file} not found.')

        self.config = configparser.ConfigParser()
        self.config.read(cfg_file)

        # enumerate top-level configuration categories
        self.headings = {}
        for category in self.config.sections():
            self.headings[category] = {}
            for topic in self.config[category]:
                self.headings[category][topic] = self.config[category][topic].replace('\n', '').split(',')

        TheConfig().headings = self.headings
