"""BookMarks Verify URL's Module"""

# System imports
from typing import Dict, List, Tuple
import requests, urllib3

# Project imports
from defines import UrlType
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
        self.bad_urls_dict: Dict[UrlType, List[Tuple[str, str, str]]] = {
            UrlType.HOSTNAME: [],
            UrlType.MOBILE: [],
            UrlType.MENUBAR: [],
            UrlType.LOCALHOST: [],
        }

        #: Bad URL Hostnames - used to bypass testing BM's for bad HostNames
        self.bad_hostnames: List[str] = []

    # =========================================================================
    def verify_urls(self):
        """Function creating a dictionary of bad URL's"""
        logger.info('Verify HostNames')
        self.verify_url_list(url_type=UrlType.HOSTNAME, url_list=Analyze.hostnames())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        logger.info('Verify Mobile BookMarks')
        self.verify_bm_list(url_type=UrlType.MOBILE, bm_list=Analyze.mobile_bookmarks())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        logger.info('Verify MenuBar BookMarks')
        self.verify_url_dict(url_type=UrlType.MENUBAR, url_dict=Analyze.menubar_bookmarks())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        logger.info('Verify localhost BookMarks')
        self.verify_url_dict(url_type=UrlType.LOCALHOST, url_dict=Analyze.localhost_bookmarks())
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

    # =========================================================================
    def prune_bad_urls(self) -> None:
        """Function to prune (delete) BookMark's with bad URL's"""
        logger.info("Prune bad URL's")
        self.prune_bad_menubar()
        self.prune_bad_localhost()
        self.prune_bad_mobile()
        self.prune_bad_hosts()

    def prune_bad_menubar(self) -> None:
        """Function to remove bookmarks from menubar"""
        logger.info("Prune menubar bookmarks")

    def prune_bad_hosts(self) -> None:
        """Function to remove bookmarks with bad hosts"""
        logger.info("Prune bad hosts")

    def prune_bad_mobile(self) -> None:
        """Function to remove bad mobile bookmarks"""
        logger.info("Prune mobile bookmarks")

    def prune_bad_localhost(self) -> None:
        """Function to remove bad localhost bookmarks"""
        logger.info("Prune localhost bookmarks")

    # =========================================================================
    def verify_url_list(self, url_type: UrlType, url_list: List[str]) -> None:
        """Verify a list of URL's

        :param url_type: Type of URL being verified
        :param url_list: List of URL's (strings) to verify
        """
        for url in url_list:
            if not self.verify_url(url_type, url):
                break

    # =========================================================================
    def verify_url_dict(self, url_type: UrlType, url_dict: Dict) -> None:
        """Verify a dictionary of URL's

        NB: A dictionary of URL's has strings as indices and may have either
            a List or Dict as a value.

        :param url_type: Type of URL being verified
        :param url_dict: Dictionary to verify
        """
        for index, value in url_dict.items():
            if isinstance(value, List):
                self.verify_bm_list(url_type, value)
            elif isinstance(value, Dict):
                self.verify_url_dict(url_type, value)
            else:
                raise ValueError('UNHANDLED URL DICTIONARY TYPE: %s, %s', index, value)

    # =========================================================================
    def verify_bm_list(self, url_type: UrlType, bm_list: List[BookMark]) -> None:
        """Verify a list of URL's in BookMark form

        :param url_type: Type of URL being verified
        :param bm_list: List of BookMarks
        """
        for bm in bm_list:
            bm_url = f'{bm.scheme}://{bm.hostname}{bm.path}'
            if not self.verify_url(url_type, url=bm_url, url_hostname=bm.hostname):
                break

    # =========================================================================
    def verify_url(self, url_type: UrlType, url: str, url_hostname: str = None) -> bool:
        """Verify URL and return False if caller should abort looping

        NB: We will not attempt to verify a URL associated with a known bad
        hostname.

        :param url_type: Type of URL being verified
        :param url: URL to verify
        :param url_hostname: URL HostName for bookkeeping
        :return: abort_looping - boolean - True/False
        """
        # accommodate callers who do not specify a hostname
        if not url_hostname:
            url_hostname = url
        # see if this is a known bad hostname
        if url_hostname in self.bad_hostnames:
            # don't bother checking if hostname is in the bad hostnames list
            status, message = False, "BAD HOSTNAME"
        else:
            # all clear to verify status of this URL
            status, message = self._verify_url(url)
        if not status:
            # keep track of the number of bad URL's
            self.bad_urls_counter += 1
            # enter URL info into bad URL's dictionary
            self.bad_urls_dict[url_type].append((url_hostname, url, message))
            # record bad URL hostname separately
            if url_type == UrlType.HOSTNAME:
                self.bad_hostnames.append(url_hostname)
            # cut testing short if debugging is enabled
            if TheConfig.debug and self.bad_urls_counter > 5:
                logger.debug("EARLY EXIT: %s bad URL's", self.bad_urls_counter)
                return False
        return True

    # =========================================================================
    # Low-level URL verify function
    # =========================================================================
    def _verify_url(self, url: str) -> Tuple[bool, str]:
        """Verify that a URL is reachable

        :param url: URL to verify
        :return: Boolean True/False == Reachable/NotReachable
        """
        logger.debug('VerifyURL: %s', url)
        # prefix URL with HTTPS protocol if no protocol specified
        if url.startswith('http'):
            url_test = url
        else:
            url_test = f'https://{url}'

        # ==========================
        # try opening the url
        try:
            requests.get(url=f'{url_test}', timeout=TheConfig.request_get_timeout)
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
            logger.exception('%s: %s', self.unhandled_exception, url_test, exc_info=e)
            return False, self.unhandled_exception
