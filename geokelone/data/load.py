# -*- coding: utf-8 -*-
"""
Fixed settings for extraction and projection of toponyms (as is: European places in German texts).
"""


# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

# standard
import logging
import re
import sys

# external
import exrex
# from sqlitedict import SqliteDict

# own
from .. import settings
from . import validators

# logging
logger = logging.getLogger(__name__)

# DB
# DBPATH = './metainfo.sqlite'


def expand(expression):
    """
    Use regex entry expansion to populate the register.
    """
    expresults = list(exrex.generate(expression))
    # no regex
    if len(expresults) == 1:
        results = list()
        results.append(expression)
        if settings.LANGUAGE == 'DE':
            # German genitive form: if no s at the end of one component
            if not re.search(r's$', expression) and not re.search(r'\s', expression):
                temp = expression + 's'
                results.append(temp)
        return results
    # serialize
    else:
        return expresults


def store_variants(expanded, columns, level):
    """
    Stores variants and metadata in a dictionary.
    """
    # init
    dic = dict()
    canonical = expanded[0]
    lat, lon = columns[-2], columns[-1]
    # logger.debug('%s %s %s %s', canonical, expanded, columns, level)
    # loop
    for variant in expanded:
        # verbosity
        logger.debug('seen variant of %s : %s', canonical, variant) # , dic[variant]
        # control and store
        if validators.validate_entry(variant) is False:
            logger.debug('refused: %s', variant)
            continue
        if variant in dic:
            if dic[variant]['level'] > level:
                logger.warning('key discarded: %s %s', variant, level)
            #elif dic[variant]['level'] == level:
            #    logger.warning('duplicate entry: %s %s', variant, level)
            #    dic[variant]['values'] = (lat, lon, canonical)
            else:
                dic[variant]['values'] = (lat, lon, canonical)
        else:
            dic[variant] = dict()
            dic[variant]['values'] = (lat, lon, canonical)
            dic[variant]['level'] = level
    # finish
    logger.debug('%s', dic)
    return dic


def load_tsv(filename, level=0):
    """
    Open a TSV file and load its content into memory. Requires a level.
    """
    # init
    dic = dict()
    if not isinstance(level, int):
        logger.error('level is not an int: %s', level)
        return dic
    # read
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            line = line.strip()
            columns = re.split('\t', line)
            # sanity check
            if validators.validate_tsv_registry(columns) is False:
                continue
            # process
            expansions = list()
            # strip
            for item in columns:
                item = item.strip()
            # historical names
            if re.search(r';', columns[0]):
                variants = re.split(r';', columns[0])
                # add to list, name checked later
                for item in variants:
                    expansions.extend(expand(item))
            else:
                # add to list, name checked later
                expansions.extend(expand(columns[0]))
            # canonical form?
            canonical = expansions[0]
            # process variants
            dic.update(store_variants(expansions, columns, level))

    logger.info('%s entries found in registry %s', len(dic), filename)
    return dic


def load_csv(filename, level=0):
    """
    Open a CSV file and load its content into memory.
    """
    # init
    dic = dict()
    if not isinstance(level, int):
        logger.error('level is not an int: %s', level)
        return dic
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            line = line.strip()
            columns = re.split(',', line)
            # sanity check
            if validators.validate_csv_registry(columns) is False:
                continue
            # process
            expansions = list()
            # strip
            for item in columns:
                item = item.strip()
            # historical names
            if re.search(r';', columns[0]):
                variants = re.split(r';', columns[0])
                for item in variants:
                    expansions.extend(expand(item))
            else:
                expansions.extend(expand(columns[0]))
            # current names
            if re.search(r';', columns[1]):
                variants = re.split(r';', columns[1])
                for item in variants:
                    expansions.extend(expand(item))
            else:
                expansions.extend(expand(columns[1]))
            # process variants
            dic.update(store_variants(expansions, columns, level))

    logger.info('%s entries found in registry %s', len(dic), filename)
    return dic


# geonames
### FILE MUST EXIST, use the preprocessing script provided
def geonames_meta(filename):
    """
    Load metadata for a place name from Geonames.
    """
    metainfo = dict()
    try:
        with open(filename, 'r', encoding='utf-8') as inputfh: #, SqliteDict(DBPATH) as metainfo:
            for line in inputfh:
                line = line.strip()
                columns = re.split('\t', line)
                if validators.validate_geonames_registry(columns) is False:
                    continue
                # no empty places at filter levels 1 & 2
                if settings.FILTER_LEVEL == 'MAXIMUM' or settings.FILTER_LEVEL == 'MEDIUM':
                    if columns[5] == '0':
                        continue
                # filter: skip elements
                if settings.FILTER_LEVEL == 'MAXIMUM':
                    if columns[3] != 'A':
                        continue
                elif settings.FILTER_LEVEL == 'MEDIUM':
                    if columns[3] != 'A' and columns[3] != 'P':
                        continue
                # process
                ##metainfo[columns[0]] = columns[1:]
                metainfo[columns[0]] = list()
                for item in columns[1:]:
                    metainfo[columns[0]].append(item)
    except IOError:
        logger.error('geonames data or empty dictionary object required at this stage')
        sys.exit(1)
    logger.info('different names: %s', len(metainfo))
    # metainfo.commit()
    # logger.info('changes committed to DB: %s', len(metainfo))
    return metainfo


# load codes (while implementing filter)
### FILE MUST EXIST, use the preprocessing script provided
def geonames_codes(filename, metainfo):
    """
    Load codes from Geonames for matching and disambiguation purposes.
    """
    codesdict = dict()
    try:
        with open(filename, 'r', encoding='utf-8') as inputfh:
            for line in inputfh:
                line = line.strip()
                columns = re.split('\t', line)
                if validators.validate_geonames_codes(columns) is False:
                    continue
                # add codes
                if len(columns) > 2:
                    ids = columns[1:]
                else:
                    ids = list()
                    ids.append(columns[1])
                # load
                for item in ids:
                    # depends from filter level
                    if item in metainfo:
                        if columns[0] not in codesdict:
                            codesdict[columns[0]] = list()
                        codesdict[columns[0]].append(item)
    except IOError:
        logger.error('geonames data or empty dictionary object required at this stage')
        sys.exit(1)
    logger.info('different codes: %s', len(codesdict))
    return codesdict


def results_tsv(filename):
    """
    Open a TSV file containing geoparsing results and load its content into memory.
    """
    # init
    results = dict()
    # read
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            line = line.strip()
            columns = re.split('\t', line)
            # validate
            if validators.validate_result(columns) is False:
                continue
            # store
            results[columns[0]] = columns[1:]

    logger.info('%s entries found in results file %s', len(results), filename)
    return results
