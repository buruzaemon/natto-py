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

|version| |pyversions| |license| |travis| |readthedocs|

Requirements
------------
``natto-py`` requires the following:

- An existing installation of `MeCab 0.996`_
- A system dictionary, like `IPA`_, `Juman`_ or `Unidic`_
- `cffi 0.8.6`_ or greater

The following Python versions are supported:

- `Python 2.7`_
- `Python 3.2`_
- `Python 3.3`_
- `Python 3.4`_
- `Python 3.5`_
- `Python 3.6`_
- `Python 3.7`_
- `Python 3.8`_

Installation
------------
Install ``natto-py`` as you would any other Python package:

.. code-block:: bash

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

e.g., for Mac OS:

.. code-block:: bash

    export MECAB_PATH=/usr/local/Cellar/mecab/0.996/lib/libmecab.dylib
    export MECAB_CHARSET=utf8

e.g., for bash on UNIX/Linux:

.. code-block:: bash

    export MECAB_PATH=/usr/local/lib/libmecab.so
    export MECAB_CHARSET=euc-jp

e.g., on Windows:

.. code-block:: bat

    set MECAB_PATH=C:\Program Files\MeCab\bin\libmecab.dll
    set MECAB_CHARSET=shift-jis

e.g., from within a Python program:

.. code-block:: python

    import os

    os.environ['MECAB_PATH']='/usr/local/lib/libmecab.so'
    os.environ['MECAB_CHARSET']='utf-16'

Usage
-----
Here's a very quick guide to using ``natto-py``.

Instantiate a reference to the ``mecab`` library, and display some details:

.. code-block:: python

    from natto import MeCab

    nm = MeCab()
    print(nm)

    # displays details about the MeCab instance
    <natto.mecab.MeCab
     model=<cdata 'mecab_model_t *' 0x801c16300>,
     tagger=<cdata 'mecab_t *' 0x801c17470>,
     lattice=<cdata 'mecab_lattice_t *' 0x801c196c0>,
     libpath="/usr/local/lib/libmecab.so",
     options={},
     dicts=[<natto.dictionary.DictionaryInfo
             dictionary='mecab_dictionary_info_t *' 0x801c19540>,
             filepath="/usr/local/lib/mecab/dic/ipadic/sys.dic",
             charset=utf8,
             type=0],
     version=0.996>

----

Display details about the ``mecab`` system dictionary used:

.. code-block:: python

    sysdic = nm.dicts[0]
    print(sysdic)

    # displays the MeCab system dictionary info
    <natto.dictionary.DictionaryInfo
     dictionary='mecab_dictionary_info_t *' 0x801c19540>,
     filepath="/usr/local/lib/mecab/dic/ipadic/sys.dic",
     charset=utf8,
     type=0>

----

Parse Japanese text and send the MeCab result as a single string to
``stdout``:

.. code-block:: python

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
for using ``natto-py`` in a production environment:

.. code-block:: python

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
output as a single, large string, use MeCab's ``--node-format`` option
(short form ``-F``) to customize the node's ``feature`` attribute.

- morpheme surface
- part-of-speech
- part-of-speech ID
- pronunciation

It is good practice when using ``--node-format`` to also specify node 
formatting in the case where the morpheme cannot be found in the dictionary,
by using ``--unk-format`` (short form ``-U``).

This example formats the node ``feature`` to capture the items above as a
comma-separated value:

.. code-block:: python

    # MeCab options used:
    #
    # -F    ... short-form of --node-format
    # %m    ... morpheme surface
    # %f[0] ... part-of-speech
    # %h    ... part-of-speech id (ipadic)
    # %f[8] ... pronunciation
    # 
    # -U    ... short-form of --unk-format
    #           output ?,?,?,? for morphemes not in dictionary
    #
    with MeCab(r'-F%m,%f[0],%h,%f[8]\n -U?,?,?,?\n') as nm:
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
how to tokenize morphemes when parsing. Most useful are boundary constraint
parsing and feature constraint parsing.

With boundary constraint parsing, you can specify either a compiled ``re``
regular expression object or a string to tell MeCab where the boundaries of
a morpheme should be. Use the ``boundary_constraints`` keyword. For hints on
tokenization, please see `Regular expression operations`_ and `re.finditer`_
in particular.

This example uses the ``-F`` node-format option to customize the resulting
``MeCabNode`` feature attribute to extract:

- ``%m`` - morpheme surface
- ``%f[0]`` - node part-of-speech
- ``%s`` - node ``stat`` status value, 1 is ``unknown``

Note that any such morphemes captured will have node ``stat`` status of 1 (unknown):

.. code-block:: python

    import re

    with MeCab(r'-F%m,\s%f[0],\s%s\n') as nm:

        text = '俺は努力したよっ？ お前の10倍、いや100倍1000倍したよっ！'
        
        # capture 10倍, 100倍 and 1000倍 as single parts-of-speech
        pattern = re.compile('10+倍') 

        for n in nm.parse(text, boundary_constraints=pattern, as_nodes=True):
    ...     print(n.feature)
    ...
    俺, 名詞, 0
    は, 助詞, 0
    努力, 名詞, 0
    し, 動詞, 0
    たよっ, 動詞, 0
    ？, 記号, 0
    お前, 名詞, 0
    の, 助詞, 0
    10倍, 名詞, 1
    、, 記号, 0
    いや, 接続詞, 0
    100倍, 名詞, 1
    1000倍, 名詞, 1
    し, 動詞, 0
    たよっ, 動詞, 0
    ！, 記号, 0
    EOS

With feature constraint parsing, you can provide instructions to MeCab
on what feature to use for a matching morpheme. Use the 
``feature_constraints`` keyword to pass in a ``tuple`` containing elements
that themselves are ``tuple`` instances with a specific morpheme (str) 
and a corresponding feature (str), in order of constraint precedence:

.. code-block:: python

    with MeCab(r'-F%m,\s%f[0],\s%s\n') as nm:

        text = '心の中で3回唱え、 ヒーロー見参！ヒーロー見参！ヒーロー見参！'
        features = (('ヒーロー見参', '感動詞'),)

        for n in nm.parse(text, feature_constraints=features, as_nodes=True):
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
    ヒーロー見参, 感動詞, 1
    ！, 記号, 0
    ヒーロー見参, 感動詞, 1
    ！, 記号, 0
    ヒーロー見参, 感動詞, 1
    ！, 記号, 0
    EOS


----

Learn More
----------
- Examples and more detailed information about ``natto-py`` can be found on the `project Wiki`_.
- Working code in Jupyter notebook form can be found under this `project's notebooks directory`_.
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
  future version unintentionally.
- Please try not to mess with the ``setup.py``, ``CHANGELOG``, or version
  files. If you must have your own version, that is fine, but please isolate
  to its own commit so I can cherry-pick around it.
- This project uses the following packages for development:

  - Sphinx_ for document generation
  - twine_ for secure uploads during release
  - unittest_ for unit tests, as it is very natural and easy-to-use
  - PyYAML_ for data loading during tests

Changelog
---------
Please see the ``CHANGELOG`` for the release history.

Copyright
---------
Copyright |copy| 2019, Brooke M. Fujita. All rights reserved. Please see
the ``LICENSE`` file for further details.

.. |version| image:: https://badge.fury.io/py/natto-py.svg
    :target: https://pypi.python.org/pypi/natto-py
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/natto-py.svg?style=flat
.. |travis| image:: https://travis-ci.org/buruzaemon/natto-py.svg?branch=master
    :target: https://travis-ci.org/buruzaemon/natto-py
.. |license| image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: _
.. |readthedocs| image:: https://readthedocs.org/projects/natto-py/badge/?version=master
    :target: http://natto-py.readthedocs.org/en/master/?badge=master
    :alt: Documentation Status
.. _Python: http://www.python.org/
.. _MeCab: http://taku910.github.io/mecab/
.. _IPA: http://taku910.github.io/mecab/#download
.. _Juman: http://taku910.github.io/mecab/#download
.. _Unidic: http://taku910.github.io/mecab/#download
.. _natto-py at GitHub: https://github.com/buruzaemon/natto-py
.. _MeCab 0.996: http://taku910.github.io/mecab/#download
.. _cffi 0.8.6: https://bitbucket.org/cffi/cffi
.. _Python 2.7: https://docs.python.org/2.7/whatsnew/2.7.html 
.. _Python 3.2: https://docs.python.org/3.2/whatsnew/3.2.html
.. _Python 3.3: https://docs.python.org/3.3/whatsnew/3.3.html 
.. _Python 3.4: https://docs.python.org/3.4/whatsnew/3.4.html 
.. _Python 3.5: https://docs.python.org/3.5/whatsnew/3.5.html 
.. _Python 3.6: https://docs.python.org/3.6/whatsnew/3.6.html 
.. _Python 3.7: https://docs.python.org/3.7/whatsnew/3.7.html 
.. _Python 3.8: https://docs.python.org/3.8/whatsnew/3.8.html 
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
.. _Sphinx: http://sphinx-doc.org/
.. _twine: https://github.com/pypa/twine
.. _unittest: http://pythontesting.net/framework/unittest/unittest-introduction/
.. _PyYAML: https://github.com/yaml/pyyaml 
.. |copy| unicode:: 0xA9 .. copyright sign
