``geokelone``
=============

.. image:: https://img.shields.io/pypi/v/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/pypi/l/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/pypi/pyversions/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/travis/adbar/geokelone.svg
    :target: https://travis-ci.org/adbar/geokelone

.. image:: https://img.shields.io/codecov/c/github/adbar/geokelone.svg
    :target: https://codecov.io/gh/adbar/geokelone


Work towards the integration of spatial and textual data processing tools into a modular software package which features preprocessing, geocoding, disambiguation and visualization. Construction of gazzetteers and basic text processing functions are included. The installation works best with recent Linux and Mac systems (see below for more details).

Current reference: Barbaresi, A. (2017). `Towards a toolbox to map historical text collections <https://hal.archives-ouvertes.fr/hal-01654526/document>`_, *Proceedings of 11th Workshop on Geographic Information Retrieval*, ACM, Heidelberg.


.. contents:: **Contents**
    :backlinks: none


Usage as a toolchain
----------------------


Bootstrapped geographic databases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data helpers are included to derive geographic data from existing sources such as Geonames, Wikipedia or Wikidata (all under CC BY licenses), see for example Geonames with country codes:

.. code-block:: python

    >>> from geokelone import data
    # decide countries for which Geonames information is downloaded
    >>> countries = ['dk', 'fi'] # 2-letter tld-style country code
    # go fetch the data
    >>> codesdict, metainfo = data.geonames.fetchdata(countries)
    # write files for further use
    >>> data.geonames.writefile(codesdict, 'geonames-codes.dict')
    >>> data.geonames.writefile(metainfo, 'geonames-meta.dict')


Extraction, disambiguation and mapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tutorial uses a file provided in the ``tests`` folder and the information gathered above to go from a tagged sentence to a map:

.. code-block:: python

    >>> from geokelone import data, geo, text
    # read from a tagged text (one token per line)
    >>> splitted = text.readfile.readtagged('tests/data/fontane-stechlin.tagged')
    # load default gazetteer info (Geonames, see above)
    >>> metainfo = data.load.geonames_meta('geonames-meta.dict')
    >>> codesdict = data.load.geonames_codes('geonames-codes.dict', metainfo)
    # search for place names and store a list of resolved toponyms with metadata
    >>> results = geo.geocoding.search(splitted, codesdict, metainfo)
    # write the results to a file
    >>> text.outputcontrol.writefile('results.tsv', results, dict())
    # load results from a file
    >>> results = data.load.results_tsv('results.tsv')
    # draw a map
    >>> geo.mapping.draw_map('testmap.png', results)


Usage of single components
--------------------------

Mapping
~~~~~~~

Requires a file containing results of a placename extraction. The minimal requirements are a toponym and coordinates, see the example file in the ``tests`` folder:

.. code-block:: python

    >>> from geokelone import data, geo
    >>> results = data.load.results_tsv('tests/data/dummy-results.tsv')
    >>> geo.mapping.draw_map('testmap1.png', results)

The map window can be configured using the ``settings.py`` file.


Extension and adaptation
------------------------


Special parameters
~~~~~~~~~~~~~~~~~~

Did you know there was a Jerusalem in Bavaria and a Leipzig in Ukraine?

A series of parameters can be set to affect both search and visualization, see ``settings.py`` file.

Allowed values for the filter level are ``MAXIMUM`` (conservative setting, recommended), ``MEDIUM`` and ``MINIMUM`` (better recall comes at a price).


Why curate special registers or gazetteers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even with a touch of filtering, the token "Berlin" in Geonames resolves to a place north of Germany with a population of 0, see map below:

.. image:: tests/example-wrong.png
    :align: center
    :alt: example


Custom registers
~~~~~~~~~~~~~~~~

The helper function in ``data.load.load_tsv()`` allow for additional registers to match particular needs, with particular levels (0 to 3), for example:

.. code-block:: python

    >>> from geokelone import data
    # read from a TSV-file with three columns: name, latitude, longitude
    >>> customized = data.load.load_tsv('file-X.tsv')
    # read from a CSV-file with optional level option (additional metadata)
    # four columns expected: name, canonical name, latitude, longitude
    >>> customized = data.load.load_csv('file-Y.csv', level=1)
    >>> results = geo.geocoding.search(splitted, codesdict, metainfo, customized)


Using information from Wikipedia/Wikidata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module includes helpers to navigate categories, for example the `World Heritage Sites in England <https://en.wikipedia.org/wiki/Category:World_Heritage_Sites_in_England>`_ or the `Cultural Landscapes of Japan <https://en.wikipedia.org/wiki/Category:Cultural_Landscapes_of_Japan>`_ and to fetch coordinates for a given list by querying Wikipedia.

.. code-block:: python

    >>> from geokelone.data import wikipedia
    # chained operations for a list of categories
    >>> wikipedia.process_todolist('mytodolist.txt', outputfile='solved.tsv', categories=True)
    # discover entries in a category
    >>> category_members = wikipedia.navigate_category('XYZ')
    # process them one by one
    >>> for member in category_members:
    >>>     lat, lon = wikipedia.find_coordinates(member)
    >>>     print(member, lat, lon)
    # change language code for search (default is 'en')
    >>> wikipedia.find_coordinates('Wien', language='de')
    (48.208, 16.373)

Integration
~~~~~~~~~~~

For language-independent solutions in the Python world, see `spacy <https://spacy.io/>`_ or `polyglot <https://github.com/aboSamoor/polyglot>`_.

API-based geocoding solutions for Python: `geopy <https://github.com/geopy/geopy>`_ and `geocoder <https://github.com/DenisCarriere/geocoder>`_.


Installation
------------

The instructions below have been tested on Linux with several system settings (see ``.travis.yml`` file). It works best with recent Linux and Mac systems and Python version >= 3.5.

The cartographic components may need to be installed separately, for detailed instructions please refer to the Cartopy `documentation <http://scitools.org.uk/cartopy/docs/latest/installing.html#installing>`_.

Unofficial Windows binaries for Python packages are `available here <https://www.lfd.uci.edu/~gohlke/pythonlibs/>`_.


Proj library
~~~~~~~~~~~~

The `proj library <https://github.com/OSGeo/proj.4/>`_ is needed. There are several ways to install it:

- From a package repository (preferably posterior to 2016)

  - there are several options (*libproj0* or *libproj9* or *libproj12*), to let the system decide:
  - ``apt-get install libproj-dev proj-data proj-bin``

- From source:

  a. ``wget http://download.osgeo.org/proj/proj-5.2.0.tar.gz``
  b. ``tar -xzvf proj-5.2.0.tar.gz``
  c. ``cd proj-5.2.0 && ./configure --prefix=/usr && make && sudo make install``

Other packages
~~~~~~~~~~~~~~

-  ``apt-get install libgeos-* libffi-dev libgdal-dev libxslt1-dev``

Python packages
~~~~~~~~~~~~~~~

Only Python3 (especially 3.4 onwards) is supported, although the scripts may work for Python 2.7.

Two options, from system repositories or through ``pip``:

- *python3-dev python3-shapely python3-gdal python3-matplotlib python3-pyproj python3-shapely*
- or simply ``pip3 install cairocffi GDAL matplotlib pyproj shapely``

For installation on Debian/Ubuntu simply follow the instructions (*before_install:*) in the ``travis.yml`` file

*Additional note on GDAL in case problems occur during installation:*

- ``gdal-config --version``
- ``sudo pip3 install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==2.2.3``


Cartopy install notes
~~~~~~~~~~~~~~~~~~~~~

Finally, *cartopy* can be installed:

- ``pip3 install Cython`` (if not installed already)
- ``pip3 install cartopy``
- or on newer systems: ``apt-get install python3-cartopy`` cf `<https://packages.ubuntu.com/source/zesty/python-cartopy>`_
- or see here: `<http://scitools.org.uk/cartopy/docs/latest/installing.html#installing>`_

Install this package
~~~~~~~~~~~~~~~~~~~~

Direct installation of the latest version over pip is possible (see `build status <https://travis-ci.org/adbar/geokelone>`_):

-  ``pip3 install git+https://github.com/adbar/geokelone.git``



Additional info
---------------

Why *geokelone*? `Because <https://en.wikipedia.org/wiki/Geochelone>`_.

**Work in progress**, see legacy page for more information: `<https://github.com/adbar/toponyms>`_

TODO
~~~~

- provide map configuration
- integrate named entity recognition tool from Python repositories
- add more import and export filters
- write more tests
- documentation


References
~~~~~~~~~~

Uses of the code base so far:

- Barbaresi, A. (2018). `Borderlands of text mapping: Experiments on Fontane's Brandenburg <https://hal.archives-ouvertes.fr/hal-01951880/document>`_. Proceedings of INF-DH-2018 workshop.
- Barbaresi, A. (2018). `A constellation and a rhizome: two studies on toponyms in literary texts <https://hal.archives-ouvertes.fr/hal-01775127/document>`_. In *Visual Linguistics*, Bubenhofer N. & Kupietz M. (Eds.), Heidelberg University Publishing, pp. 167-184.
- Barbaresi, A. (2018). `Toponyms as Entry Points into a Digital Edition: Mapping Die Fackel <https://hal.archives-ouvertes.fr/hal-01775122/document>`_. *Open Information Science*, 2(1), De Gruyter, pp.23-33.
- Barbaresi, A. (2018). `Placenames analysis in historical texts: tools, risks and side effects <https://hal.archives-ouvertes.fr/hal-01775119/document>`_. In *Proceedings of the Second Workshop on Corpus-Based Research in the Humanities (CRH-2)*, Dept. of Geoinformation, TU Vienna, pp. 25-34.
- Barbaresi, A. (2017). `Towards a toolbox to map historical text collections <https://hal.archives-ouvertes.fr/hal-01654526/document>`_, *Proceedings of 11th Workshop on Geographic Information Retrieval*, ACM, Heidelberg.
- Barbaresi, A. and Biber, H. (2016). `Extraction and Visualization of Toponyms in Diachronic Text Corpora <https://hal.archives-ouvertes.fr/hal-01348696/document>`_. In *Digital Humanities 2016: Book of Abstracts*, pp. 732-734.
- Barbaresi, A. (2016). `Visualisierung von Ortsnamen im Deutschen Textarchiv <https://halshs.archives-ouvertes.fr/halshs-01287931/document>`_. In *Proceedings of DHd 2016*, Digital Humanities im deutschprachigen Raum e.V. pp. 264-267.
