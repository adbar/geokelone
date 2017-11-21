# -*- coding: utf-8 -*-
"""
Tools for data collection from Wikipedia and Wikidata.
"""


# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals


# standard
import logging
import re
import ssl

from time import sleep


# extra
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager



# logging
logger = logging.getLogger(__name__)


# download pool manager
class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_version=ssl.PROTOCOL_TLSv1, timeout=10.0)

s = requests.Session()
s.mount('https://', MyAdapter())



def navigate_categories(name, language='en'):
    """Takes a category name as input and returns all category members"""
    # init
    flag = 1
    continuecode = ''
    members = list()
    # loop
    while flag > 0:
        if flag == 1:
            qurl = 'https://' + language + '.wikipedia.org/w/api.php?action=query&list=categorymembers&format=json&cmlimit=500&cmtitle=' + name
        elif flag == 2:
            qurl = 'https://' + language + '.wikipedia.org/w/api.php?action=query&list=categorymembers&format=json&cmlimit=500&cmtitle=' + name + '&cmcontinue=' + continuecode
            r = s.get(qurl, verify=False)
            jsonresponse = r.text
            for match in re.finditer(r'"title":"(.+?)"', r.text):
                try:
                    title = match.group(1)
                except AttributeError:
                    logger.warning('Unexpected response for query %s', qurl)
                else:
                    # filter: parentheses and lists
                    if not re.search(r'\(', title) and not re.match(r'Liste? ', title):
                        members.append(title.decode('unicode-escape'))
                        # outputfh.write(line + '\t' + title.decode('unicode-escape') + '\n')
            if 'cmcontinue' in r.text:
                flag = 2
                continuecode = re.search(r'"cmcontinue":"(.+?)"', jsonresponse).group(1)
            else:
                flag = 0
            # throttle
            sleep(0.5)
    return members


def find_coordinates(name, language='en'):
    """Find coordinates for given wikipedia entry"""
    # init
    qurl = 'https://' + language + '.wikipedia.org/w/api.php?action=query&format=json&prop=coordinates&titles=' + name
    logger.debug('sending request %s', qurl)
    # send request
    r = s.get(qurl, verify=False)
    try:
        latitude = re.search(r'"lat":-?([0-9\.]+?),', r.text).group(1)
        longitude = re.search(r'"lon":-?([0-9\.]+?),', r.text).group(1)
    except AttributeError:
        logger.warning('Unexpected response for query %s', qurl)
        # outputfh.write(line + '\t' + '' + '\t' + '' + '\n')
    else:
        return latitude, longitude
        # sleep(0.25)
        # outputfh.write(line + '\t' + latitude + '\t' + longitude + '\n')
    return None, None


#def master():
#    """..."""
#
#    return


