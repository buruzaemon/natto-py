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

This will automatically install the ``cffi`` package, which natto-py uses to
bind to the ``mecab`` library.

Configuration
-------------
Set the ``MECAB_PATH`` environment variable to the exact name/path to your
``mecab`` library.

e.g., for Mac OS X::

    export MECAB_PATH=/usr/local/Cellar/mecab/0.996/lib/libmecab.dylib 

e.g., for bash on UNIX/Linux::

    export MECAB_PATH=/usr/local/lib/libmecab.so

e.g., on Windows::

    set MECAB_PATH=C:\Program Files\MeCab\bin\libmecab.dll

e.g., from within a Python program::

    import os

    os.environ['MECAB_PATH']='/usr/local/lib/libmecab.so'

Usage
-----
Here's a very quick guide to using ``natto-py``.

Instantiate a reference to the ``mecab`` library, and display some details::

    >>> import natto
    >>> nm = natto.MeCab()

    >>> print nm
    <natto.api.MeCab 
     tagger="<cdata 'mecab_t *' 0x000000000037AB40>", 
     options="{}", 
     dicts=[<natto.api.DictionaryInfo 
             pointer=<cdata 'mecab_dictionary_info_t *' 0x00000000003AC530>, 
             type="0", 
             filename="/usr/local/lib/mecab/dic/ipadic/sys.dic",
             charset="utf8">], 
     version="0.996">

Display details about the ``mecab`` system dictionary used::

    >>> sysdic = nm.dicts[0]

    >>> print sysdic 
    <natto.api.DictionaryInfo 
     pointer=<cdata 'mecab_dictionary_info_t *' 0x00000000003AC530>, 
     type="0", 
     filename="/usr/local/lib/mecab/dic/ipadic/sys.dic", 
     charset="utf8">

    >>> print sysdic.is_sysdic()
    True

Parse Japanese text as a string, outputting to ``stdout``::

    >>> print nm.parse('ピンチの時には必ずヒーローが現れる。')
    ピンチ	名詞,一般,*,*,*,*,ピンチ,ピンチ,ピンチ
    の	助詞,連体化,*,*,*,*,の,ノ,ノ
    時	名詞,非自立,副詞可能,*,*,*,時,トキ,トキ
    に	助詞,格助詞,一般,*,*,*,に,ニ,ニ
    は	助詞,係助詞,*,*,*,*,は,ハ,ワ
    必ず	副詞,助詞類接続,*,*,*,*,必ず,カナラズ,カナラズ
    ヒーロー	名詞,一般,*,*,*,*,ヒーロー,ヒーロー,ヒーロー
    が	助詞,格助詞,一般,*,*,*,が,ガ,ガ
    現れる	動詞,自立,*,*,一段,基本形,現れる,アラワレル,アラワレル
    。	記号,句点,*,*,*,*,。,。,。
    EOS

Parse Japanese text using MeCab node parsing, using the more detailed
information related to each morphem::

    >>> nodes = nm.parse('ピンチの時には必ずヒーローが現れる。', as_nodes=True)

    >>> for n in nodes:
    ...     if not n.is_eos():
    ...         print "%s\t%s" % (n.surface, n.posid)
    ... 
    ピンチ	38
    の	24
    時	66
    に	13
    は	16
    必ず	35
    ヒーロー	38
    が	13
    現れる	31
    。	7


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