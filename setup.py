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
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        #'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python',
        #'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        #'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Linguistic',
        #'License :: OSI Approved :: XX License',

      ],
      keywords='keywords',
      url='http://github.com/adbar/',
      author='Adrien Barbaresi',
      author_email='adrien.barbaresi@oeaw.ac.at',
      license='license',
      packages=['testmodule'],
      # packages=find_packages(exclude=['tests']),
      install_requires=[
          'exrex', 'requests'
      ],
    # install_requires=get_dependencies(),
     test_suite='nose.collector',
     tests_require=['nose'],
     include_package_data=True,
     zip_safe=False,
)
