# -*- coding: utf-8 -*-
import codecs
import os
import sys
from os import path
from setuptools import setup

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

info = path.join(path.abspath(os.getcwd()), 'natto', 'version.py')
exec(open(info).read())

with codecs.open(path.join(os.getcwd(), 'README.rst'),
                 encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name='natto-py',

    version=__version__,

    description=('A Tasty Python Binding with MeCab'
                 '(FFI-based, no SWIG or compiler necessary)'),
    long_description=LONG_DESC,
    long_description_content_type='text/x-rst',

    url='https://github.com/buruzaemon/natto-py',

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
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Japanese',

        'License :: OSI Approved :: BSD License',

        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords=' '.join(['MeCab',
                       '和布蕪',
                       '納豆',
                       'Japanese morphological analyzer',
                       'NLP',
                       '形態素解析',
                       '自然言語処理',
                       'FFI',
                       'binding',
                       'バインディング']),

    packages=['natto', 'tests'],

    install_requires=['cffi'],

    zip_safe=False,

    test_suite="tests.test_suite",

    **extra
)

