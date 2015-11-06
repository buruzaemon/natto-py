.. natto-py documentation master file, created by
   sphinx-quickstart on Sun Dec 21 14:48:14 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

natto-py
========

What is natto-py?
-----------------
A package leveraging FFI (foreign function interface), ``natto-py`` combines
the Python_ programming language with MeCab_, the part-of-speech and
morphological analyzer for the Japanese language. No compiler is necessary, as
it is **not** a C extension. ``natto-py`` will run on Mac OS, Windows and
\*nix.

You can learn more about `natto-py at GitHub`_.

|license| |travis| |version| |pypi|

Requirements
-------------
``natto-py`` requires the following:

- An existing installation of `MeCab 0.996`_
- A system dictionary, like `mecab-ipadic`_ or `mecab-jumandic`_
- `cffi 0.8.6`_ or greater

The following Python versions are supported:

- `Python 2.7`_
- `Python 3.2`_
- `Python 3.3`_
- `Python 3.4`_
- `Python 3.5`_

Installation
------------
Install ``natto-py`` as you would any other Python package::

    $ pip install natto-py

This will automatically install the ``cffi`` package, which ``natto-py`` uses
to bind to the ``mecab`` library.



.. |version| image:: https://badge.fury.io/py/natto-py.svg
    :target: https://pypi.python.org/pypi/natto-py
.. |travis| image:: https://travis-ci.org/buruzaemon/natto-py.svg?branch=master
    :target: https://travis-ci.org/buruzaemon/natto-py
.. |pypi| image:: https://img.shields.io/pypi/dm/natto-py.svg
    :target: https://pypi.python.org/pypi/natto-py
.. |license| image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: _
.. _Python: http://www.python.org/
.. _MeCab: http://taku910.github.io/mecab/
.. _mecab-ipadic: http://taku910.github.io/mecab/#download
.. _mecab-jumandic: http://taku910.github.io/mecab/#download
.. _natto-py at GitHub: https://github.com/buruzaemon/natto-py
.. _MeCab 0.996: http://taku910.github.io/mecab/#download
.. _cffi 0.8.6: https://bitbucket.org/cffi/cffi
.. _Python 2.7: https://docs.python.org/dev/whatsnew/2.7.html 
.. _Python 3.2: https://docs.python.org/dev/whatsnew/3.2.html
.. _Python 3.3: https://docs.python.org/dev/whatsnew/3.3.html
.. _Python 3.4: https://docs.python.org/dev/whatsnew/3.4.html 
.. _Python 3.5: https://docs.python.org/dev/whatsnew/3.5.html 
.. _NLTK3's lead: https://github.com/nltk/nltk/wiki/Porting-your-code-to-NLTK-3.0
.. _Python with-statement: https://www.python.org/dev/peps/pep-0343/
.. _project Wiki: https://github.com/buruzaemon/natto-py/wiki 
.. _Partial parsing: http://taku910.github.io/mecab/partial.html
.. _Regular expression operations: https://docs.python.org/3/library/re.html
.. _re.finditer: https://docs.python.org/3/library/re.html#re.finditer
.. _project's notebooks directory: https://github.com/buruzaemon/natto-py/tree/master/notebooks
.. _git: http://git-scm.com/downloads
.. _check out the latest code at GitHub: https://github.com/buruzaemon/natto-py
.. _Browse the issue tracker: https://github.com/buruzaemon/natto-py/issues
.. _Sphinx: http://sphinx-doc.org/
.. _twine: https://github.com/pypa/twine
.. _unittest: http://pythontesting.net/framework/unittest/unittest-introduction/
.. _PyYAML: http://pyyaml.org/wiki/PyYAMLDocumentation
.. |copy| unicode:: 0xA9 .. copyright sign


.. toctree::
   :maxdepth: 2
 
   code


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

