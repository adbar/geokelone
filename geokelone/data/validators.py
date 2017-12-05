# -*- coding: utf-8 -*-
"""
Validate input data types.
"""


# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

# standard
# import locale
import logging
import re

# own
from .. import settings

# logging
logger = logging.getLogger(__name__)

# locale
# locale.setlocale(locale.LC_ALL, settings.LOCALE)


def validate_text(text):
    """
    Validate text input format.
    """
    ## TODO
    return True


def validate_tok(line):
    """
    Validate tokenized input format.
    """
    if re.match(r'[^ \t\n\r\f\v]{1,200}$', line):
        return True
    return False


def validate_tagged(line):
    """
    Validate tokenized and tagged input format.
    """
    if re.match(r'[^\t]+?\t[A-Z$,().]+?\t.+$', line):
        return True
    return False


def validate_csv_registry(columns):
    """
    Validate CSV registry data.
    """
    # four columns expected
    if len(columns) != 4:
        logger.warning('registry line not conform: %s', columns)
        return False
    # coordinates
    if validate_latlon(columns[2], columns[3]) is False:
        logger.warning('coordinates not conform: %s %s', columns[2], columns[3])
        return False
    
    return True


def validate_tsv_registry(columns):
    """
    Validate TSV registry data.
    """
    # three columns expected
    if len(columns) != 3:
        logger.warning('registry line not conform: %s', columns)
        return False
    # coordinates
    if validate_latlon(columns[1], columns[2]) is False:
        logger.warning('coordinates not conform: %s %s', columns[1], columns[2])
        return False
    return True


def validate_entry(name):
    # length filter
    if len(name) < settings.MINLENGTH:
        logger.debug('entry too short: %s', name)
        return False
    # too many spaces
    elif name.count(' ') >= 3:
        logger.debug('too many spaces: %s', name)
        return False
    # refuse non-word characters (and out of Unicode charset)
    elif re.search(r'[^\w .&-]', name): # , re.LOCALE Python 3.6 locale error
        logger.debug('contains unsuitable characters: %s', name)
        return False
    # catchall
    return True


def validate_geonames_registry(columns):
    """
    Validate geonames registry data.
    """
    # formal validation
    if len(columns) != 6:
        logger.warning('geonames metainfo line not conform: %s', ' '.join(columns))
        return False
    # metadata
    if not columns[0].isdigit() or not re.match(r'[0-9.-]+$', columns[1]) or not re.match(r'[0-9.-]+$', columns[2]):
        logger.warning('geonames metainfo line not conform: %s %s %s', columns[0], columns[1], columns[2])
        return False
    if not columns[5].isdigit() or int(columns[5]) < 0:
        logger.warning('value error for population: %s', columns[5])
        return False
    return validate_latlon(columns[1], columns[2])
    # default
    # return True


def validate_geonames_codes(columns):
    """
    Validate geonames code data.
    """
    # formal validation
    # TODO: add column by column validation for multiple columns
    if len(columns) < 2 or not columns[-1].isdigit():
        logger.warning('geonames code line not conform: %s', columns)
        return False
    # form filter
    if validate_entry(columns[0]) is False:
        logger.debug('entry refused: %s', columns[0])
        return False
    return True


def validate_latlon(lat, lon):
    """
    Validate coordinates (latitude and longitude).
    """
    try:
        # latitude
        if float(lat) > 90 or float(lat) < -90:
            logger.warning('latitude out of bounds: %s', lat)
            return False
        # longitude
        if float(lon) > 180 or float(lon) < -180:
            logger.warning('longitude out of bounds: %s', lon)
            return False
        return True
    except ValueError:
        logger.warning('problem with coordinates: %s %s', lat, lon)
        return False


def validate_mapdata(dicentry):
    """
    Validate metadata imported from registries.
    """
    if len(dicentry) < 8:
        logger.warning('malformed result line: %s', dicentry)
        return False
    # toponym
    #if 'place' not in dicentry:
    #    logger.warning('empty key in dict: %s', dicentry)
    #    return False
    if not re.search(r'\w', dicentry[5]):
        logger.warning('malformed entry name: %s', dicentry[6])
        return False
    # coordinates
    #if 'lat' not in dicentry or 'lon' not in dicentry:
    #    logger.warning('empty coordinates: %s', dicentry)
    #    return False
    try:
        lat = float(dicentry[0])
        lon = float(dicentry[1])
    except ValueError:
        logger.warning('malformed coordinates: %s %s', dicentry[1], dicentry[2])
        return False
    # return validate_latlon(dicentry['lat'], dicentry['lon'])
    return validate_latlon(lat, lon)


def validate_result(columns):
    """
    Validate result from geoparsing.
    """
    # columns
    if len(columns) != 9:
        logger.debug('malformed entry: %s', columns)
        return False
    # numeric id
    if not columns[0].isdigit():
        logger.debug('malformed id: %s', columns[0])
        return False
    # name
    if validate_entry(columns[6]) is False:
        logger.debug('malformed place name: %s', columns[6])
        return False
    # coordinates
    if validate_latlon(columns[1], columns[2]) is False:
        logger.debug('malformed coordinates: %s %s', columns[1], columns[2])
        return False
    # TODO: type?

    # catchall
    return True


## TODO:
# def validate_WKT():
