"""BookMarks prune module - remove bad or requested URL's"""

# System imports
from typing import List

# Project imports
from defines import UrlType
from verify_urls import VerifyUrls, BadUrlStatus
from analyze import Analyze
from logger import Logger
logger = Logger(name=__name__).logger

# =========================================================================
def prune_bad_urls() -> None:
    """Function to prune (delete) BookMark's with bad URL's"""
    logger.info("Prune bad URL's")
    # _prune_bad_dns()
    _prune_bad_hosts()
    _prune_bad_localhost()
    # _prune_bad_menubar()
    _prune_bad_mobile()

def _prune_bad_menubar() -> None:
    """Function to remove bookmarks from menubar"""
    logger.info("Prune menubar bookmarks")
    # remove any BM's with a known bad hostname
    menubar_urls: List[BadUrlStatus] = list(VerifyUrls.bad_urls_dict()[UrlType.MENUBAR])
    bad_hostnames = VerifyUrls.bad_hostnames()
    for _bm in menubar_urls:
        bm_hostname = _bm[0]
        bm_id = _bm[3]
        logger.debug("CHECK: %d - %s", bm_id, bm_hostname)
        if bm_hostname in bad_hostnames:
            Analyze.delete_bookmark_by_id(bm_id)

def _prune_bad_dns() -> None:
    """:ToDo: Function to remove bookmarks with bad DNS"""
    logger.info("Prune bad DNS")
    # remove any BM's with a known bad DNS hostname
    bookmarks_list = Analyze.bookmarks_list()
    bad_dns = sorted(VerifyUrls.bad_hostnames_dns())
    # check all bookmarks for bad DNS
    for bm in bookmarks_list:
        if bm.hostname in bad_dns:
            Analyze.delete_bookmark_by_id(bm.id)

def _prune_bad_hosts() -> None:
    """:ToDo: Function to remove bookmarks with bad hosts"""
    logger.info("Prune bad hosts")

def _prune_bad_mobile() -> None:
    """:ToDo: Function to remove bad mobile bookmarks"""
    logger.info("Prune mobile bookmarks")

def _prune_bad_localhost() -> None:
    """:ToDo: Function to remove bad localhost bookmarks"""
    logger.info("Prune localhost bookmarks")
