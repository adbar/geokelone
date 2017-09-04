# -*- coding: utf-8 -*-


# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals


import re


from .. import settings



def validate_text(text):
    return True


def validate_tok(line):
    return False


def validate_tagged(line):
    if re.search(r'^.+?\t[A-Z]+?\t.+$', line):
        return True
    return False




def validate_mapdata(dicentry):
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

    return True



