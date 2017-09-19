# -*- coding: utf-8 -*-
"""
Unit tests for the library.
"""

import os
import sys

# from geokelone import *
from geokelone import data


# TEST_DIR = os.path.abspath(os.path.dirname(__file__))



def test_expand():
    assert data.load.expand('Stevens?') == ['Steven', 'Stevens']















if __name__ == '__main__':
    # print('testing', TEST_DIR)
    # print (os.path.join(sys.path[0], '..'))
    test_expand()


