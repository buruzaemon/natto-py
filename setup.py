# -*- coding: utf-8 -*-
from setuptools import setup
import codecs
from os import path
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

with codecs.open(path.join(path.abspath(path.dirname(__file__)), 'README.rst'),
                 encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name='natto-py',

    version='0.0.3',

    description=' '.join(['A Tasty Python Binding with MeCab',
                          '(FFI-based, no SWIG or compiler necessary)']),
    long_description=LONG_DESC,

    url='https://bitbucket.org/buruzaemon/natto-py',

    author='Brooke M. Fujita',
    author_email='buruzaemon@gmail.com',

    license='BSD',

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Japanese',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords=' '.join(['mecab',
                       '和布蕪',
                       'japanese morphological analyzer',
                       'nlp',
                       '形態素解析',
                       '自然言語処理']),

    packages=['natto', 'tests' ],

    install_requires=['cffi'],

    zip_safe=False,

    test_suite="tests.test_suite",
    
    use_2to3=True
    
)
