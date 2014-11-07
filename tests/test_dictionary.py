# -*- coding: utf-8 -*-
'''Tests for natto.dictionary.'''
import re
import unittest
import natto.mecab as mecab

class TestDictionary(unittest.TestCase):
    '''Tests the behavior of the natto.dictionary.DictionaryInfo class.

    Assumes that the mecab-ipadic 2.7.0-20070801 dictionary is installed.
    
    MeCab supports the following character encodings:
    - UTF-8 (sometimes displayed as UTF8)
    - UTF-16
    - SHIFT-JIS
    - EUC-JP
    '''

    def test_sysdic(self):
        with mecab.MeCab() as nm:
            sysdic = nm.dicts[0]
    
            cs = sysdic.charset.lower()
            self.assertIn(cs, ['utf-16', 'utf-8', 'utf8', 'shift-jis', 'euc-jp'])
            self.assertIsNotNone(re.search('sys.dic$', sysdic.filename))
            self.assertEqual(sysdic.type, 0)
            self.assertEqual(sysdic.version, 102)
