# -*- coding: utf-8 -*-
'''Tests for natto.dictionary.'''
import re
import unittest
import natto.mecab as mecab
from tests import Test23Support

class TestDictionary(unittest.TestCase, Test23Support):
    '''Tests the behavior of the natto.dictionary.DictionaryInfo class.

    Assumes that the mecab-ipadic 2.7.0-20070801 dictionary is installed.

    MeCab supports the following character encodings:
    - UTF-8 (sometimes displayed as UTF8)
    - UTF-16
    - SHIFT-JIS
    - EUC-JP
    '''
    CHARSETS = ['utf-16', 'utf-8', 'utf8', 'shift-jis', 'euc-jp']

    def test_sysdic(self):
        '''Test dictionary interface on system dictionary.'''
        with mecab.MeCab() as nm:
            sysdic = nm.dicts[0]
            cs = sysdic.charset.lower()
            self.assertIn(cs, self.CHARSETS)
            self.assertIsNotNone(re.search('sys.dic$', sysdic.filepath))
            self.assertEqual(sysdic.type, 0)
            self.assertEqual(sysdic.version, 102)

'''
Copyright (c) 2019, Brooke M. Fujita.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above
   copyright notice, this list of conditions and the
   following disclaimer.

 * Redistributions in binary form must reproduce the above
   copyright notice, this list of conditions and the
   following disclaimer in the documentation and/or other
   materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
