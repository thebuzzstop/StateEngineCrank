"""BookMarks Verify URL's Module"""

# System imports
from typing import Dict, List, Tuple
import requests, urllib3

# Project imports
from config import TheConfig
from analyze import Analyze
from structures import BookMark
from logger import Logger
logger = Logger(name=__name__).logger

class VerifyUrls:
    """Class to verify reachability of URL's"""

    #: quell SonarLint
    unhandled_exception: str = 'UNHANDLED EXCEPTION'
    #: quell SonarLint
    bad_urls_fmt: str = "BAD URL's: %d"

    def __init__(self):
        """VerifyUrls constructor"""
        logger.info('INFO (%s)', __name__)

        #: Counter of bad URL's
        self.bad_urls_counter: int = 0

        #: Bad URL's status - used by low-level functions
        self.bad_urls_list: List[Tuple[str, str]] = []

        #: URL verification results (only record errors)
        self._url_verify_errors: Dict[str, str] = {}

    @property
    def url_verify_errors(self) -> Dict[str, str]:
        """Property returning dictionary of bad URL's"""
        return self._url_verify_errors

    def verify_urls(self):
        """Function creating a dictionary of bad URL's"""
        logger.info('Verify HostNames')
        self.verify_url_list(Analyze.hostnames())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        logger.info('Verify Mobile BookMarks')
        self.verify_bm_list(Analyze.mobile_bookmarks())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        logger.info('Verify MenuBar BookMarks')
        self.verify_url_dict(Analyze.menubar_bookmarks())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        logger.info('Verify localhost BookMarks')
        self.verify_url_dict(Analyze.localhost_bookmarks())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

    def verify_url_list(self, url_list: List[str]) -> None:
        """Verify a list of URL's

        :param url_list: List of URL's (strings) to verify
        """
        for url in url_list:
            if not self.verify_url(url):
                break

    def verify_url_dict(self, url_dict: Dict) -> None:
        """Verify a dictionary of URL's

        NB: A dictionary of URL's has strings as indices and may have either
            a List or Dict as a value.

        :param url_dict: Dictionary to verify
        """
        for index, value in url_dict.items():
            if isinstance(value, List):
                self.verify_bm_list(value)
            elif isinstance(value, Dict):
                self.verify_url_dict(value)
            else:
                raise ValueError('UNHANDLED URL DICTIONARY TYPE: %s, %s', index, value)
        pass

    def verify_bm_list(self, bm_list: List[BookMark]) -> None:
        """Verify a list of URL's in BookMark form

        :param bm_list: List of BookMarks
        """
        for bm in bm_list:
            bm_url = f'{bm.scheme}://{bm.hostname}{bm.path}'
            if not self.verify_url(bm_url):
                break

    def verify_url(self, url: str) -> bool:
        """Verify URL and return False if caller should abort looping

        :param url: URL to verify
        :return: abort_looping - boolean - True/False
        """
        status, message = self._verify_url(url)
        if not status:
            self.bad_urls_counter += 1
            self.bad_urls_list.append((url, message))
            # cut testing short if debugging is enabled
            if TheConfig.debug and self.bad_urls_counter > 5:
                logger.debug("EARLY EXIT: %s bad URL's", self.bad_urls_counter)
                return False
        return True

    def _verify_url(self, url: str) -> Tuple[bool, str]:
        """Verify that a URL is reachable

        :param url: URL to verify
        :return: Boolean True/False == Reachable/NotReachable
        """
        logger.debug('VerifyURL: %s', url)

        # ==========================
        # try opening the url
        try:
            requests.get(url=f'https://{url}', timeout=TheConfig.request_get_timeout)
            return True, ''

        # =============================
        # Python connection error
        except ConnectionError:
            return False, 'ConnectionError'

        # =============================
        # requests module exceptions
        except requests.exceptions.ConnectionError:
            return False, 'requests.ConnectionError'
        except requests.exceptions.ReadTimeout:
            return False, 'requests.ReadTimeout'
        except requests.exceptions.TooManyRedirects:
            return False, 'requests.TooManyRedirects'
        except requests.exceptions.ContentDecodingError:
            return False, 'requests.ContentDecodingError'

        # =============================
        # urllib3 exceptions
        except urllib3.exceptions.NameResolutionError:
            return False, 'urllib3.NameResolutionError'
        except urllib3.exceptions.ReadTimeoutError:
            return False, 'urllib3.ReadTimeoutError'
        except urllib3.exceptions.DecodeError:
            return False, 'urllib3.DecodeError'

        # =============================
        # unhandled/unknown exception
        except Exception as e:
            logger.exception('%s: %s', self.unhandled_exception, url, exc_info=e)
            return False, self.unhandled_exception
