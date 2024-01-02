"""BookMarks common definitions"""

# System imports
from enum import Enum, auto


class UrlType(Enum):
    """URL Types"""
    HOSTNAME = auto()
    MOBILE = auto()
    MENUBAR = auto()
    LOCALHOST = auto()

class BadHostType(Enum):
    """Types of bad hosts"""
    PING = auto()
    DNS = auto()
    URL = auto()
