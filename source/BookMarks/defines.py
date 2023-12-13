"""BookMarks common definitions"""

# System imports
from enum import Enum, auto


class UrlType(Enum):
    """URL Types"""
    HOSTNAME = auto()
    MOBILE = auto()
    MENUBAR = auto()
    LOCALHOST = auto()
