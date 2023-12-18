"""Functions to obtain localhost info"""

import socket

def get_ip() -> str:
    """Function to get localhost IP address

    Taken from StackOverFlow:
      https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib

    According to the author:

    This method returns the "primary" IP on the local box (the one with a default route).

        + Does NOT need routable net access or any connection at all.
        + Works even if all interfaces are unplugged from the network.
        + Does NOT need or even try to get anywhere else.
        + Works with NAT, public, private, external, and internal IP's
        + Pure Python 2 (or 3) with no external dependencies.
        + Works on Linux, Windows, and OSX.

    :return: LocalHost IP address in string form (e.g. '192.168.1.101')
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        _ip = s.getsockname()[0]
    except Exception:
        _ip = '127.0.0.1'
    finally:
        s.close()
    return _ip

def get_hostname() -> str:
    """Function to return localhost name

    :return: LocalHost name in string form (e.g. 'mark-linux')
    """
    try:
        return socket.gethostname()
    except Exception:
        return 'localhost'
