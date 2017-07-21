#!/usr/bin/python3


from distutils.core import setup
# from setuptools import setup


def readme():
    with open('README.md') as readmefile:
        return readmefile.read()

setup(name='unnamed',
      version='0.1',
      description='to complete',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: XX License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='keywords',
      url='http://github.com/adbar/',
      author='Adrien Barbaresi',
      author_email='adrien.barbaresi@oeaw.ac.at',
      license='license',
      packages=['testmodule'],
      install_requires=[
          'exrex', 'requests'
      ],
     test_suite='nose.collector',
     tests_require=['nose'],
     include_package_data=True,
     zip_safe=False)
