# -*- coding: utf-8 -*-
"""
Validate input data types.
"""


# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

# standard
import re

# own
from .. import settings



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
    if re.match(r'[^\s\t]{1,200}$', line):
        return True
    return False


def validate_tagged(line):
    """
    Validate tokenized and tagged input format.
    """
    if re.match(r'[^\t]+?\t[A-Z$,().]+?\t.+$', line):
        return True
    return False


def validate_mapdata(dicentry):
    """
    Validate metadata imported from registries.
    """
    # toponym
    if dicentry['place'] is None:
        print('# WARN: empty key', dicentry['place'])
        return False
    return validate_latlon(dicentry['lat'], dicentry['lon'])
    # return True


def validate_csv_registry(line):
    """
    Validate CSV registry data.
    """
    # four columns expected
    if re.match(r'[^,]+?,[^,]+?,[^,]+?,[^,]+$', line):
        return True
    print('# WARN: registry line not conform', line)
    return False


def validate_tsv_registry(line):
    """
    Validate TSV registry data.
    """
    # three columns expected
    if re.match(r'[^\t]+?\t[^\t]+?\t[^\t]+$', line):
        return True
    print('# WARN: registry line not conform', line)
    return False


def validate_geonames_registry(columns):
    """
    Validate geonames registry data.
    """
    # formal validation
    if len(columns) != 6:
        print('# WARN: geonames metainfo line not conform:', columns)
        return False
    # 
    if not columns[0].isdigit() or not re.match(r'[0-9.-]+$', columns[1]) or not re.match(r'[0-9.-]+$', columns[2]):
        print('# WARN: geonames metainfo line not conform:', columns[0], columns[1], columns[2])
        return False
    if not columns[5].isdigit() or int(columns[5]) < 0:
        print('# WARN: value error for population:', columns[5])
        return False
    return validate_latlon(columns[1], columns[2])
    # default
    # return True


def validate_geonames_codes(columns):
    """
    Validate geonames code data.
    """
    # formal validation
    if len(columns) <= 1 or not columns[1].isdigit():
        print('# WARN: geonames code line not conform:', columns)
        return False
    # length filter
    elif len(columns[0]) < settings.MINLENGTH:
        print('# WARN: entry name too short:', columns[0])
        return False
    return True


def validate_latlon(lat, lon):
    """
    Validate coordinates (latitude and longitude).
    """
    # latitude
    if float(lat) > 90 or float(lat) < -90:
        print('# WARN: latitude out of bounds:', lat)
        return False
    # longitude
    if float(lon) > 180 or float(lon) < -180:
        print('# WARN: latitude out of bounds:', lon)
        return False
    return True
