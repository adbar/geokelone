# -*- coding: utf-8 -*-
"""
Unit tests for the library.
"""

import logging
import sys

from os import path

# from geokelone import *
from geokelone import data, geo, text #, settings
import geokelone.settings


TEST_DIR = path.abspath(path.dirname(__file__))

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

geokelone.settings.FILTER_LEVEL = 'MINIMUM'
geokelone.settings.ROUNDING = 3


def test_expand():
    assert data.load.expand('[VW]ien(na)?') == ['Vien', 'Vienna', 'Wien', 'Wienna']
    assert data.load.expand('(Außer|Über)au') == ['Außerau', 'Überau']


def test_store_variants():
    assert data.load.store_variants(['Tests'], [None, None, None], 1) is not None
    #print(data.load.store_variants(['Tests'], [None, None, None], 1))
    #assert data.load.store_variants(['Tests'], [None, None, None], 1) is {}
    #assert data.load.store_variants(['Tests'], [None, None, None], 2) is None


def test_read():
    assert text.readfile.readplain(path.join(TEST_DIR, 'data/dummy-file.txt')) == ['Token', 'T15', 'Other-info']
    assert len(text.readfile.readplain(path.join(TEST_DIR, 'data/fontane-stechlin.txt'))) == 42
    assert text.readfile.readtok(path.join(TEST_DIR, 'data/dummy-file.txt')) == []
    assert len(text.readfile.readtok(path.join(TEST_DIR, 'data/fontane-stechlin.tok'))) == 44
    assert len(text.readfile.readtagged(path.join(TEST_DIR, 'data/fontane-stechlin.tagged'))) == 4


def custom_csv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.csv')
    # level
    assert data.load.load_tsv(registry, level='NN') == {}
    # store
    customized = data.load.load_csv(registry)
    # test alternatives
    assert 'Atest' in customized and 'Btest' in customized
    return customized


def custom_tsv():
    registry = path.join(TEST_DIR, 'data/dummy-registry.tsv')
    # level
    assert data.load.load_tsv(registry, level='NN') == dict()
    # store
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
    assert data.validators.validate_csv_registry(['Petersburg;Sankt-Petersburg', 'Sankt Petersburg', '-2', '-2.2']) is True
    assert data.validators.validate_csv_registry(['Petersburg', 'St. Petersburg', '-2', '2', '3']) is False
    assert data.validators.validate_csv_registry(['Petersburg', 'St. Petersburg', '-222', '2E']) is False
    assert data.validators.validate_tsv_registry(['Preußens?','-33.3','33.3']) is True
    assert data.validators.validate_tsv_registry(['Preußens?','1111','2222']) is False
    assert data.validators.validate_tsv_registry(['AAA','NNN','NNN','NNN']) is False

    # entries in gazetteers
    map_boundaries = [geokelone.settings.WESTMOST, geokelone.settings.EASTMOST, geokelone.settings.SOUTHMOST, geokelone.settings.NORTHMOST]
    assert data.validators.validate_mapdata(['-190', '11.5075', 'X', 'YY', '0', 'A', 'NULL', 2], map_boundaries) is False
    assert data.validators.validate_mapdata(['47.003333', '11.5075', 'X', 'YY', '0', 'Brenner', 'NULL', 2], map_boundaries) is True
    assert data.validators.validate_mapdata(['AAA', '11.5075', 'X', 'YY', '0', 'Brenner', 'NULL', 2], map_boundaries) is False
    assert data.validators.validate_mapdata(['47.003333', '11.5075', 'X', 'YY', '0', '###', 'NULL', 2], map_boundaries) is False
    assert data.validators.validate_mapdata(['47.003333', '11.5075', 'X'], map_boundaries) is False
    map_boundaries = [-20, 20, -20, 20]
    assert data.validators.validate_mapdata(['47.003333', '11.5075', 'X', 'YY', '0', 'Brenner', 'NULL', 2], map_boundaries) is False
    assert data.validators.validate_mapdata(['0', '0', 'X', 'YY', '0', 'ABC', 'NULL', 2], map_boundaries) is True

    # load gazetteers
    assert data.validators.validate_geonames_registry(['2849119', '48.13333', '8.85', 'P', 'DE', '0' ,'0']) is False
    assert data.validators.validate_geonames_registry(['2849119', '48.13333', '8.85']) is False
    assert data.validators.validate_geonames_registry(['AAA', '48.13333', '8.85', 'P', 'DE', '0']) is False
    assert data.validators.validate_geonames_registry(['2849119', 'G13', 'D10', 'P', 'DE', '0']) is False
    assert data.validators.validate_geonames_registry(['2849119', '48.13333', '8.85', 'P', 'DE', '-10']) is False
    assert data.validators.validate_geonames_codes(['Reichenbach am Heuberg', '2849119']) is True
    assert data.validators.validate_geonames_codes(['Reichenbach', '12', '++']) is False
    assert data.validators.validate_geonames_codes(['RR', '2849119']) is False
    assert data.validators.validate_geonames_codes(['Reichenbach am Heuberg', 'V12']) is False

    # result
    assert data.validators.validate_result(['6536007', '46.938', '11.442', 'X', 'YY', '2087', 'NULL', 2]) is False
    assert data.validators.validate_result(['6536007', '46.938', '11.442', 'X', 'YY', '2087', 'Brenner', 'NULL', 2]) is True
    assert data.validators.validate_result(['6536007', '46.938', '11.442', 'X', 'YY', '2087', 'B', 'NULL', 2]) is False
    assert data.validators.validate_result(['6536007', '46.938', '11.442', 'X', 'YY', '2087', 'B B B B B', 'NULL', 2]) is False


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
    assert data.geonames.quality_control('\n') is None
    assert data.geonames.quality_control('	1	2.3') is None
    assert data.geonames.quality_control('																			') is None
    assert data.geonames.quality_control('		2.3	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA	AAA') is None
    assert data.geonames.quality_control('6466296	AAA BBB GGG AAA BBBB	Amba		51	4	P	PPL	BE		VLG	VAN	11	11002	0		7	XX	YY')  is None
    # wrong type
    assert data.geonames.quality_control('6466296	Ambassador	Ambassador		51.2091	4.4226	S	HTL	BE		VLG	VAN	11	11002	0		7	Europe/Brussels	2016-08-02')  is None
    # OK
    assert data.geonames.quality_control('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is not None
    result = data.geonames.quality_control('2801074	Breitfeld	Breitfeld	Breitfeld	50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25')
    assert result is not None and result[0] == {'Breitfeld'}
    # filtering levels
    geokelone.settings.FILTER_LEVEL = 'MAXIMUM'
    assert data.geonames.quality_control('6466296	Ambassador	Ambassador		51.2091	4.4226	S	HTL	BE		VLG	VAN	11	11002	0		7	Europe/Brussels	2016-08-02')  is None
    assert data.geonames.quality_control('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is not None
    geokelone.settings.FILTER_LEVEL = 'MINIMUM'
    # coordinates
    assert data.geonames.quality_control('2801074	Breitfeld	Breitfeld		1150.26417	4446.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is None
    # country
    assert data.geonames.quality_control('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BEL		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is None
    # population
    assert data.geonames.quality_control('2801074	Breitfeld	Breitfeld		50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	BE		432	Europe/Brussels	2017-03-25') is None
    # alternatives
    result = data.geonames.quality_control('2867714	Munich	Munich	Monachium,Monaco di Baviera,München	48.13743	11.57549	P	PPLA	DE		02	091	09162	09162000	1260391		524	Europe/Berlin	2014-01-26')
    print(result)
    assert result is not None and result[0] == {'Monachium', 'Monaco di Baviera', 'München'}


def test_geonames_store():
    # init
    alternatives, canonical, infotuple = data.geonames.quality_control('2801074	Breitfeld	Breitfeld	Breitfeld,Breitfelds	50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25')

    # store code
    assert canonical not in data.geonames.codesdict
    data.geonames.store_codesdata(infotuple[0], canonical, alternatives)
    assert canonical in data.geonames.codesdict
    for alt in alternatives:
        assert alt in data.geonames.codesdict
    assert list(data.geonames.codesdict[canonical])[0] == infotuple[0]

    # store info
    assert infotuple[0] not in data.geonames.metainfo
    data.geonames.store_metainfo(infotuple)
    assert infotuple[0] in data.geonames.metainfo and '2801074' in data.geonames.metainfo
    data.geonames.store_metainfo(infotuple)

    # duplicate entry
    assert data.geonames.quality_control('2801074	Breitfeld	Breitfeld	Breitfeld,Breitfelds	50.26417	6.15389	P	PPL	BE		WAL	WLG	63	63067	0		432	Europe/Brussels	2017-03-25') is None


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
    geokelone.settings.FILTER_LEVEL = 'MINIMUM'
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-meta.dict')
    metainfo = data.load.geonames_meta(inputfile)
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-codes.dict')
    codes = data.load.geonames_codes(inputfile, metainfo)
    # control
    assert len(codes) == 5 and len(metainfo) == 9
    assert codes['Valwig'] == ['6553731', '2817894']
    # search
    results = geo.geocoding.search(['Aachen', 'Aachen'], codes, metainfo)
    assert len(results) == 1 and '3247449' in results
    results = geo.geocoding.search(['Mörsfeld'], codes, metainfo)
    assert len(results) == 1 and '2869159' in results
    results = geo.geocoding.search(['Valwig'], codes, metainfo)
    assert len(results) == 1 and '6553731' in results
    ## multi-word
    # 2
    results = geo.geocoding.search(['Öderquarter'], codes, metainfo)
    assert '2858070' not in results
    results = geo.geocoding.search(['Öderquarter', 'Moor'], codes, metainfo)
    assert len(results) == 1 and '2858070' in results
    # 3
    results = geo.geocoding.search(['It', 'was', 'in', 'Reichenbach', 'am', 'Heuberg', '.'], codes, metainfo)
    assert len(results) == 1 and '6555850' in results

    ##filter level
    geokelone.settings.FILTER_LEVEL = 'MAXIMUM'
    metainfo = {}
    codes = {}
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-meta.dict')
    metainfo = data.load.geonames_meta(inputfile)
    inputfile = path.join(TEST_DIR, 'data/dummy-geonames-codes.dict')
    codes = data.load.geonames_codes(inputfile, metainfo)
    # control
    assert len(codes) == 4 and len(metainfo) == 4


def test_wikipedia():
    assert data.wikipedia.find_coordinates('Wien', language='en') == (None, None)
    assert data.wikipedia.find_coordinates('Wien', language='de') == (48.208, 16.373)


def test_distances():
    assert geo.geocoding.haversine((53.4, 1.2), (61, 10.53)) == 1012.7688
    assert geo.geocoding.haversine((-53.466666, 1), (61, -3.33333)) == 12733.90603
    assert geo.geocoding.vincenty((53.4, 1.2), (61, 10.53)) == 1014.90503
    assert geo.geocoding.vincenty((-53.466666, 1), (61, -3.33333)) == 12697.86368


def test_geofind():
    test_metainfo = {\
                    '1':[47.13, 7.85, 'P', 'DE', 0],\
                    '2':[48.13, 7.85, 'P', 'DE', 2000],\
                    }
    test_codesdict = {\
                    'AAA':['1'],\
                    }
    assert geo.geocoding.geofind('AAA', test_codesdict, test_metainfo) is False



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
    assert geo.geocoding.disambiguate(['1', '2', '3'], 1, {'2': [-46.13, -8.85, 'P', 'ZZ', 1000], '3': [-45.13, -9.85, 'P', 'ZZ', 1000], '1': [47.13, 7.85, 'P', 'ZZ', 1000]}) == '1'


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
    assert len(results) == 7 and '10173868' in results
    # statistics
    assert geo.mapping.examine(results, 10) == (1, 9, 1)


def test_mapping():
    # point size normalization
    assert geo.mapping.normalize(5, 1, 10, 1, 10) == 5
    assert geo.mapping.normalize(1, 1, 5, 1, 100) == 1
    assert geo.mapping.normalize(100, 0, 200, 1, 10) == 5.5
    # random placement
    xval, yval = geo.mapping.random_placement()
    assert -30 <= xval <= 30
    assert -30 <= yval <= 30


    

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
    test_store_variants()
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
    test_distances()
    test_geodata_validators()
    test_mapping()
    test_draw_line()

    # geocoding functions
    test_disambiguate()
    test_rounds()



