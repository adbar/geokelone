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
import urllib3

from time import sleep

# extra
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from . import utils, validators
from .. import settings



## TODO:
# validators
# test output
# language variable



# logging
logger = logging.getLogger(__name__)


def parse_json_response(jsonresponse):
    """Extract crucial elements in the API response"""
    newmembers = list()
    # extract
    for match in re.finditer(r'"title":"(.+?)"', jsonresponse):
        try:
            title = match.group(1)
        except AttributeError:
            logger.warning('Unexpected response for query %s', query_url)
        else:
            # filter: parentheses and lists
            if not re.search(r'\(', title) and not re.match(r'Liste? ', title):
                newmembers.append(title) #.decode('unicode-escape'))
                # outputfh.write(line + '\t' + title.decode('unicode-escape') + '\n')
    if 'cmcontinue' in jsonresponse:
        continuecode = re.search(r'"cmcontinue":"(.+?)"', jsonresponse).group(1)
    else:
        continuecode = None
    return continuecode, newmembers


def navigate_category(name, language='en'):
    """Takes a category name as input and returns all category members"""
    # init
    flag = 1
    members = list()
    logger.info('processing category %s with language code %s', name, language)
    # loop
    while flag > 0:
        # determine URL structure
        if flag == 1:
            query_url = 'https://' + language + '.wikipedia.org/w/api.php?action=query&list=categorymembers&format=json&cmlimit=500&cmtitle=' + name
        elif flag == 2:
            query_url = 'https://' + language + '.wikipedia.org/w/api.php?action=query&list=categorymembers&format=json&cmlimit=500&cmtitle=' + name + '&cmcontinue=' + continuecode
        # send request
        result = utils.send_request(query_url)
        if result is None:
            return list()
        # parse response
        continuecode, newmembers = parse_json_response(result)
        if continuecode is not None:
            flag = 2
        else:
            flag = 0
        members = members + newmembers
        # throttle
        sleep(0.5)
    return members


def find_coordinates(name, language='en'):
    """Find coordinates for given wikipedia entry"""
    # init
    query_url = 'https://' + language + '.wikipedia.org/w/api.php?action=query&format=json&prop=coordinates&titles=' + name
    # send request
    result = utils.send_request(query_url)
    if result is not None:
        try:
            latitude = re.search(r'"lat":(-?[0-9\.]+?),', result).group(1)
            longitude = re.search(r'"lon":(-?[0-9\.]+?),', result).group(1)
        except AttributeError:
            logger.warning('Unexpected response for query %s', query_url)
            # outputfh.write(line + '\t' + '' + '\t' + '' + '\n')
        else:
            if validators.validate_latlon(latitude, longitude) is True:
                 # round
                return round(float(latitude), settings.ROUNDING), round(float(longitude), settings.ROUNDING)
            # sleep(0.25)
            # outputfh.write(line + '\t' + latitude + '\t' + longitude + '\n')
    # catchall
    return None, None


#def process_categories(categories):
#    """Processes a list of categories and returns a list of entries with or without coordinates"""
#    for category in categories:
#        for member in navigate_category(category):
#            lat, lon = find_coordinates(member)
#
#    return


def process_todolist(filename, outputfile=None, categories=False): # , language='en'
    """Processes a list of entries (one entry per line)"""
    # init
    if outputfile is None:
        outputfile = filename + '_output.tsv'
    logger.info('reading from input file %s and appending to output file %s', filename, outputfile)
    # process
    with open(filename, 'r', encoding='utf-8') as inputfh, open(outputfile, 'a', encoding='utf-8') as outputfh:
        for line in inputfh:
            line = line.strip()
            if categories is True:
                for member in navigate_category(line):
                    lat, lon = find_coordinates(member)
                    if lat is not None:
                        outputfh.write(member + '\t' + str(lat) + '\t' + str(lon) + '\n')
                    else:
                        logger.warning('no coordinates found for entry %s', member)
            else:
                lat, lon = find_coordinates(line)
                if lat is not None:
                    outputfh.write(line + '\t' + str(lat) + '\t' + str(lon) + '\n')
                else:
                    logger.warning('no coordinates found for entry %s', line)
    return
