# -*- coding: utf-8 -*-
"""
Unit tests for the library.
"""

import logging
import sys

from os import path

# from geokelone import *
from geokelone import data, geo, text


TEST_DIR = path.abspath(path.dirname(__file__))

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)



def test_expand():
    assert data.load.expand('[VW]ien(na)?') == ['Vien', 'Vienna', 'Wien', 'Wienna']
    assert data.load.expand('(Außer|Über)au') == ['Außerau', 'Überau']


def test_read():
    assert len(text.readfile.readplain(path.join(TEST_DIR, 'data/fontane-stechlin.txt'))) == 71
    assert len(text.readfile.readtok(path.join(TEST_DIR, 'data/fontane-stechlin.tok'))) == 44
    assert len(text.readfile.readtagged(path.join(TEST_DIR, 'data/fontane-stechlin.tagged'))) == 4


def custom_csv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.csv')
    customized = data.load.load_csv(registry)
    # test alternatives
    print(customized)
    assert 'Atest' in customized and 'Btest' in customized
    return (customized)


def custom_tsv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.tsv')
    customized = data.load.load_tsv(registry)
    # test alternatives
    assert 'Sankt Petersburg' in customized # and 'St. Petersburg' in customized
    return (customized)


def test_tagged():
    # setup
    inputfile = path.join(TEST_DIR, 'data/fontane-stechlin.tagged')
    splitted = text.readfile.readtagged(inputfile)
    # search
    results = geo.geocoding.search(splitted, dict(), dict(), custom_csv())
    assert len(results) == 3
    assert 'Berlin' in results and 'Petersburg' in results and 'Preußen' in results
    results = geo.geocoding.search(splitted, dict(), dict(), custom_tsv())
    assert len(results) == 3
    assert 'Berlin' in results and 'Petersburg' in results and 'Preußen' in results


def test_tok():
    # setup
    inputfile = path.join(TEST_DIR, 'data/fontane-stechlin.tok')
    splitted = text.readfile.readtok(inputfile)
    # search
    results = geo.geocoding.search(splitted, dict(), dict(), custom_csv())
    assert len(results) == 3
    assert 'Berlin' in results and 'Petersburg' in results and 'Preußen' in results
    results = geo.geocoding.search(splitted, dict(), dict(), custom_tsv())
    assert len(results) == 3
    assert 'Berlin' in results and 'Petersburg' in results and 'Preußen' in results


def test_geonames():
    # setup
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-meta.dict')
    metainfo = data.load.loadmeta(inputfile)
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-codes.dict')
    codes = data.load.loadcodes(inputfile, metainfo)
    assert len(metainfo) == 3 and len(codes) == 3
    # search
    # results = dict()
    results = geo.geocoding.search(['Aachen', 'Aachen'], codes, metainfo)
    print('###')
    print(results)
    assert len(results) == 1 and '3247449' in results
    ## multi-word
    # 2
    results = geo.geocoding.search(['Öderquarter'], codes, metainfo)
    assert '2858070' not in results
    # results = dict()
    results = geo.geocoding.search(['Öderquarter', 'Moor'], codes, metainfo)
    print('###')
    print(results)
    assert len(results) == 1 and '2858070' in results
    # 3
    results = geo.geocoding.search(['It', 'was', 'in', 'Reichenbach', 'am', 'Heuberg', '.'], codes, metainfo)
    print('###')
    print(results)
    assert len(results) == 1 and '2849119' in results


if __name__ == '__main__':
    # print('testing', TEST_DIR)
    # print (os.path.join(sys.path[0], '..'))
    test_expand()
    test_read()
    test_tagged()
    test_tok()
    test_geonames()



