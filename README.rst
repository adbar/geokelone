geokelone: work in progress
==============================================


.. image:: https://img.shields.io/pypi/v/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/pypi/l/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/pypi/pyversions/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/pypi/status/geokelone.svg
    :target: https://pypi.python.org/pypi/geokelone

.. image:: https://img.shields.io/travis/adbar/geokelone.svg
    :target: https://travis-ci.org/adbar/geokelone

# .. image:: https://codecov.io/gh/adbar/geokelone/branch/master/graph/badge.svg
#    :target: https://codecov.io/gh/adbar/geokelone


About
-----

*work in progress*


Why disambiguate?
~~~~~~~~~~~~~~~~~

Did you know there was a Jerusalem in Bavaria and a Leipzig in Ukraine?


Why curate special registers or gazetteers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Even with a touch of filtering, the token "Berlin" in Geonames is a place north of Germany with 0 inhabitants (see map below [add image]).



Installation
------------

Cartopy install notes
~~~~~~~~~~~~~~~~~~~~~

Under Linux:
- https://github.com/OSGeo/proj.4/ is needed: libproj0 or libproj9 or libproj12
- ``apt-get install libgeos-* libgeos-dev libffi-dev``
- packages available directly: libxslt1-dev python3-dev python3-shapely python3-gdal python3-pyproj

And/or through python pip:
- ``pip3 install cairocffi, pyproj, shapely``

Finally:
- ``pip3 install cartopy``
- or see here: `<http://scitools.org.uk/cartopy/docs/latest/installing.html#installing>`_

``pip install git+https://github.com/adbar/geokelone.git``


Proof of concept
----------------

see ``test/...`` *work in progress*

.. code-block:: python

    >>> import geokelone
    >>>


TODO
----

- add import and export filters
- write more tests
- documentation



Integration
-----------

For a language-independent solution in the Python world, I would suggest `<https://github.com/aboSamoor/polyglot>`_



References
----------

Previous uses of parts of the code:

- Barbaresi, A. (2016). `Visualisierung von Ortsnamen im Deutschen Textarchiv <https://halshs.archives-ouvertes.fr/halshs-01287931/document>`_. In DHd 2016, pages 264-267. Digital Humanities im deutschprachigen Raum eV.
- Barbaresi, A. and Biber, H. (2016). `Extraction and Visualization of Toponyms in Diachronic Text Corpora <https://hal.archives-ouvertes.fr/hal-01348696/document>`_. In Digital Humanities 2016, pages 732-734.
- Barbaresi, A. (2017). `Toponyms as Entry Points into a Digital Edition: Mapping Die Fackel <https://dh2017.adho.org/abstracts/209/209.pdf>`_. In Digital Humanities 2017, pages 159-161.

Legacy page, see for more information: `<https://github.com/adbar/toponyms>`_
