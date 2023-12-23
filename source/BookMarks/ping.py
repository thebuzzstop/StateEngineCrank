"""Function supporting pinging network hosts"""

from typing import Tuple
from ping3 import ping, EXCEPTIONS


def my_ping(dest_address: str, timeout: int = 4) -> Tuple[bool, str]:
    """Function to return status of destination address ping

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
