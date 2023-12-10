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

    def __init__(self):
        """VerifyUrls constructor"""
        logger.info('INFO (%s)', __name__)

        #: URL verification results (only record errors)
        self._url_verify_errors: Dict[str, str] = {}
    @property
    def url_verify_errors(self) -> Dict[str, str]:
        """Property returning dictionary of bad URL's"""
        return self._url_verify_errors

    def verify_urls(self):
        """Function creating a dictionary of bad URL's"""
        logger.info('Verify HostNames')
        for bad_url, error in self.verify_url_list(Analyze.hostnames()):
            self._url_verify_errors[bad_url] = error

        logger.info('Verify Mobile BookMarks')
        for bad_url, error in self.verify_bm_list(Analyze.mobile_bookmarks()):
            self._url_verify_errors[bad_url] = error

        logger.info('Verify MenuBar BookMarks')
        for bad_url, error in self.verify_url_list(Analyze.menubar_bookmarks()):
            self._url_verify_errors[bad_url] = error

        logger.info('Verify localhost BookMarks')
        for bad_url, error in self.verify_url_list(Analyze.localhost_bookmarks()):
            self._url_verify_errors[bad_url] = error

    def verify_url_list(self, url_list: List[str]) -> List[Tuple[str, str]]:
        """Verify a list of URL's in string form

        Return a list of Tuples of failing URL's and associated error.

        :param url_list: List of URL's (strings)
        :returns: List[Tuple[str, str]]
        """
        url_status: List[Tuple[str, str]] = []
        for url in url_list:
            status, message = self.verify_url(url)
            if not status:
                url_status.append((url, message))
        return url_status

    def verify_bm_list(self, bm_list: List[BookMark]):
        """Verify a list of URL's in BookMark form

        Return a list of Tuples of failing URL's and associated error.

        :param bm_list: List of URL's (BookMarks)
        :returns: List[Tuple[str, str]]
        """
        url_status: List[Tuple[str, str]] = []
        return url_status

    def verify_url(self, url: str) -> Tuple[bool, str]:
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
