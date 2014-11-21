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

This will automatically install the ``cffi`` package, which ``natto-py`` uses to
bind to the ``mecab`` library.

Configuration
-------------
``natto-py`` should just work without any explicit configuration.

On \*nix and Mac OS, it queries ``mecab-config`` to discover the
path to the ``libmecab.so`` or ``libmecab.dylib``, respectively.

On Windows, it queries the Windows Registry to locate the MeCab 
installation folder.

In order to convert character encodings to/from Unicode, ``natto-py``
will examine the charset of the ``mecab`` system dictionary.

Therefore, as long as the ``mecab`` (and ``mecab-config`` for \*nix
and Mac OS) executables are on your ``PATH``, ``natto-py`` should
not require any explicit configuration.

If ``natto-py`` for some reason cannot locate the ``mecab`` library,
or if it cannot determine the correct charset used internally by
``mecab``, then you will need to set the ``MECAB_PATH`` and ``MECAB_CHARSET``
environment variables. 

Set the ``MECAB_PATH`` environment variable to the exact name/path to your
``mecab`` library. Set the ``MECAB_CHARSET`` environment variable if you
compiled ``mecab`` and the related dictionary to use a non-default character
encoding.

e.g., for Mac OS X::

    export MECAB_PATH=/usr/local/Cellar/mecab/0.996/lib/libmecab.dylib
    export MECAB_CHARSET=utf8

e.g., for bash on UNIX/Linux::

    export MECAB_PATH=/usr/local/lib/libmecab.so
    export MECAB_CHARSET=euc-jp

e.g., on Windows::

    set MECAB_PATH=C:\Program Files\MeCab\bin\libmecab.dll
    set MECAB_CHARSET=shift-jis

e.g., from within a Python program::

    import os

    os.environ['MECAB_PATH']='/usr/local/lib/libmecab.so'
    os.environ['MECAB_CHARSET']=utf-16

Usage
-----
Here's a very quick guide to using ``natto-py``.

Following `NLTK3's lead`_, ``natto-py`` requires all input
to be unicode, and always returns text as unicode.
On Python 2.7, you will have to decode/encode accordingly.

Instantiate a reference to the ``mecab`` library, and display some details::

    from natto import MeCab

    with MeCab() as nm:
        print(nm)

    # displays details about the MeCab instance
    <natto.mecab.MeCab
     lib="/usr/local/lib/libmecab.so",
     tagger=<cdata 'mecab_t *' 0x000000000037AB40>,
     options={},
     dicts=[<natto.dictionary.DictionaryInfo
             pointer=<cdata 'mecab_dictionary_info_t *' 0x00000000003AC530>,
             type="0",
             filename="/usr/local/lib/mecab/dic/ipadic/sys.dic",
             charset="utf8">],
     version="0.996">

Display details about the ``mecab`` system dictionary used::

        sysdic = nm.dicts[0]
        print(sysdic)

    # displays the MeCab system dictionary info
    <natto.dictionary.DictionaryInfo
     pointer=<cdata 'mecab_dictionary_info_t *' 0x00000000003AC530>,
     type=0,
     filename="/usr/local/lib/mecab/dic/ipadic/sys.dic",
     charset="utf8">


Parse Japanese text as a string, outputting to ``stdout``::

        print(nm.parse('ピンチの時には必ずヒーローが現れる。'))

    # MeCab's parsing as a string sent to stdout
    ピンチ    名詞,一般,*,*,*,*,ピンチ,ピンチ,ピンチ
    の      助詞,連体化,*,*,*,*,の,ノ,ノ
    時      名詞,非自立,副詞可能,*,*,*,時,トキ,トキ
    に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
    は      助詞,係助詞,*,*,*,*,は,ハ,ワ
    必ず    副詞,助詞類接続,*,*,*,*,必ず,カナラズ,カナラズ
    ヒーロー  名詞,一般,*,*,*,*,ヒーロー,ヒーロー,ヒーロー
    が      助詞,格助詞,一般,*,*,*,が,ガ,ガ
    現れる  動詞,自立,*,*,一段,基本形,現れる,アラワレル,アラワレル
    。      記号,句点,*,*,*,*,。,。,。
    EOS

Next, try parsing the text with MeCab node parsing, using the more detailed
information related to each morpheme::

        nodes = nm.parse('ピンチの時には必ずヒーローが現れる。', as_nodes=True)

        for n in nodes:
    ...     if not n.is_eos():
    ...         print('%s\t%s' % (n.surface, n.cost))
    ...
    ピンチ	3348
    の	3722
    時	5176
    に	5083
    は	5305
    必ず	7525
    ヒーロー	11363
    が	10508
    現れる	10841
    。	7127

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
.. _NLTK3's lead: https://github.com/nltk/nltk/wiki/Porting-your-code-to-NLTK-3.0
.. _project Wiki: https://bitbucket.org/buruzaemon/natto-py/wiki/Home
.. _mercurial: http://mercurial.selenic.com/
.. _check out the latest code at Bitbucket: https://bitbucket.org/buruzaemon/natto-py/src
.. _Browse the issue tracker: https://bitbucket.org/buruzaemon/natto-py/issues?status=new&status=open
.. _unittest: http://pythontesting.net/framework/unittest/unittest-introduction/
.. |copy| unicode:: 0xA9 .. copyright sign
