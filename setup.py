#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description here.
http://github.com/adbar/geokelone
"""

from codecs import open # python2
import os
from setuptools import setup # find_packages


here = os.path.abspath(os.path.dirname(__file__))
packages = ['geokelone']


def readme():
    with open(os.path.join(here, 'README.rst'), 'r', 'utf-8') as readmefile:
        return readmefile.read()

setup(name='geokelone',
      version='0.1',
      description='to complete',
      long_description=readme(),
      classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        #'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords=['keywords',],
      url='http://github.com/adbar/geokelone',
      author='Adrien Barbaresi',
      author_email='adrien.barbaresi@oeaw.ac.at',
      license='GPLv3+',
      packages=packages,
      include_package_data=True,
      install_requires=[
      #    'adjustText',
          'cartopy',
          'cairocffi',
          'exrex',
          'requests',
          'pyproj',
          'shapely',
      ],
     # install_requires=get_dependencies(),
     tests_require=['pytest', 'tox'],
     zip_safe=False,
)
