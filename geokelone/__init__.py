"""
geokelone
integrates spatial and textual data processing tools into a modular software package which features preprocessing, geocoding, disambiguation and visualization
"""


## meta

__title__ = 'geokelone'
__version__ = '0.1'
__license__ = 'GNU GPL v3'
__author__ = 'Adrien Barbaresi'
__copyright__ = 'Copyright 2017, Adrien Barbaresi'


__all__ = [
    'data',
    'geo',
    'text',
]


## logging best practices
# http://docs.python-guide.org/en/latest/writing/logging/
# https://github.com/requests/requests/blob/master/requests/__init__.py

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logging.getLogger(__name__).addHandler(NullHandler())



# from codecs import open # python2




# from . import geo
# from . import text
# from . import *
# import .settings


