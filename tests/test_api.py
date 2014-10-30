# -*- coding: utf-8 -*-
import os
import re
import sys
from StringIO import StringIO
import unittest

import natto.api as api

class TestApi(unittest.TestCase):

    def setUp(self):
        self.nm = api.MeCab()

    def test_init_unknownoption(self):
        # SystemExit and message on stderr if unrecognized option passed in
        orig_err = sys.stderr
        try:
            tmp_err = StringIO()
            sys.stderr = tmp_err

            with self.assertRaises(SystemExit) as cm:
                api.MeCab('--unknown')

            self.assertEqual(cm.exception.code, 2)
            self.assertIsNotNone(re.search('unrecognized arguments: --unknown',
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
        self.assertEquals(self.nm.version, '0.996')

    def test_sysdic(self):
        sysdic = self.nm.dicts[0]

        self.assertIn(sysdic.charset.lower(), ['utf-16',
                                               'utf-8',
                                               'shift-jis',
                                               'euc-jp'])
        self.assertRegexpMatches(sysdic.filename, 'sys.dic$')
        self.assertEquals(sysdic.type, 0)
        self.assertEquals(sysdic.version, 102)

    def test_parse(self):
        morphs = ['日本語', 'だ', 'よ', '、', 'これ', 'が', '。', 'EOS']
        utxt = "".join(morphs).decode('utf-8')
        res = self.nm.parse(utxt)
        lines = res.split("\n")
        for i, l in enumerate(lines[0:-1]):
            self.assertRegexpMatches(l, morphs[i].decode('utf-8'))
        self.assertRegexpMatches(lines[-1], morphs[-1].decode('utf-8'))
