"""Function supporting pinging network hosts"""

# System imports
from typing import Tuple

# PyPi imports
from ping3 import ping, EXCEPTIONS


WWW_PREFIX = 'www.'
LEN_WWW_PREFIX = len(WWW_PREFIX)

def my_ping(dest_address: str, timeout: int = 4) -> Tuple[bool, str]:
    """High-level function to return status of destination address ping

    It has possible that URL's that contain 'www' prefix will fail when
    attempting a ping.

    It is also possible that URL's that are a simple hostname without
    the 'www' will fail.

    We will parse the destination address and either add or remove a
    'www' prefix contained in the address depending on if the first
    attempt fails.

    :param dest_address: Hostname to ping, e.g. www.google.com
    :param timeout: Time to wait for response (seconds)
    :return: Tuple[bool, str] True/False - hostname is/not pingable, status string
    """
    # first try ping with no modifications to destination address
    status1, message1 = _my_ping(dest_address)
    if status1:
        return True, message1

    # failure so modify destination address - add/remove 'www' prefix
    if dest_address.startswith(WWW_PREFIX):
        dest_address2 = dest_address[LEN_WWW_PREFIX:]
    else:
        dest_address2 = WWW_PREFIX + dest_address

    # try again with modified destination address
    status2, message2 = _my_ping(dest_address2, timeout)
    if status2:
        return True, message2

    # modified destination failed so just send original status and message
    return status1, message1

def _my_ping(dest_address: str, timeout: int = 4) -> Tuple[bool, str]:
    """Low-level function to return status of destination address ping

    NB: This implementation does not require root priv's to access ping

    :param dest_address: Hostname to ping, e.g. www.google.com
    :param timeout: Time to wait for response (seconds)
    :return: Tuple[bool, str] True/False - hostname is/not pingable, status string
    """
    try:
        status = ping(dest_address, timeout, unit='ms')
        if status is None:
            return False, "TIMEOUT"
        if not status:
            return False, "ERROR"
    except EXCEPTIONS as e:
        print('ping error:', e)
        return False, "UNHANDLED EXCEPTION"
    # status is time in msec returned from ping3.ping()
    return True, f'{int(status+0.5)} msec'
