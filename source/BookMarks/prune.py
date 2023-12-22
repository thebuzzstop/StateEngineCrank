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
    _prune_bad_hosts()
    _prune_bad_localhost()
    _prune_bad_menubar()
    _prune_bad_mobile()

def _prune_bad_menubar() -> None:
    """Function to remove bookmarks from menubar"""
    logger.info("Prune menubar bookmarks")
    # remove any BM's with a known bad hostname
    menubar_urls: List[BadUrlStatus] = list(VerifyUrls.bad_urls_dict()[UrlType.MENUBAR])
    for _bm in menubar_urls:
        if _bm.hostname in VerifyUrls.bad_hostnames():
            Analyze.delete_bookmark_by_id(_bm.bm_id)

def _prune_bad_hosts() -> None:
    """Function to remove bookmarks with bad hosts"""
    logger.info("Prune bad hosts")

def _prune_bad_mobile() -> None:
    """Function to remove bad mobile bookmarks"""
    logger.info("Prune mobile bookmarks")

def _prune_bad_localhost() -> None:
    """Function to remove bad localhost bookmarks"""
    logger.info("Prune localhost bookmarks")
