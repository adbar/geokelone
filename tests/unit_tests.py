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
    assert 'Atest' in customized and 'Btest' in customized
    return (customized)


def custom_tsv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.tsv')
    customized = data.load.load_tsv(registry)
    # test alternatives
    assert 'Sankt Petersburg' in customized # and 'St. Petersburg' in customized
    return (customized)


def geonames_filter():
    # malformed
    assert data.geonames.filterline('\n', dict(), dict()) == 0
    assert data.geonames.filterline('	1	2.3', dict(), dict()) == 0
    # wrong type
    assert data.geonames.filterline('6466296	Ambassador	Ambassador		51.2091	4.4226	S	HTL	BE		VLG	VAN	11	11002	0		7	Europe/Brussels	2016-08-02', dict(), dict()) == 0
    # OK
    assert data.geonames.filterline('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25', dict(), dict()) == 1
    # duplicate entry
    assert data.geonames.filterline('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25', dict(), dict()) == 0


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
    metainfo = data.load.geonames_meta(inputfile)
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-codes.dict')
    codes = data.load.geonames_codes(inputfile, metainfo)
    assert len(metainfo) == 3 and len(codes) == 3
    # search
    results = geo.geocoding.search(['Aachen', 'Aachen'], codes, metainfo)
    assert len(results) == 1 and '3247449' in results
    ## multi-word
    # 2
    results = geo.geocoding.search(['Öderquarter'], codes, metainfo)
    assert '2858070' not in results
    results = geo.geocoding.search(['Öderquarter', 'Moor'], codes, metainfo)
    assert len(results) == 1 and '2858070' in results
    # 3
    results = geo.geocoding.search(['It', 'was', 'in', 'Reichenbach', 'am', 'Heuberg', '.'], codes, metainfo)
    assert len(results) == 1 and '2849119' in results


def test_haversine():
    assert geo.geocoding.haversine(53.4, 1.2, 61, 10.53) == '1012.13'
    assert geo.geocoding.haversine(-53.466666, 1, 61, -3.33333) == '12725.89'


def test_disambiguate():
    test_metainfo = {\
                    '1':[48.13, 8.85, 'P', 'DE', 0],\
                    '2':[48.13, 8.85, 'P', 'DE', 10],\
                    }
    assert geo.geocoding.disambiguate(['1', '2'], 1, test_metainfo) == '2'
    assert geo.geocoding.disambiguate(['1', '2'], 2, test_metainfo) == '2'
    test_metainfo = {\
                    '1':[48.13, 8.85, 'P', 'DE', 10],\
                    '2':[48.13, 8.85, 'A', 'DE', 10],\
                    }
    assert geo.geocoding.disambiguate(['1', '2'], 1, test_metainfo) == '1'
    assert geo.geocoding.disambiguate(['1', '2'], 2, test_metainfo) == '1'

    #print(geo.geocoding.disambiguate(['1', '2', '3'], 1, {'2': [-46.13, -8.85, 'P', 'ZZ', 10], '3': [45.13, 9.85, 'P', 'DE', 2000], '1': [47.13, 7.85, 'P', 'DE', 0]}))


def test_rounds():
    test_metainfo = {\
                    '1':[47.13, 7.85, 'P', 'DE', 0],\
                    '2':[46.13, 8.85, 'P', 'DE', 10],\
                    '3':[45.13, 9.85, 'P', 'DE', 2000],\
                    }
    test_codesdict = {\
                    'AAA':['1', '2', '3'],\
                    }

    #print(geo.geocoding.disambiguating_rounds('AAA', test_codesdict, test_metainfo))
    #assert geo.geocoding.disambiguating_rounds('AAA', test_codesdict, test_metainfo) == '3'



if __name__ == '__main__':
    # print('testing', TEST_DIR)
    # print (os.path.join(sys.path[0], '..'))
    test_expand()
    test_read()
    test_tagged()
    test_tok()
    geonames_filter()
    test_geonames()
    test_haversine()
    test_disambiguate()
    # test_rounds()



