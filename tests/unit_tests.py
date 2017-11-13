# -*- coding: utf-8 -*-
"""
Unit tests for the library.
"""

from os import path
import sys

# from geokelone import *
from geokelone import data, geo, text


TEST_DIR = path.abspath(path.dirname(__file__))



def test_expand():
    assert data.load.expand('Stevens?') == ['Steven', 'Stevens']



def test_read():
    assert len(text.readfile.readtok(path.join(TEST_DIR, 'data/fontane-stechlin.tok'))) == 44











if __name__ == '__main__':
    # print('testing', TEST_DIR)
    # print (os.path.join(sys.path[0], '..'))
    test_expand()
    test_tsv()


