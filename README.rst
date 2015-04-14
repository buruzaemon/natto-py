natto-py |version| |travis|
===========================
.. |version| image:: https://badge.fury.io/py/natto-py.svg
    :target: http://badge.fury.io/py/natto-py
.. |travis| image:: https://travis-ci.org/buruzaemon/natto-py.svg?branch=master
    :target: https://travis-ci.org/buruzaemon/natto-py
.. |pypi| image:: https://img.shields.io/pypi/dm/natto-py.svg
    :target: https://pypi.python.org/pypi/natto-py
.. |license| image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: 

What is natto-py?
-----------------
A package leveraging FFI (foreign function interface), ``natto-py`` combines
the Python_ programming language with MeCab_, the part-of-speech and
morphological analyzer for the Japanese language. No compiler is necessary, as
it is **not** a C extension. ``natto-py`` will run on Mac OS, Windows and
\*nix.

You can learn more about `natto-py at GitHub`_.

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

Installation
------------
Install ``natto-py`` as you would any other Python package::

    $ pip install natto-py

This will automatically install the ``cffi`` package, which ``natto-py`` uses
to bind to the ``mecab`` library.

Automatic Configuration
-----------------------
As long as the ``mecab`` (and ``mecab-config`` for \*nix and Mac OS)
executables are on your ``PATH``, ``natto-py`` does not require any explicit
configuration. 

- On \*nix and Mac OS, it queries ``mecab-config`` to discover the path to the ``libmecab.so`` or ``libmecab.dylib``, respectively.
- On Windows, it queries the Windows Registry to locate the MeCab installation folder.
- In order to convert character encodings to/from Unicode, ``natto-py`` will examine the charset of the ``mecab`` system dictionary.

Explicit configuration via MECAB_PATH and MECAB_CHARSET
-------------------------------------------------------
If ``natto-py`` for some reason cannot locate the ``mecab`` library,
or if it cannot determine the correct charset used internally by
``mecab``, then you will need to set the ``MECAB_PATH`` and ``MECAB_CHARSET``
environment variables. 

- Set the ``MECAB_PATH`` environment variable to the exact name/path to your ``mecab`` library.
- Set the ``MECAB_CHARSET`` environment variable to the ``charset`` character encoding used by your system dictionary.

e.g., for Mac OS::

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
    os.environ['MECAB_CHARSET']='utf-16'

Usage
-----
Here's a very quick guide to using ``natto-py``.

Instantiate a reference to the ``mecab`` library, and display some details::

    from natto import MeCab

    nm = MeCab()
    print(nm)

    # displays details about the MeCab instance
    <natto.mecab.MeCab
     pointer=<cdata 'mecab_t *' 0x000000000037AB40>,
     libpath="/usr/local/lib/libmecab.so",
     options={},
     dicts=[<natto.dictionary.DictionaryInfo
             pointer=<cdata 'mecab_dictionary_info_t *' 0x00000000003AC530>,
             filepath="/usr/local/lib/mecab/dic/ipadic/sys.dic",
             charset=utf8,
             type=0],
     version=0.996>

----

Display details about the ``mecab`` system dictionary used::

    sysdic = nm.dicts[0]
    print(sysdic)

    # displays the MeCab system dictionary info
    <natto.dictionary.DictionaryInfo
     pointer=<cdata 'mecab_dictionary_info_t *' 0x00000000003AC530>,
     filepath="/usr/local/lib/mecab/dic/ipadic/sys.dic",
     charset=utf8,
     type=0>

----

Parse Japanese text and send the MeCab result as a single string to
``stdout``::

    print(nm.parse('ピンチの時には必ずヒーローが現れる。'))

    # MeCab result as a single string
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

----

Next, try parsing the text with MeCab node parsing. A generator yielding the
MeCabNode instances lets you efficiently iterate over the output without first
materializing each and every resulting MeCabNode instance. The MeCabNode 
instances yielded allow access to more detailed information about each
morpheme.

Here we use a `Python with-statement`_ to automatically clean up after we 
finish node parsing with the MeCab tagger. This is the recommended approach
for using ``natto-py`` in a production environment::

    # Use a Python with-statement to ensure mecab_destroy is invoked
    #
    with MeCab() as nm:
        for n in nm.parse('ピンチの時には必ずヒーローが現れる。', as_nodes=True):
    ...     # ignore any end-of-sentence nodes
    ...     if not n.is_eos():
    ...         print('{}\t{}'.format(n.surface, n.cost))
    ...
    ピンチ    3348
    の        3722
    時        5176
    に        5083
    は        5305
    必ず    7525
    ヒーロー   11363
    が       10508
    現れる   10841
    。        7127

----

MeCab output formatting is extremely flexible and is highly recommended for
any serious natural language processing task. Rather than parsing the MeCab
output as a single, large string, use MeCab's ``--node-format`` option to 
customize the node's ``feature`` attribute.

This example formats the node ``feature`` to capture the following as a
comma-separated value:

- morpheme surface
- part-of-speech
- part-of-speech ID
- pronunciation

The ``-F`` short form of the ``--node-format`` option is used here::

    # MeCab options used:
    #
    # -F    ... short-form of --node-format
    # %m    ... morpheme surface
    # %f[0] ... part-of-speech
    # %h    ... part-of-speech id (ipadic)
    # %f[8] ... pronunciation
    #
    with MeCab('-F%m,%f[0],%h,%f[8]') as nm:
        for n in nm.parse('ピンチの時には必ずヒーローが現れる。', as_nodes=True):
    ...     # only normal nodes, ignore any end-of-sentence and unknown nodes
    ...     if n.is_nor():
    ...         print(n.feature)
    ...
    ピンチ,名詞,38,ピンチ
    の,助詞,24,ノ
    時,名詞,66,トキ
    に,助詞,13,ニ
    は,助詞,16,ワ
    必ず,副詞,35,カナラズ
    ヒーロー,名詞,38,ヒーロー
    が,助詞,13,ガ
    現れる,動詞,31,アラワレル
    。,記号,7,。


----

`Partial parsing`_ (制約付き解析), allows you to pass hints to MeCab on
how to tokenize morphemes when parsing. With boundary constraint parsing,
you can specify either a compiled ``re`` regular expression object or a
string to tell MeCab where the boundaries of a morpheme should be. Use the new
``boundary_constraints`` keyword. For hints on tokenization, please see
`Regular expression operations`_ and `re.finditer`_ in particular.

In the example below, we again use the ``-F`` short form of the
``--node-format`` option to capture the following in the node's ``feature``:

- morpheme surface
- node part-of-speech
- node status value

Note that any such morphemes captured will have node ``stat`` status of 1 (unknown)::

    with MeCab('-F%m,\s%f[0],\s%s') as nm:

        text = '心の中で3回唱え、 ヒーロー見参！ヒーロー見参！ヒーロー見参！'
        pattern = 'ヒーロー見参'

        for n in nm.parse(text, boundary_constraints=pattern, as_nodes=True):
    ...     print(n.feature)
    ...
    心, 名詞, 0
    の, 助詞, 0
    中, 名詞, 0
    で, 助詞, 0
    3, 名詞, 1
    回, 名詞, 0
    唱え, 動詞, 0
    、, 記号, 0
    ヒーロー見参, 名詞, 1
    ！, 記号, 0
    ヒーロー見参, 名詞, 1
    ！, 記号, 0
    ヒーロー見参, 名詞, 1
    ！, 記号, 0
    EOS


----

Learn More
----------
- Examples and more detailed information about ``natto-py`` can be found on the `project Wiki`_.
- Working code in IPython notebook form can be found under this `project's notebooks directory`_.
- `API documentation on Read the Docs`_.

Contributing to natto-py
------------------------
- Use git_ and `check out the latest code at GitHub`_ to make sure the
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
Copyright |copy| 2015, Brooke M. Fujita. All rights reserved. Please see
the ``LICENSE`` file for further details.

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
.. _NLTK3's lead: https://github.com/nltk/nltk/wiki/Porting-your-code-to-NLTK-3.0
.. _Python with-statement: https://www.python.org/dev/peps/pep-0343/
.. _Partial parsing: http://taku910.github.io/mecab/partial.html
.. _Regular expression operations: https://docs.python.org/3/library/re.html
.. _re.finditer: https://docs.python.org/3/library/re.html#re.finditer
.. _project Wiki: https://github.com/buruzaemon/natto-py/wiki 
.. _project's notebooks directory: https://github.com/buruzaemon/natto-py/tree/master/notebooks
.. _API documentation on Read the Docs: http://natto-py.readthedocs.org/en/master/
.. _git: http://git-scm.com/downloads
.. _check out the latest code at GitHub: https://github.com/buruzaemon/natto-py
.. _Browse the issue tracker: https://github.com/buruzaemon/natto-py/issues
.. _unittest: http://pythontesting.net/framework/unittest/unittest-introduction/
.. |copy| unicode:: 0xA9 .. copyright sign
