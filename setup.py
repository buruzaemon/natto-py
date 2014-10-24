# -*- coding: utf-8 -*-
from setuptools import setup
import codecs
from os import path

# Get the long description from the relevant file
with codecs.open(path.join(path.abspath(path.dirname(__file__)), 'README.md'),
                 encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name='natto-py',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.1',

    description='A Tasty Python Binding with MeCab',
    long_description=LONG_DESC,

    # The project's main homepage.
    url='https://bitbucket.org/buruzaemon/natto-py',

    # Author details
    author='Brooke M. Fujita',
    author_email='buruzaemon@gmail.com',

    # Choose your license
    license='BSD',

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Japanese',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='mecab japanese morphological analyzer nlp 形態素解析',

    packages=['natto'],

    zip_safe=False
)
