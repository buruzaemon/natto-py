natto-py
========

A Tasty Python Binding with MeCab

What is natto-py?
-----------------
natto combines the Python_ programming language with MeCab_, the part-of-speech
and morphological analyzer for the Japanese language.

You can learn more about `natto-py at Bitbucket`_.

Requirements
-------------
natto-py requires the following:

- `MeCab 0.996`_
- `cffi 0.8.6`_
- `Python 2.7.8`_

Installation
------------
Install natto-py with the following command::

    pip install natto-py

This will automatically install the ```cffi``` package, which natto-py uses to
bind to the ```mecab``` library.

Configuration
-------------
Set the `MECAB_PATH` environment variable to the exact name/path to your
```mecab``` library.

e.g., for Mac OS X::

    export MECAB_PATH=/usr/local/Cellar/mecab/0.996/lib/libmecab.dylib 

e.g., for bash on UNIX/Linux::

    export MECAB_PATH=/usr/local/lib/libmecab.so

e.g., on Windows::

    set MECAB_PATH=C:\Program Files\MeCab\bin\libmecab.dll

e.g., from within a Python program::

    import os

    os.environ['MECAB_PATH']='/usr/local/lib/libmecab.so'


Changelog
---------
Please see the CHANGELOG for the release history.

Copyright
---------
Copyright |copy| 2014, Brooke M. Fujita. All rights reserved. Please see the
LICENSE file for further details. 

.. _Python: http://www.python.org/
.. _MeCab: http://mecab.googlecode.com/svn/trunk/mecab/doc/index.html
.. _natto-py at Bitbucket: https://bitbucket.org/buruzaemon/natto-py
.. _MeCab 0.996: http://code.google.com/p/mecab/downloads/list
.. _cffi 0.8.6: https://bitbucket.org/cffi/cffi
.. _Python 2.7.8: https://www.python.org/download/releases/2.7.8/
.. |copy| unicode:: 0xA9 .. copyright sign