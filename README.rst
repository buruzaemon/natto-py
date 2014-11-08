natto-py
========

What is natto-py?
-----------------
``natto-py`` combines the Python_ programming language with MeCab_, the part-of-speech
and morphological analyzer for the Japanese language.

You can learn more about `natto-py at Bitbucket`_.

Requirements
-------------
``natto-py`` requires the following:

- `MeCab 0.996`_ along with an appropriate dictionary (`mecab-ipadic`_ recommended)
- `cffi 0.8.6`_

``natto-py`` is compatible with the following Python versions:

- `Python 2.7.8`_
- `Python 3.2.5`_
- `Python 3.3.5`_
- `Python 3.4.2`_

Installation
------------
Install ``natto-py`` with the following command::

    pip install natto-py

This will automatically install the ``cffi`` package, which natto-py uses to
bind to the ``mecab`` library.

Configuration
-------------
As long as the ``mecab`` (and ``mecab-config`` for \*nix and Mac OS) executables 
are on your ``PATH``, ``natto-py`` should just work without any explicit configuration.

If not, or if you are using a custom-built system dictionary located in a
non-default directory, or if you are using a non-default character encoding,
then you will need to explicitly set the ``MECAB_PATH`` and ``MECAB_CHARSET``
environment variables.

Set the ``MECAB_PATH`` environment variable to the exact name/path to your
``mecab`` library. Set the ``MECAB_CHARSET`` environment variable if you
compiled ``mecab`` and the related dictionary to use a non-default character
encoding.


Learn More
----------
You can read more about ``natto-py`` on the `project Wiki`_.

Contributing to natto-py
------------------------
- Use mercurial_ and `check out the latest code at Bitbucket`_ to make sure the 
  feature hasn't been implemented or the bug hasn't been fixed yet.
- `Browse the issue tracker`_ to make sure someone already hasn't requested it 
  and/or contributed it.
- Fork the project.
- Start a feature/bugfix branch.
- Commit and push until you are happy with your contribution.
- Make sure to add tests for it. This is important so I don't break it in a 
  future version unintentionally. I use unittest_ as it is very natural
  and easy-to-use.
- Please try not to mess with the ``setup.py``, ``CHANGELOG``, or version 
  files. If you must have your own version, that is fine, but please isolate 
  to its own commit so I can cherry-pick around it.

Changelog
---------
Please see the ``CHANGELOG`` for the release history.

Copyright
---------
Copyright |copy| 2014, Brooke M. Fujita. All rights reserved. Please see the
LICENSE file for further details. 

.. _Python: http://www.python.org/
.. _MeCab: http://mecab.googlecode.com/svn/trunk/mecab/doc/index.html
.. _mecab-ipadic: http://mecab.googlecode.com/files/mecab-ipadic-2.7.0-20070801.tar.gz
.. _natto-py at Bitbucket: https://bitbucket.org/buruzaemon/natto-py
.. _MeCab 0.996: http://code.google.com/p/mecab/downloads/list
.. _cffi 0.8.6: https://bitbucket.org/cffi/cffi
.. _Python 2.7.8: https://www.python.org/download/releases/2.7.8/
.. _Python 3.2.5: https://www.python.org/download/releases/3.2.5/
.. _Python 3.3.5: https://www.python.org/download/releases/3.3.5/
.. _Python 3.4.2: https://www.python.org/downloads/release/python-342/
.. _project Wiki: https://bitbucket.org/buruzaemon/natto-py/wiki/Home
.. _mercurial: http://mercurial.selenic.com/
.. _check out the latest code at Bitbucket: https://bitbucket.org/buruzaemon/natto-py/src
.. _Browse the issue tracker: https://bitbucket.org/buruzaemon/natto-py/issues?status=new&status=open
.. _unittest: http://pythontesting.net/framework/unittest/unittest-introduction/
.. |copy| unicode:: 0xA9 .. copyright sign