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
    ## TODO
    return False


def validate_tagged(line):
    """
    Validate tokenized and tagged input format.
    """
    if re.search(r'^.+?\t[A-Z]+?\t.+$', line):
        return True
    return False


def validate_mapdata(dicentry):
    """
    Validate metadata imported from registries.
    """
    # latitude
    if dicentry['lat'] is None or dicentry['lat'] > 90 or dicentry['lat'] < -90:
        return False
    # longitude
    if dicentry['lon'] is None or dicentry['lon'] > 180 or dicentry['lon'] < -180:
        return False
    # toponym
    if dicentry['place'] is None:
        return False

    return True


def validate_registry(line):
    """
    Validate registry data.
    """
    ## TODO
    return True
