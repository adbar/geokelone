#!/usr/bin/python3
# -*- coding: utf-8 -*-




MINLENGTH = 4
FILTER_LEVEL = 3
CONTEXT_THRESHOLD = 20


VERBOSITY = 'V'

LINESBOOL = False

DATEBOOL = False




DISAMBIGUATION_SETTING = { \
    'Vienna': { \
        'vicinity': set(['AT', 'BA', 'BG', 'CH', 'CZ', 'DE', 'HR', 'HU', 'IT', 'PL', 'RS', 'RU', 'SI', 'SK', 'UA']), \
        'reference': (float(48.2082), float(16.37169)), \
        }, \
    'Wittenberg': { \
        'vicinity': set(['AT', 'BE', 'CH', 'CZ', 'DK', 'FR', 'LU', 'NL', 'PL']), \
        'reference': (float(51.86666667), float(12.64333333)),
        }
}
STANDARD_SETTING = 'Wittenberg'





