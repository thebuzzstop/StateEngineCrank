""" Common Configuration Definitions """

# System imports
from abc import ABC, abstractmethod
import argparse


class ConfigData(ABC):
    """ Base Configuration Class Data """

    def __init__(self, parser=None):
        if parser:
            self.parser = parser
        else:
            self.parser = argparse.ArgumentParser()

    @abstractmethod
    def add_args(self, parser):
        """ Add parser arguments

            :param parser: Parser to add arguments to
        """
        pass

    @abstractmethod
    def parse_args(self, parser):
        """ Parse arguments

            :param parser: Parser to use for parsing
        """
        pass
