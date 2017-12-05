# -*- coding: utf-8 -*-
"""
Unit tests for the library.
"""

import logging
import sys

from os import path

# from geokelone import *
from geokelone import data, geo, text, settings


TEST_DIR = path.abspath(path.dirname(__file__))

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

settings.FILTER_LEVEL = 'MINIMUM'
settings.ROUNDING = 3


def test_expand():
    assert data.load.expand('[VW]ien(na)?') == ['Vien', 'Vienna', 'Wien', 'Wienna']
    assert data.load.expand('(Außer|Über)au') == ['Außerau', 'Überau']


def test_read():
    assert text.readfile.readplain(path.join(TEST_DIR, 'data/dummy-file.txt')) == ['Token', 'T15', 'Other-info']
    assert len(text.readfile.readplain(path.join(TEST_DIR, 'data/fontane-stechlin.txt'))) == 42
    assert text.readfile.readtok(path.join(TEST_DIR, 'data/dummy-file.txt')) == []
    assert len(text.readfile.readtok(path.join(TEST_DIR, 'data/fontane-stechlin.tok'))) == 44
    assert len(text.readfile.readtagged(path.join(TEST_DIR, 'data/fontane-stechlin.tagged'))) == 4


def custom_csv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.csv')
    customized = data.load.load_csv(registry)
    # test alternatives
    assert 'Atest' in customized and 'Btest' in customized
    return customized


def custom_tsv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.tsv')
    customized = data.load.load_tsv(registry)
    # test alternatives
    assert 'Sankt Petersburg' in customized # and 'St. Petersburg' in customized
    return customized


def test_validate_entry():
    assert data.validators.validate_entry(' ') is False
    assert data.validators.validate_entry('Efghi!') is False
    assert data.validators.validate_entry('AAA BBB Ccc Dddd Ee') is False # too many spaces
    assert data.validators.validate_entry('Amsterdam') is True
    assert data.validators.validate_entry('Marcq-en-Barœul') is True


def test_data_validators():
    # custom files
    assert data.validators.validate_csv_registry('Petersburg;Sankt-Petersburg,Sankt Petersburg,-2,-2.2') is True
    assert data.validators.validate_csv_registry('Petersburg,St. Petersburg,-2,2,3') is False
    assert data.validators.validate_tsv_registry('Preußens?	-33.3	33.3') is True
    assert data.validators.validate_tsv_registry('AAA	NNN	NNN	NNN') is False

    # entries in gazetteers
    # assert data.validators.validate_mapdata({'place': 'test', 'lat': '30', 'lon': 30}) is True
    # assert data.validators.validate_mapdata({'place': None, 'lat': '30', 'lon': 30}) is False
    # assert data.validators.validate_mapdata({'place': 'test', 'lat': '300', 'lon': 300}) is False
    # assert data.validators.validate_mapdata({'place': 'test', 'lat': '20.5'}) is False
    assert data.validators.validate_mapdata([47.003333, 11.5075, 'X', 'YY', 0, 'Brenner', 'NULL', 2]) is True
    assert data.validators.validate_mapdata(['AAA', 11.5075, 'X', 'YY', 0, 'Brenner', 'NULL', 2]) is False
    assert data.validators.validate_mapdata([47.003333, 11.5075, 'X']) is False

    # load gazetteers
    assert data.validators.validate_geonames_registry('2849119	48.13333	8.85	P	DE	0	0') is False
    assert data.validators.validate_geonames_registry(['2849119', '48.13333', '8.85']) is False
    assert data.validators.validate_geonames_registry(['AAA', '48.13333', '8.85', 'P', 'DE', '0']) is False
    assert data.validators.validate_geonames_registry(['2849119', 'G13', 'D10', 'P', 'DE', '0']) is False
    assert data.validators.validate_geonames_registry(['2849119', '48.13333', '8.85', 'P', 'DE', '-10']) is False
    assert data.validators.validate_geonames_codes(['Reichenbach am Heuberg', '2849119']) is True
    assert data.validators.validate_geonames_codes(['Reichenbach', '12', '++']) is False
    assert data.validators.validate_geonames_codes(['RR', '2849119']) is False
    assert data.validators.validate_geonames_codes(['Reichenbach am Heuberg', 'V12']) is False


def test_text_validators():
    assert data.validators.validate_tok('Marcq-en-Barœul') is True
    assert data.validators.validate_tok('Marcq en Barœul') is False
    assert data.validators.validate_tagged('Token	NN	Token') is True
    assert data.validators.validate_tagged('Token	nn	Token') is False
    assert data.validators.validate_tagged(',	$,	,') is True
    # assert data.validators.validate_text('') is True


def test_geodata_validators():
    assert data.validators.validate_latlon(0, 0) is True
    assert data.validators.validate_latlon(-90, 180) is True
    assert data.validators.validate_latlon(90.1, -180.1) is False
    assert data.validators.validate_latlon(-10, 365) is False
    assert data.validators.validate_latlon(10, +1000) is False


def test_geonames_download():
    assert data.geonames.generate_urls('fi') == (['http://download.geonames.org/export/dump/FI.zip'], ['FI.txt'])
    assert data.geonames.generate_urls(['fi']) == (['http://download.geonames.org/export/dump/FI.zip'], ['FI.txt'])
    assert data.geonames.generate_urls(['fa', 'fi', 'fr']) == (['http://download.geonames.org/export/dump/FA.zip', 'http://download.geonames.org/export/dump/FI.zip', 'http://download.geonames.org/export/dump/FR.zip'], ['FA.txt', 'FI.txt', 'FR.txt'])


def test_geonames_filter():
    # malformed
    assert data.geonames.filterline('\n') is None
    assert data.geonames.filterline('	1	2.3') is None
    assert data.geonames.filterline('		2.3	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA') is None
    assert data.geonames.filterline('6466296	AAA BBB GGG AAA BBBB	Amba		51	4	P	PPL	BE		VLG	VAN	11	11002	0		7	XX	YY')  is None
    # wrong type
    assert data.geonames.filterline('6466296	Ambassador	Ambassador		51.2091	4.4226	S	HTL	BE		VLG	VAN	11	11002	0		7	Europe/Brussels	2016-08-02')  is None
    # OK
    assert data.geonames.filterline('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is not None
    # alternatives
    result = data.geonames.filterline('2867714	Munich	Munich	Monachium,Monaco di Baviera,München	48.13743	11.57549	P	PPLA	DE		02	091	09162	09162000	1260391		524	Europe/Berlin	2014-01-26')
    print(result)
    assert result is not None and result[0] == {'Monachium', 'Monaco di Baviera', 'München'}


def test_geonames_store():
    # init
    alternatives, code, infotuple = data.geonames.filterline('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25')

    # store code
    assert code not in data.geonames.codesdict
    data.geonames.store_codesdata(code, alternatives)
    assert code in data.geonames.codesdict

    # store info
    assert infotuple[0] not in data.geonames.metainfo
    data.geonames.store_metainfo(infotuple)
    assert infotuple[0] in data.geonames.metainfo

    # duplicate entry
    assert data.geonames.filterline('2801074	Breitfeld	Breitfeld	50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is None


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


def test_wikipedia():
    assert data.wikipedia.find_coordinates('Wien', language='en') == (None, None)
    assert data.wikipedia.find_coordinates('Wien', language='de') == (48.208, 16.373)


def test_haversine():
    assert geo.geocoding.haversine(53.4, 1.2, 61, 10.53) == '1012.13'
    assert geo.geocoding.haversine(-53.466666, 1, 61, -3.33333) == '12725.89'


def test_geofind():
    test_metainfo = {\
                    '1':[47.13, 7.85, 'P', 'DE', 0],\
                    '2':[48.13, 7.85, 'P', 'DE', 2000],\
                    }
    test_codesdict = {\
                    'AAA':['1'],\
                    }
    assert geo.geocoding.geofind('AAA', test_codesdict, test_metainfo, None) is False



def test_disambiguate():
    ## type
    assert geo.geocoding.disambiguate(None, 1, dict()) is None
    assert geo.geocoding.disambiguate('Test', 1, dict()) == 'Test'
    assert geo.geocoding.disambiguate(['Test'], 1, dict()) == 'Test'

    ## pop count
    test_metainfo = {\
                    '1':[48.13, 8.85, 'P', 'DE', 0],\
                    '2':[48.13, 8.85, 'P', 'DE', 100],\
                    '3':[48.13, 8.85, 'P', 'DE', 10000],\
                    }
    assert geo.geocoding.disambiguate(['1', '2'], 1, test_metainfo) == '2'
    assert geo.geocoding.disambiguate(['1', '2'], 2, test_metainfo) == '2'
    assert geo.geocoding.disambiguate(['2', '3'], 1, test_metainfo) == '3'
    assert geo.geocoding.disambiguate(['2', '3'], 2, test_metainfo) == '3'
    assert geo.geocoding.disambiguate(['1', '2', '3'], 1, test_metainfo) == '3'
    assert geo.geocoding.disambiguate(['1', '2', '3'], 2, test_metainfo) == '3'

    ## place type
    test_metainfo = {\
                    '1':[48.13, 8.85, 'P', 'DE', 100],\
                    '2':[48.13, 8.85, 'A', 'DE', 100],\
                    '3':[30, 8, 'A', 'XX', 0],\
                    }
    assert geo.geocoding.disambiguate(['1', '2', '3'], 2, test_metainfo) == '1'
    test_metainfo = {\
                    '1':[48.13, 8.85, 'A', 'DE', 100],\
                    '2':[48.13, 8.85, 'P', 'DE', 100],\
                    '3':[30, 8, 'P', 'XX', 0],\
                    }
    assert geo.geocoding.disambiguate(['1', '2', '3'], 2, test_metainfo) == '2'

    ## distance
    assert geo.geocoding.disambiguate(['1', '2', '3'], 1, {'2': [-46.13, -8.85, 'P', 'ZZ', 1000], '3': [-45.13, -9.85, 'P', 'ZZ', 1000], '1': [47.13, 7.85, 'P', 'ZZ', 1000]}) == '3'


def test_rounds():
    ## normal situation
    test_metainfo = {\
                    '1':[47.13, 7.85, 'P', 'DE', 0],\
                    '2':[46.13, 8.85, 'P', 'DE', 0],\
                    '3':[45.13, 9.85, 'P', 'DE', 2000],\
                    }
    test_codesdict = {\
                    'AAA':['1', '2', '3'],\
                    }
    assert geo.geocoding.disambiguating_rounds('AAA', test_codesdict, test_metainfo) == '3'
    ## no winner
    test_metainfo = {\
                    '1':[47.13, 7.85, 'P', 'DE', 0],\
                    '2':[47.13, 7.85, 'P', 'DE', 0],\
                    '3':[47.13, 7.85, 'P', 'DE', 0],\
                    '4':[47.13, 7.85, 'P', 'DE', 0],\
                    }
    test_codesdict = {\
                    'AAA':['1', '2', '3', '4'],\
                    }
    assert geo.geocoding.disambiguating_rounds('AAA', test_codesdict, test_metainfo) is None
    ## too many values
    test_metainfo = {\
                    '1':[47.13, 7.85, 'P', 'DE', 0],\
                    '2':[47.13, 7.85, 'P', 'DE', 0],\
                    '3':[47.13, 7.85, 'P', 'DE', 0],\
                    '4':[47.13, 7.85, 'P', 'DE', 0],\
                    '5':[47.13, 7.85, 'P', 'DE', 0],\
                    '6':[47.13, 7.85, 'P', 'DE', 0],\
                    '7':[47.13, 7.85, 'P', 'DE', 0],\
                    '8':[47.13, 7.85, 'P', 'DE', 0],\
                    '9':[47.13, 7.85, 'P', 'DE', 0],\
                    '10':[47.13, 7.85, 'P', 'DE', 0],\
                    '11':[47.13, 7.85, 'P', 'DE', 0],\
                    '12':[47.13, 7.85, 'P', 'DE', 0],\
                    }
    test_codesdict = {\
                    'AAA':['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],\
                    }
    assert geo.geocoding.disambiguating_rounds('AAA', test_codesdict, test_metainfo) is None


def test_results():
    # setup
    inputfile = path.join(TEST_DIR, 'data/dummy-results.tsv')
    results = data.load.results_tsv(inputfile)
    # validation
    print(results)
    assert len(results) == 7 and '10173868' in results
    

def test_draw_line():
    geo.geocoding.pair = list()
    geo.geocoding.lines = list()
    geo.geocoding.pair_counter = 0
    # draw a line
    geo.geocoding.draw_line(10, 10)
    assert len(geo.geocoding.pair) == 1 and geo.geocoding.pair[0] == (10, 10)
    geo.geocoding.draw_line(20, 20)
    assert len(geo.geocoding.pair) == 1 and geo.geocoding.pair[0] == (20, 20)
    assert len(geo.geocoding.lines) == 1 and geo.geocoding.lines[0] == ((10, 10), (20, 20))
    # window limit exceeded
    geo.geocoding.pair_counter = 100
    geo.geocoding.draw_line(10, 10)
    assert len(geo.geocoding.pair) == 1 and geo.geocoding.pair[0] == (10, 10)



if __name__ == '__main__':
    # print('testing', TEST_DIR)
    # print (os.path.join(sys.path[0], '..'))
    # print(settings.FILTER_LEVEL)

    # registry functions
    test_expand()
    test_validate_entry()

    # input/output functions
    test_read()
    test_tok()
    test_tagged()
    test_text_validators()
    test_results()

    # geonames functions
    test_geonames_download()
    test_geonames_filter()
    test_geonames_store()
    test_geonames()
    test_wikipedia()

    # GIS functions
    test_haversine()
    test_geodata_validators()
    test_draw_line()

    # geocoding functions
    test_disambiguate()
    test_rounds()



