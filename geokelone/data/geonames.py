# -*- coding: utf-8 -*-
"""
Helpers to import data from geonames.
"""

# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import locale
import logging
import re
import sys
from io import BytesIO
from zipfile import ZipFile

import requests

from .. import settings


# Python3 types
if sys.version_info[0] == 3:
    STRING_TYPE = str
else:
    STRING_TYPE = basestring

# logging
logger = logging.getLogger(__name__)

# locale
locale.setlocale(locale.LC_ALL, settings.LOCALE)
# directory = 'geonames'

# vars
codesdict = dict()
metainfo = dict()


def name_filter(name):
    # length filter
    if len(name) < settings.MINLENGTH:
        return False
    # filter non-locale characters
    # TODO: fix Python 3.6 locale error
    elif re.match(r'[^\w -]+$', name): # , re.LOCALE
        return False
    # catchall
    return True


def generate_urls(countrycodes):
    """
    generate download URLs
    """
    urls = list()
    filenames = list()
    # make it a list
    if isinstance(countrycodes, STRING_TYPE):
        tmp = countrycodes
        countrycodes = list()
        countrycodes.append(tmp)
    # iterate through countrycodes
    for countrycode in countrycodes:
        # i = 0
        countrycode = countrycode.upper()
        url = 'http://download.geonames.org/export/dump/' + countrycode + '.zip'
        filename = countrycode + '.txt'
        urls.append(url)
        filenames.append(filename)
    # bundle
    return urls, filenames


# filter data
def filterline(line):
    """
    Only store a geonames entry if it satisfies formal criteria (type, validity, etc.)
    """
    # global codesdict, metainfo
    columns = re.split('\t', line)

    ## filters
    if len(columns) < 10: # could be higher
        logger.debug('malformed: %s', line)
        return None
    if len(columns[0]) < 1 or len(columns[1]) < 1:
        logger.debug('malformed: %s', line)
        return None
    if columns[1].count(' ') > 3:
        logger.debug('malformed: %s', columns[1])
        return None
    if columns[7] in ('BANK', 'BLDG', 'HTL', 'PLDR', 'PS', 'SWT', 'TOWR'):
        logger.debug('not suitable type: %s', columns[7])
        return None

    # name
    if name_filter(columns[1]) is False:
        logger.debug('no suitable name: %s', columns[1])
        return None

    # check if exists in db
    if columns[0] in codesdict:
        logger.warning('code already seen: %s', line)
        return None
    # examine alternatives
    alternatives = set()
    if ',' in columns[3]:
        for alternative in re.split(',', columns[3]):
            # store
            if name_filter(alternative) is True:
                alternatives.add(alternative)
    else:
        if name_filter(columns[3]) is True:
            alternatives.add(columns[3])

    # store selected information
    # metainfo[columns[0]] = (columns[4], columns[5], columns[6], columns[8], columns[14])
    ## name, alternatenames, latitude, longitude, code, country, population
    # main
    return alternatives, columns[1], (columns[0], columns[4], columns[5], columns[6], columns[8], columns[14])


def store_codesdata(code, alternatives):
    """
    Store codes data in register.
    """
    global codesdict
    # control
    if code not in codesdict:
        codesdict[code] = set()
    # add
    codesdict[code].update(alternatives)


def store_metainfo(infotuple):
    """
    Store metainfo data in register.
    """
    global metainfo
    # control
    if infotuple[0] in metainfo:
        logger.warning('item already in register: %s', infotuple[0])
    # store
    metainfo[infotuple[0]] = (infotuple[1], infotuple[2], infotuple[3], infotuple[4], infotuple[5])


# download data
def fetchdata(countrycodes):
    """
    Retrieve data from geonames for the countries given.
    """
    i = 1
    urls, filenames = generate_urls(countrycodes)
    for url in urls:
        # start
        j = 0
        logger.info('download %s url: %s', i, url)
        request = requests.get(url)

        # log and exit if unsuccessful
        if request.status_code != requests.codes.ok:
            logger.error('problem with response (%s) for url %s', request.status_code, url)
        # normal case
        else:
            with ZipFile(BytesIO(request.content)) as myzip:
                with myzip.open(filenames[i]) as myfile:
                    for line in myfile:
                        # filter
                        alternatives, code, infotuple = filterline(line.decode())
                        # store
                        store_codesdata(code, alternatives)
                        store_metainfo(infotuple)
                        j += 1
            logger.info('%s lines seen', j)
        i += 1
    return codesdict, metainfo


def filterfile(filename):
    """
    File data helper.
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            # filter
            alternatives, code, infotuple = filterline(line.decode())
            # store
            store_codesdata(code, alternatives)
            store_metainfo(infotuple)
    return codesdict, metainfo


# write info to file
def writefile(dictname, filename):
    """
    Save geonames information to a file.
    """
    logger.info('writing register to file %s', filename)
    i = 0
    with open(filename, 'w', encoding='utf-8') as outfh:
        for key in sorted(dictname):
            if len(key) > 1:
                outfh.write(key)
                for item in dictname[key]:
                    outfh.write('\t' + item)
                outfh.write('\n')
                i += 1
    logger.info(i, '%s lines written')


# control
#with open('geonames-codes.dict', 'w') as out1:
#    with open('geonames-meta.dict', 'w') as out2:
#        for key in codesdict:
            #if len(key) > 1:
#            out1.write (key)
#            for item in codesdict[key]:
#                out1.write ('\t' + item)
#                out2.write (item)
#                for metaelem in metainfo[item]:
#                    out2.write ('\t' + metaelem)
#                out2.write ('\n')
#            out1.write ('\n')


# writefile('geonames.filtered', places)
