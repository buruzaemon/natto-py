# -*- coding: utf-8 -*-
import os
import re
import sys
from io import StringIO
import unittest

import natto.api as api

import codecs
#import sys

if sys.version < '3':
    def _u(s):
        return codecs.unicode_escape_decode(s)[0]
    def _b(x, enc):
        return x.encode(enc)
else:
    def _u(x):
        return x
    def _b(x, enc):
        return codecs.encode(x, enc)


class TestApi(unittest.TestCase):

    def setUp(self):
        self.nm = api.MeCab()

    def test_init_unknownoption(self):
        # SystemExit and message on stderr if unrecognized option passed in
        orig_err = sys.stderr
        try:
            tmp_err = StringIO()
            sys.stderr = tmp_err

            with self.assertRaises(api.MeCabError):
                api.MeCab('--unknown')

            self.assertIsNotNone(re.search('--unknown',
                                 tmp_err.getvalue().strip()))
        finally:
            sys.stderr = orig_err

    def test_init_libunset(self):
        # load error when MeCab lib is not found
        try:
            orig_env = os.getenv(api.MeCab.MECAB_PATH)
            os.environ[api.MeCab.MECAB_PATH] = "/foo/bar"

            with self.assertRaises(api.MeCabError) as cm:
                api.MeCab()

            self.assertIsNotNone(re.search('cannot load library /foo/bar',
                                           str(cm.exception)))
        finally:
            os.environ[api.MeCab.MECAB_PATH] = orig_env

    def test_version(self):
        self.assertEqual(self.nm.version, '0.996')

    def test_sysdic(self):
        sysdic = self.nm.dicts[0]

        self.assertIn(sysdic.charset.lower(), ['utf-16',
                                               'utf-8',
                                               'shift-jis',
                                               'euc-jp'])
        self.assertRegexpMatches(sysdic.filename, 'sys.dic$')
        self.assertEqual(sysdic.type, 0)
        self.assertEqual(sysdic.version, 102)

    def test_parse(self):
        morphs = ['日本語', 'だ', 'よ', '、', 'これ', 'が', '。', 'EOS']
        utxt = "".join(morphs[0:-1]).decode('utf-8')
        res = self.nm.parse(utxt)
        
        lines = res.split("\n")
        for i, l in enumerate(lines):
            print(l)
            print(morphs[i].decode('utf-8'))
            print
            self.assertIsNotNone(re.search(morphs[i].decode('utf-8'), l))
            
