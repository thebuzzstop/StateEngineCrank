"""Configuration File Processing"""

# System imports
import argparse
import configparser
import logging
import os

# 3rd party imports

# Project imports
from the_config import TheConfig
from exceptions import MyException
from logger import Logger, Loggers



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
        parser.add_argument("-P", "--prune", help="prune bad URL's during processing", action="store_true")
        parser.add_argument("-T", "--test", help="enable 'test mode'", action="store_true")
        parser.add_argument("--timeout", type=float, help="timeout in seconds (float) for verifying URL's")
        parser.add_argument("--http2https", help="convert HTTP URL's to HTTPS", action="store_true")
        parser.add_argument("--use_hosts_cache", help="use bad hosts cache files", action="store_true")
        parser.add_argument("--use_urls_cache", help="use bad URL's cache file", action="store_true")
        parser.add_argument("--prune_bad_dns", help="prune bookmarks with bad DNS", action="store_true")

        # parse command line arguments
        args = parser.parse_args()
        if args.debug:
            TheConfig.debug = True
            Loggers.set_logging_levels(logging_level=logging.DEBUG)
        if args.test:
            TheConfig.test_mode = True
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
        if args.prune:
            TheConfig.verify_prune = True
        if args.prune_bad_dns:
            TheConfig.prune_bad_dns = True
        if args.timeout:
            TheConfig.request_get_timeout = args.timeout
        if args.http2https:
            TheConfig.http2https = True
        if args.use_hosts_cache:
            TheConfig.use_bad_hosts_cache = True
        if args.use_urls_cache:
            TheConfig.use_bad_urls_cache = True

    @staticmethod
    def substitute_tilde(path: str):
        """Substitute $HOME for leading tilde '~'"""
        if path.startswith('~'):
            home = os.environ.get('HOME')
            return home + path[1:]
        return path


class CfgParser(configparser.ConfigParser):
    """Configuration File Parsing using the Python standard ConfigParser"""

    # make available for debugging
    the_config = TheConfig

    def __init__(self):
        super().__init__()

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
                menubar[heading][topic] = { # :FixMe:
                    topic: None for topic in self.get_list(config[heading][topic])
                }

        # check for private hosts
        if 'hosts' in config:
            hosts = config['hosts']
            for host in hosts:
                ip = config['hosts'][host].strip(',')
                if ip == 'localhost':
                    # 'localhost' is a special case for ip-address and hostname
                    TheConfig.local_hosts_by_name[TheConfig.my_hostname] = TheConfig.my_ip_address
                    TheConfig.local_hosts_by_ip[TheConfig.my_ip_address] = TheConfig.my_hostname
                else:
                    # if not 'localhost' then use whatever is in the config-file
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
        """Return a [list] of configuration items

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
        """Return a [list] of configuration items which are parsed as tuples

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
