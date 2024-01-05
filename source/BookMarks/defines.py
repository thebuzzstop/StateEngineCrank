"""BookMarks common definitions"""

# System imports
from enum import Enum, auto


class UrlType(str):
    """URL Types"""
    HOSTNAME = "HostName"
    MOBILE = "Mobile"
    MENUBAR = "MenuBar"
    LOCALHOST = "LocalHost"

class BadHostType(str):
    """Types of bad hosts"""
    PING = "Ping"
    DNS = "DNS"
    URL = "URL"
