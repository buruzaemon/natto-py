natto-py
========

What is natto-py?
-----------------
natto-py combines the Python_ programming language with MeCab_, the part-of-speech
and morphological analyzer for the Japanese language.

You can learn more about `natto-py at Bitbucket`_.

Requirements
-------------
natto-py requires the following:

- `MeCab 0.996`_ along with an appropriate dictionary (`mecab-ipadic`_ recommended)
- `cffi 0.8.6`_

natto-py is compatible with the following Python versions:

- `Python 2.7.8`_
- `Python 3.2.5`_
- `Python 3.3.5`_
- `Python 3.4.2`_

Installation
------------
Install natto-py with the following command::

    pip install natto-py

This will automatically install the ``cffi`` package, which natto-py uses to
bind to the ``mecab`` library.
