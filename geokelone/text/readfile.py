# -*- coding: utf-8 -*-
"""
Read input texts in various formats.
"""

# standard
import logging
import re

# own
from ..data import validators

# logging
logger = logging.getLogger(__name__)


# load all tokens
def readplain(filename, datesbool=False, datestok=None):
    """
    Read raw text from file and tokenize in a crude way.
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        # splitted = inputfh.read().replace('\n', ' ').split()
        text = inputfh.read().replace('\n', ' ')
        ## validate: if text
        if validators.validate_text(text) is False:
            logger.warning('text format not valid')
            return None

        # very basic regex-tokenizer
        splitted = list()
        for item in re.split(r'([^\w-]+)', text, flags=re.UNICODE):
            if not re.match(r'^$|\s+', item):
                splitted.append(item.strip())

        # print ('types:', numtokens)
        logger.info('%s tokens found', len(splitted))
        return splitted


def readtok(filename, datesbool=False, datestok=None):
    """
    Read tokenized text from file (one token per line).
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        i = 0
        splitted = list()
        for line in inputfh:
            if len(line.strip()) < 1:
                continue
            i += 1
            if i % 10000000 == 0:
                logger.info('tokens seen: %s', i)
            # control
            if validators.validate_tok(line) is False:
                logger.warning('line not valid: %s', line)
                continue

            # consider dates
            #if datesbool is True:
            #    columns = re.split('\t', line)
            #    if columns[0] not in datestok:
            #        datestok[columns[0]] = set()
            #    datestok[columns[0]].add(columns[1])
            # take only first columns

            # discard further info
            #if re.search(r'[ \t\n\r\f\v]', line):
            #    token = re.split(r'[ \t\n\r\f\v]', line)[0]
            #else:
            #    token = line.strip()
            token = line.strip()
            splitted.append(token)

        # build frequency dict
        logger.info('%s tokens read', len(splitted))
        return splitted


def readtagged(filename, datesbool=False, datestok=None):
    """
    Read tokenized and tagged text from file (one token per line, tab-separated values).
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        i = 0
        splitted = list()
        for line in inputfh:
            if len(line.strip()) < 1:
                continue
            i += 1
            if i % 10000000 == 0:
                logger.info('tokens seen: %s', i)
            # control
            if validators.validate_tagged(line) is False:
                logger.warning('line not valid: %s', line)
                continue

            # split
            columns = re.split('\t', line.strip())

            # consider dates
            #if datesbool is True:
            #    if columns[0] not in datestok:
            #        datestok[columns[0]] = set()
            #    datestok[columns[0]].add(columns[1])

            # take only NEs (common tags)
            if columns[1] in ('I-LOC', 'NE', 'NPROP', 'PROPN'):
                # take column 3 (lemmata) is there is one
                if len(columns) == 3:
                    splitted.append(columns[2])
                else:
                    splitted.append(columns[0])

        # print ('types:', numtokens)
        logger.info('%s tokens read', len(splitted))
        return splitted


# def frequency_dict(splitted):
    # build frequency dict
    # tokens = defaultdict(int)
    # for elem in splitted:
        # tokens[elem] += 1
    # print ('types:', numtokens)
    # return tokens
