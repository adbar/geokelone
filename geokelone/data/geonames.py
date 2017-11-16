# -*- coding: utf-8 -*-
"""
Helpers to import data from geonames.
"""

# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

import locale
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


locale.setlocale(locale.LC_ALL, settings.LOCALE)
# directory = 'geonames'


# filter data
def filterline(line, codesdict, metainfo):
    """
    Only store a geonames entry if it satisfies formal criteria (type, validity, etc.)
    """
    seen_codes = set()
    columns = re.split('\t', line)

    ## filters
    if len(columns[0]) < 1 or len(columns[1]) < 1:
        return
    if columns[1].count(' ') > 3:
        return
    if columns[7] in ('BANK', 'BLDG', 'HTL', 'PLDR', 'PS', 'SWT', 'TOWR'):
        return
    # check if exists in db
    if columns[0] in seen_codes:
        print('WARN: code already seen', line)
        return

    ## name, alternatenames, latitude, longitude, code, country, population
    # main
    if columns[1] not in codesdict:
        codesdict[columns[1]] = set()
        codesdict[columns[1]].add(columns[0])

    # examine alternatives
    alternatives = re.split(',', columns[3])
    if len(alternatives) > 0:
        for item in alternatives:
            # filter non-German characters
            if len(item) > 2 or re.match(r'[^\w -]+$', item, re.LOCALE):
                continue
            # add to known codes
            if item not in codesdict:
                codesdict[item] = set()
                codesdict[item].add(columns[0])

    # store selected information
    metainfo[columns[0]] = (columns[4], columns[5], columns[6], columns[8], columns[14])
    seen_codes.add(columns[0])


# download data
def fetchdata(countrycodes, codesdict, metainfo):
    """
    Retrieve data from geonames for the countries given.
    """
    # make it a list
    if isinstance(countrycodes, STRING_TYPE):
        tmp = countrycodes
        countrycodes = list()
        countrycodes.append(tmp)
    # iterate through countrycodes
    for countrycode in countrycodes:
        i = 0
        countrycode = countrycode.upper()
        url = 'http://download.geonames.org/export/dump/' + countrycode + '.zip'
        filename = countrycode + '.txt'
        print('downloading...', url)
        request = requests.get(url)
        with ZipFile(BytesIO(request.content)) as myzip:
            with myzip.open(filename) as myfile:
                for line in myfile:
                    filterline(line.decode(), codesdict, metainfo)
                    i += 1
        print(i, 'lines seen')


def filterfile(filename, codesdict, metainfo):
    """
    File data helper.
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            filterline(line, codesdict, metainfo)


# write info to file
def writefile(dictname, filename):
    """
    Save geonames information to a file.
    """
    print('writing register to file', filename)
    i = 0
    with open(filename, 'w', encoding='utf-8') as outfh:
        for key in sorted(dictname):
            if len(key) > 1:
                outfh.write(key)
                for item in dictname[key]:
                    outfh.write('\t' + item)
                outfh.write('\n')
                i += 1
    print(i, 'lines written')


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
