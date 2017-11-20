# -*- coding: utf-8 -*-
"""
Read input texts in several formats.
"""

# standard
import logging
import re

# own
from ..data import validators

# logging
logger = logging.getLogger(__name__)


# load all tokens
def readplain(filename, datesbool=False, datestok=False):
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

        # very basic tokenizer
        splitted = re.split(r'([^\w-]+)', text, flags=re.UNICODE) # [ .,;:]
        # build frequency dict
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
        return splitted


def readtok(filename, datesbool=False, datestok=False):
    """
    Read tokenized text from file (one token per line).
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        i = 0
        splitted = list()
        for line in inputfh:
            i += 1
            if i % 10000000 == 0:
                logger.info('tokens seen: %s', i)
            # control
            if validators.validate_tok(line) is False:
                logger.warning('line not valid: %s', line)
                continue
            # consider dates
            if datesbool is True:
                columns = re.split('\t', line)
                if columns[0] not in datestok:
                    datestok[columns[0]] = set()
                datestok[columns[0]].add(columns[1])
            # take only first columns
            if re.search('\t', line):
                token = re.split('\t', line)[0]
            else:
                token = line.strip()
            splitted.append(token)
        # build frequency dict
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
        return splitted


def readtagged(filename, datesbool=False, datestok=False):
    """
    Read tokenized and tagged text from file (one token per line, tab-separated values).
    """
    with open(filename, 'r', encoding='utf-8') as inputfh:
        i = 0
        splitted = list()
        for line in inputfh:
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
            if datesbool is True:
                if columns[0] not in datestok:
                    datestok[columns[0]] = set()
                datestok[columns[0]].add(columns[1])

            # take only lemmatized NEs
            if columns[1] == 'NE':
                splitted.append(columns[2])

        # build frequency dict
        #tokens = defaultdict(int)
        #for elem in splitted:
        #    tokens[elem] += 1
        return splitted


# numtokens = len(tokens)
# print ('types:', numtokens)
# print ('tokens:', len(splitted))
