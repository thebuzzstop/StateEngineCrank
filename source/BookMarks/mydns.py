"""Module supporting DNS"""

# System imports
from typing import List, Tuple

# PyPi imports
from nslookup import Nslookup, DNSresponse


# establish Nslookup
ns_lookup = Nslookup(verbose=False, tcp=False)

def dns_query(domain: str) -> Tuple[bool, List]:
    """DNS query function returning lookup status and results

    We try a simple "A" lookup first and try an "AAAA" lookup
    if the "A" lookup fails.

    We return Tuple[False, []] if both lookups fail.

    :param domain: Domain to lookup
    :return: Tuple[status True/False, [lookup results]]
    """
    # try "A" domain lookup
    ips_record: DNSresponse = ns_lookup.dns_lookup(domain)
    if ips_record.answer:
        return True, ips_record.answer

    # try "AAAA" domain lookup
    ips_record6: DNSresponse = ns_lookup.dns_lookup6(domain)
    if ips_record.answer:
        return True, ips_record6.answer

    # return lookup failure
    return False, []
