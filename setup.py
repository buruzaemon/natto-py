# -*- coding: utf-8 -*-
from setuptools import setup
import codecs
from os import path

with codecs.open(path.join(path.abspath(path.dirname(__file__)), 'README.rst'),
                 encoding='utf-8') as f:
    LONG_DESC = f.read()

setup(
    name='natto-py',

    version='0.0.2',

    description='A Tasty Python Binding with MeCab',
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
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Text Processing :: Linguistic',
        'Natural Language :: Japanese',

        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    keywords='mecab japanese morphological analyzer nlp 形態素解析 自然言語処理',

    packages=['natto'],

    install_requires=['cffi'],

    zip_safe=False,
    
    test_suite="tests"
)
