# -*- coding: utf-8 -*-
"""
Fixed settings for extraction and projection of toponyms (as is: European places in German texts).
"""


# compatibility
from __future__ import absolute_import, division, print_function, unicode_literals

# standard
import re
import sys

# external
import exrex

# own
from .. import settings
from . import validators



def expand(expression):
    """
    Use regex entry expansion to populate the register.
    """
    expresults = list(exrex.generate(expression))
    # no regex
    if len(expresults) == 1:
        results = list()
        results.append(expression)
        # German genitive form: if no s at the end of one component
        if not re.search(r's$', expression) and not re.search(r'\s', expression):
            temp = expression + 's'
            results.append(temp)
        return results
    # serialize
    else:
        return expresults


def load_tsv(filename):
    """
    Open a TSV file and load its content into memory.
    """
    dic = dict()
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            if validators.validate_tsv_registry(line) is False:
                print('# WARN: registry line not conform', line)
                continue
            line = line.strip()
            columns = re.split('\t', line)
            # sanity check
            if len(columns) == 3 and columns[1] is not None and columns[2] is not None:
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
                # append
                canonical = expansions[0]
                for variant in expansions:
                    dic[variant] = [columns[1], columns[2], canonical]
                    if settings.VERBOSITY == 'VVV':
                        print(variant, dic[variant])
    print(len(dic), 'entries found in registry', filename)
    return dic


def load_csv(filename):
    """
    Open a CSV file and load its content into memory.
    """
    dic = dict()
    with open(filename, 'r', encoding='utf-8') as inputfh:
        for line in inputfh:
            if validators.validate_tsv_registry(line) is False:
                print('# WARN: registry line not conform', line)
                continue
            line = line.strip()
            columns = re.split(',', line)
            if len(columns) == 4 and columns[2] is not None and columns[3] is not None:
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
                # canonical form?
                canonical = expansions[0]
                # process variants
                for variant in expansions:
                    # correction
                    if len(variant) > 1:
                        dic[variant] = [columns[2], columns[3], canonical]
                        if settings.VERBOSITY == 'VVV':
                            print(variant, dic[variant])

    print(len(dic), 'entries found in registry', filename)
    return dic


#if __name__ == "__main__":
# load infos level 0
#level0 = load_tsv('./rang0-makro.tsv')
# load infos level 1
#level1 = load_tsv('./rang1-staaten.tsv')
# load infos level 2
#level2 = load_csv('./rang2-regionen.csv')
# load infos level 3
#level3 = load_csv('./rang3-staedte.csv')


# geonames
### FILE MUST EXIST, use the preprocessing script provided
def loadmeta(filename): # './geonames-meta.dict'
    """
    Load metadata for a place name from Geonames.
    """
    metainfo = dict()
    try:
        with open(filename, 'r', encoding='utf-8') as inputfh:
            for line in inputfh:
                if validators.validate_geonames_registry(line) is False:
                    print('# WARN: geonames registry line not conform', line)
                    continue

                line = line.strip()
                columns = re.split('\t', line)

                # no empty places at filter levels 1 & 2
                if settings.FILTER_LEVEL == 1 or settings.FILTER_LEVEL == 2:
                    if columns[5] == '0':
                        continue
                # filter: skip elements
                if settings.FILTER_LEVEL == 1:
                    if columns[3] != 'A':
                        continue
                elif settings.FILTER_LEVEL == 2:
                    if columns[3] != 'A' and columns[3] != 'P':
                        continue
                # process
                metainfo[columns[0]] = list()
                for item in columns[1:]:
                    metainfo[columns[0]].append(item)
    except IOError:
        print('geonames data required at this stage')
        sys.exit(1)
    print('different names:', len(metainfo))
    return metainfo


# load codes (while implementing filter)
### FILE MUST EXIST, use the preprocessing script provided
def loadcodes(filename, metainfo): # './geonames-codes.dict'
    """
    Load codes from Geonames for matching and disambiguation purposes.
    """
    codesdict = dict()
    try:
        with open(filename, 'r', encoding='utf-8') as inputfh:
            for line in inputfh:
                if validators.validate_geonames_codes(line) is False:
                    print('# WARN: geonames code line not conform', line)
                    continue
                line = line.strip()
                columns = re.split('\t', line)
                # length filter
                if len(columns[0]) < settings.MINLENGTH:
                    continue
                # add codes
                for item in columns[1:]:
                    # depends from filter level
                    if item in metainfo:
                        if columns[0] not in codesdict:
                            codesdict[columns[0]] = list()
                        codesdict[columns[0]].append(item)
    except IOError:
        print('geonames data required at this stage')
        sys.exit(1)
    print('different codes:', len(codesdict))
    return codesdict
