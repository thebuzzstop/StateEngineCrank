"""BookMarks Verify URL's Module"""

# System imports
from typing import Dict, List, NamedTuple, Tuple
import requests, urllib3
import json

# Project imports
from defines import UrlType, BadHostType
from exceptions import MyException
from config import TheConfig
from analyze import Analyze
from structures import BookMark, BookMarks, bm_counter
from mydns import dns_query
from myping import my_ping
from logger import Logger
logger = Logger(name=__name__).logger


class BadUrlStatus(NamedTuple):
    """NamedTuple declaration for URL bad status"""
    hostname: str   #: URL hostname
    url: str        #: URL with path (if any)
    error: str      #: URL error status message
    bm_id: int      #: URL BookMark ID (if available)

class Borg:
    """There can only be one"""

    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class VerifyUrls(Borg):
    """Class to verify reachability of URL's"""

    #: quell SonarLint
    unhandled_exception: str = 'UNHANDLED EXCEPTION'
    #: quell SonarLint
    bad_urls_fmt: str = "BAD URL's: %d"
    #: quell SonarLint
    bad_hostnames_fmt: str = "BAD HOST's: %d"
    # quell SonarLint
    entries_fmt: str = "Entries: %d"
    #: Counter of bad Hosts
    bad_hostnames_counter: int = 0
    #: Counter for bad Hosts - ping
    bad_hostnames_counter_ping: int = 0
    #: Counter for bad Hosts - DNS lookup
    bad_hostnames_counter_dns: int = 0
    #: Ping cache has been read and is active
    ping_cache_active: bool = False
    #: DNS cache has been read and is active
    dns_cache_active: bool = False
    #: URL's cache has been read and is active
    urls_cache_active: bool = False

    def __init__(self):
        """VerifyUrls constructor"""
        Borg.__init__(self)
        if self._shared_state:
            return
        logger.info('INFO (%s)', __name__)
        #: BookMarks access
        self.bookmarks: BookMarks = BookMarks()
        #: Counter of bad URL's
        self.bad_urls_counter: int = 0
        #: URL's gas-gauge
        self.urls_gas_gauge: int = 0

    # =========================================================================
    # Class Methods
    # =========================================================================
    #: Bad URL's status - used by low-level functions
    _bad_urls_dict: Dict[UrlType, List[BadUrlStatus]] = {
        UrlType.HOSTNAME: [],
        UrlType.MOBILE: [],
        UrlType.MENUBAR: [],
        UrlType.LOCALHOST: [],
    }

    # =========================================================================
    @classmethod
    def bad_urls_dict_entries(cls) -> int:
        """Function returning number of entries in bad URL's dictionary"""
        count = 0
        for key in cls._bad_urls_dict.keys():
            count += len(cls._bad_urls_dict[key])
        return count

    # =========================================================================
    @classmethod
    def bad_urls_dict(cls) -> Dict[UrlType, List[BadUrlStatus]]:
        """Class method returning bad URL's dictionary"""
        return cls._bad_urls_dict

    # =========================================================================
    #: Bad URL Hostnames (ping) - used to bypass testing BM's for bad HostNames
    _bad_hostnames_ping: List[str] = []

    @classmethod
    def bad_hostnames(cls) -> List[str]:
        """Class method returning bad Hostnames (ping+dns)"""
        bad_hostnames = cls._bad_hostnames_dns
        bad_hostnames.extend(cls._bad_hostnames_dns)
        return bad_hostnames

    @classmethod
    def bad_hostnames_ping(cls) -> List[str]:
        """Class method returning bad Hostnames (ping)"""
        return cls._bad_hostnames_ping

    # =========================================================================
    #: Bad URL Hostnames (DNS) - used to bypass testing BM's for bad HostNames
    _bad_hostnames_dns: List[str] = []

    @classmethod
    def bad_hostnames_dns(cls) -> List[str]:
        """Class method returning bad Hostnames (DNS)"""
        return cls._bad_hostnames_dns

    # =========================================================================
    @classmethod
    def read_bad_hosts_ping_cache(cls):
        """Function to initialize bad hosts ping from cache"""
        try:
            with open(TheConfig.bad_hosts_ping_cache_file, 'r') as cache:
                logger.info('Loading BadHosts cache (%s)', TheConfig.bad_hosts_ping_cache_file)
                cls._bad_hostnames_ping = json.load(cache)
                cls.bad_hostnames_counter_ping = len(cls._bad_hostnames_ping)
                logger.info(cls.entries_fmt, cls.bad_hostnames_counter_ping)
                cls.ping_cache_active = True
        except FileNotFoundError:
            # warn user but ignore file not found
            logger.warn('BadHosts ping cache not found (%s)', TheConfig.bad_hosts_ping_cache_file)
        except Exception as e:
            logger.exception(cls.unhandled_exception, exc_info=e)

    # =========================================================================
    @classmethod
    def read_bad_hosts_dns_cache(cls):
        """Function to initialize bad hosts DNS lookup from cache"""
        try:
            with open(TheConfig.bad_hosts_dns_cache_file, 'r') as cache:
                logger.info('Loading BadHosts cache (%s)', TheConfig.bad_hosts_dns_cache_file)
                cls._bad_hostnames_dns = json.load(cache)
                cls.bad_hostnames_counter_dns = len(cls._bad_hostnames_dns)
                logger.info(cls.entries_fmt, cls.bad_hostnames_counter_dns)
                cls.dns_cache_active = True
        except FileNotFoundError:
            # warn user but ignore file not found
            logger.warn('BadHosts DNS cache not found (%s)', TheConfig.bad_hosts_dns_cache_file)
        except Exception as e:
            logger.exception(cls.unhandled_exception, exc_info=e)

    # =========================================================================
    @classmethod
    def write_bad_hosts_ping_cache(cls):
        """Function to write bad ping hosts to cache"""
        try:
            with open(TheConfig.bad_hosts_ping_cache_file, 'w') as cache:
                logger.info('Writing BadHosts ping cache (%s)', TheConfig.bad_hosts_ping_cache_file)
                json.dump(cls._bad_hostnames_ping, cache, indent=4)
                logger.info(cls.entries_fmt, len(cls._bad_hostnames_ping))
        except Exception as e:
            logger.exception(cls.unhandled_exception, exc_info=e)

    # =========================================================================
    @classmethod
    def write_bad_hosts_dns_cache(cls):
        """Function to write bad DNS hosts to cache"""
        try:
            with open(TheConfig.bad_hosts_dns_cache_file, 'w') as cache:
                logger.info('Writing BadHosts DNS cache (%s)', TheConfig.bad_hosts_dns_cache_file)
                json.dump(cls._bad_hostnames_dns, cache, indent=4)
                logger.info(cls.entries_fmt, len(cls._bad_hostnames_dns))
        except Exception as e:
            logger.exception(cls.unhandled_exception, exc_info=e)

    # =========================================================================
    @classmethod
    def read_bad_urls_cache(cls):
        """Function to read bad URL's from cache"""
        try:
            with open(TheConfig.bad_urls_cache_file, 'r') as cache:
                logger.info("Reading bad URL's cache (%s)", TheConfig.bad_urls_cache_file)
                cls._bad_urls_dict = json.load(cache)
                logger.info(cls.entries_fmt, cls.bad_urls_dict_entries())
                cls.urls_cache_active = True
        except FileNotFoundError:
            # warn user but ignore file not found
            logger.warn("Bad URL's cache not found (%s)", TheConfig.bad_urls_cache_file)
        except Exception as e:
            logger.exception(cls.unhandled_exception, exc_info=e)

    # =========================================================================
    @classmethod
    def write_bad_urls_cache(cls):
        """Function to write bad URL's cache"""
        try:
            with open(TheConfig.bad_urls_cache_file, 'w') as cache:
                logger.info("Writing bad URL's cache (%s)", TheConfig.bad_urls_cache_file)
                json.dump(cls._bad_urls_dict, cache, indent=4)
                logger.info(cls.entries_fmt, cls.bad_urls_dict_entries())
        except Exception as e:
            logger.exception(cls.unhandled_exception, exc_info=e)

    # =========================================================================
    @classmethod
    def read_bad_hosts_cache(cls):
        """Function to read bad hosts cache file(s)"""
        cls.read_bad_hosts_ping_cache()
        cls.read_bad_hosts_dns_cache()

    # =========================================================================
    @classmethod
    def write_bad_hosts_cache(cls):
        """Function to write bad hosts cache file(s)"""
        cls.write_bad_hosts_ping_cache()
        cls.write_bad_hosts_dns_cache()

    # =========================================================================
    def verify_urls(self):
        """Function creating a dictionary of bad URL's"""
        logger.info('Verify HostNames')

        # read bad host cache if requested
        if TheConfig.use_bad_hosts_cache:
            self.read_bad_hosts_cache()

        # verify hostnames DNS
        if not self.dns_cache_active:
            self._verify_host_list_dns(url_type=UrlType.HOSTNAME, url_list=Analyze.hostnames())

        # verify hostnames ping
        if not self.ping_cache_active:
            self._verify_host_list_ping(url_type=UrlType.HOSTNAME, url_list=Analyze.hostnames())

        # write bad host cache files if requested
        if TheConfig.use_bad_hosts_cache:
            self.write_bad_hosts_cache()
        logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

        # initialize the BookMarks gas-gauge for instrumentation
        self.urls_gas_gauge = bm_counter()

        # read bad url's cache if requested
        if TheConfig.use_bad_urls_cache:
            self.read_bad_urls_cache()

        # skip URL verification if cache was successfully read
        # this would not normally be used but is useful for expediting debug
        if not self.urls_cache_active:
            logger.info('Verify Mobile BookMarks')
            self.verify_bm_list(url_type=UrlType.MOBILE, bm_list=Analyze.mobile_bookmarks())
            logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

            logger.info('Verify MenuBar BookMarks')
            self.verify_url_dict(url_type=UrlType.MENUBAR, url_dict=Analyze.menubar_bookmarks())
            logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

            logger.info('Verify localhost BookMarks')
            self.verify_url_dict(url_type=UrlType.LOCALHOST, url_dict=Analyze.localhost_bookmarks())
            logger.debug(self.bad_urls_fmt, self.bad_urls_counter)

            # write bad url's cache if requested
            if TheConfig.use_bad_urls_cache:
                self.write_bad_urls_cache()

    # =========================================================================
    def _verify_host_list_dns(self, url_type: UrlType, url_list: List[str]) -> None:
        """Verify a list of hostnames - DNS lookup

        :param url_type: Type of URL being verified
        :param url_list: List of URL's (strings) to verify
        """
        dns_counter = len(url_list)
        for url in url_list:
            # skip a URL that is in the bad hosts DNS list
            if url in self._bad_hostnames_dns:
                dns_counter -= 1
                continue
            # perform DNS lookup
            status, lookup = dns_query(url)
            logger.debug('DNS[%04d]: %s %s', dns_counter, url, lookup)
            dns_counter -= 1
            # follow up on status
            if not status:
                if not self._track_bad_url(url_type, url,
                                           url_hostname=url,
                                           message="DNS-LOOKUP",
                                           url_bm_id=None,
                                           bad_host_type=BadHostType.DNS):
                    # exit early if tracking exceeds limits
                    return

    def _verify_host_list_ping(self, url_type: UrlType, url_list: List[str]) -> None:
        """Verify a list of hostnames - PING

        NB: We do not verify (PING) hosts that are in the DNS bad hosts list

        :param url_type: Type of URL being verified
        :param url_list: List of URL's (strings) to verify
        """
        ping_counter = len(url_list)
        for url in url_list:
            # skip a URL that is in the bad hosts DNS list
            if url in self._bad_hostnames_dns:
                ping_counter -= 1
                continue
            # skip a URL that is in the bad hosts ping list
            if url in self._bad_hostnames_ping:
                ping_counter -= 1
                continue
            # ping the host
            status, message = my_ping(url)
            logger.debug('PING[%04d]: %s %s', ping_counter, url, message)
            ping_counter -= 1
            # follow up on status
            if not status:
                if not self._track_bad_url(url_type, url,
                                           url_hostname=url,
                                           message=message,
                                           url_bm_id=None,
                                           bad_host_type=BadHostType.PING):
                    # exit early if tracking exceeds limits
                    return

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
        """Verify URL's in a List[BookMark] form

        :param url_type: Type of URL being verified
        :param bm_list: List of BookMarks
        """
        for bm in bm_list:
            if not self.verify_bm_url(url_type, bm):
                break

    # =========================================================================
    def verify_bm_url(self, url_type: UrlType, bm: BookMark) -> bool:
        """Verify BookMark URL and return False if caller should abort looping

        NB: We will not attempt to verify a URL associated with a known bad
            hostname.

        :param url_type: Type of URL being verified
        :param bm: BookMark
        :return: abort_looping - boolean - True/False
        """
        # see if this is a known bad hostname
        if bm.hostname in self._bad_hostnames_dns or bm.hostname in self._bad_hostnames_ping:
            # don't bother checking the bookmark if the hostname is in the bad hostnames lists
            status, message = False, "BAD HOSTNAME"
        else:
            # update HTTP to HTTPS if requested
            if TheConfig.http2https and bm.is_http and not bm.is_localhost:
                bm.protocol_override = 'https'
                status, message = self._verify_bm_url(bm)
                if status:
                    # update protocol on success
                    bm.protocol = bm.protocol_override
                else:
                    # remove override on failure
                    bm.protocol_override = None
            else:
                status, message = self._verify_bm_url(bm)

        # common exit - test status and track bad URL's
        if not status:
            return self._track_bad_url(url_type,
                                       url=f'{bm.protocol}//{bm.hostname}{bm.path}',
                                       url_hostname=bm.hostname,
                                       message=message,
                                       url_bm_id=bm.id,
                                       bad_host_type=BadHostType.URL)
        return True

    # =========================================================================
    def _track_bad_url(self, url_type, url, url_hostname, message, url_bm_id, bad_host_type: BadHostType) -> bool:
        """Function to do some bookkeeping for bad URL's

        :param url_type: Type of URL being verified
        :param url: URL to verify
        :param url_hostname: URL HostName for bookkeeping
        :param url_bm_id: URL BookMark ID
        :param bad_host_type: Bad host type (enum)
        :param message: Failing status message
        """
        # keep track of the number of bad URL's
        self.bad_urls_counter += 1
        # enter URL info into bad URL's dictionary
        self._bad_urls_dict[url_type].append(
            BadUrlStatus(hostname=url_hostname, url=url, error=message, bm_id=url_bm_id))
        # record bad URL hostname separately
        if url_type == UrlType.HOSTNAME:
            if bad_host_type == BadHostType.DNS:
                self._bad_hostnames_dns.append(url_hostname)
                self.bad_hostnames_counter_dns += 1
            elif bad_host_type == BadHostType.PING:
                self._bad_hostnames_ping.append(url_hostname)
                self.bad_hostnames_counter_ping += 1
            elif bad_host_type != BadHostType.URL:
                raise MyException(f'INVALID BAD HOST TYPE: {bad_host_type}')

        # cut testing short if debugging is enabled
        if TheConfig.test_mode and self.bad_urls_counter > 5:
            logger.debug("EARLY EXIT: %s bad URL's", self.bad_urls_counter)
            return False
        return True

    # =========================================================================
    # Low-level URL verify function
    # =========================================================================
    def _verify_bm_url(self, bm: BookMark) -> Tuple[bool, str]:
        """Verify that a BookMark URL responds to HTTP request

        :param bm: BookMark to verify
        :return: Tuple[Boolean True/False == Reachable/NotReachable, str]
        """
        def error_exit(msg: str) -> Tuple[bool, str]:
            """Common error exit

            Don't decrement URL's gas-gauge if this is an override.

            :param msg: Message to return to caller
            :return: Tuple[Boolean status, str]
            """
            if not bm.protocol_override:
                self.urls_gas_gauge -= 1
            return False, msg

        # use protocol override if one is given
        if bm.protocol_override:
            bm_protocol = bm.protocol_override
        else:
            bm_protocol = bm.protocol

        logger.debug('VerifyURL[%04d]: %s://%s%s', self.urls_gas_gauge, bm_protocol, bm.hostname, bm.path)

        # ==========================
        # try opening the url
        try:
            # noinspection PyVulnerableApiCode
            requests.get(url=f'{bm.url}',
                         timeout=TheConfig.request_get_timeout,
                         allow_redirects=False)
            self.urls_gas_gauge -= 1
            return True, ''

        # =============================
        # Python connection error
        except ConnectionError:
            return error_exit('ConnectionError')

        # =============================
        # requests module exceptions
        except requests.exceptions.ConnectionError:
            return error_exit('requests.ConnectionError')
        except requests.exceptions.ReadTimeout:
            return error_exit('requests.ReadTimeout')
        except requests.exceptions.TooManyRedirects:
            return error_exit('requests.TooManyRedirects')
        except requests.exceptions.ContentDecodingError:
            return error_exit('requests.ContentDecodingError')

        # =============================
        # urllib3 exceptions
        except urllib3.exceptions.NameResolutionError:
            return error_exit('urllib3.NameResolutionError')
        except urllib3.exceptions.ReadTimeoutError:
            return error_exit('urllib3.ReadTimeoutError')
        except urllib3.exceptions.DecodeError:
            return error_exit('urllib3.DecodeError')

        # =============================
        # unhandled/unknown exception
        except Exception as e:
            logger.exception('%s: %s', self.unhandled_exception, bm.url, exc_info=e)
            return error_exit(self.unhandled_exception)
