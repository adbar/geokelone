# -*- coding: utf-8 -*-
"""
External tools for data manipulation.
"""

# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

# standard
import logging
import ssl
import urllib3

# extra
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


# logging
logger = logging.getLogger(__name__)

# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# download pool manager
class MyAdapter(HTTPAdapter):
    """Customize HTTPS support for requests (may not be necessary anymore)"""
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_version=ssl.PROTOCOL_TLSv1, timeout=10.0)

session = requests.Session()
session.mount('https://', MyAdapter())


def send_request(query_url):
    """Send a request over the network."""
    logger.debug('sending request %s', query_url)
    request = session.get(query_url, verify=False)
    if request.status_code != requests.codes.ok:
        logger.error('problem with response (%s) for url %s', request.status_code, query_url)
        return None
    return request.text
