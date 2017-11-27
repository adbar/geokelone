# -*- coding: utf-8 -*-
"""
Fixed settings for extraction and projection of toponyms (as is: European places in German texts).
"""




MINLENGTH = 4
FILTER_LEVEL = 3 # was 3
CONTEXT_THRESHOLD = 20

LANGUAGE = 'DE' # 2-letter language code


VERBOSITY = 'V'

LINESBOOL = False

DATEBOOL = False


## registers provided or not
# CUSTOM_REGISTERS = True


## dependent on language and text type
LOCALE = 'de_DE.UTF-8'

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




## coordinate frame suitable for Central Europe
FIXED_FRAME = True
EASTMOST = 25
WESTMOST = 2.5 # for Europe: -10
NORTHMOST = 62.5 # for Europe: 65
SOUTHMOST = 42.5 # for Europe: 35
