# -*- coding: utf-8 -*-
import re
import unittest
import natto.mecab as mecab


class TestDictionary(unittest.TestCase):

    def setUp(self):
        self.nm = mecab.MeCab()

    def test_sysdic(self):
        sysdic = self.nm.dicts[0]

        cs = sysdic.charset.lower()
        self.assertIn(cs, ['utf-16', 'utf-8', 'utf8', 'shift-jis', 'euc-jp'])
        self.assertIsNotNone(re.search('sys.dic$', sysdic.filename))
        self.assertEqual(sysdic.type, 0)
        self.assertEqual(sysdic.version, 102)
