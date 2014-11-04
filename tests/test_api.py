# -*- coding: utf-8 -*-
import os
import re
import sys
import unittest
import natto.api as api
from io import StringIO



class TestApi(unittest.TestCase):

    def setUp(self):
        self.nm = api.MeCab()
        
#        if sys.version < '3':
#            self._u = lambda(s): return(s)
#            self._b = lambda s: return(s)
#        else:
#            self._u = lambda s: return(s.decode(self.nm.__enc))
#            self._b = lambda s: return(s.encode(self.nm.__enc))

    def test_init_unknownoption(self):
        # MeCabError if unrecognized option passed in
        with self.assertRaises(api.MeCabError) as ctx:
            api.MeCab('--unknown')

        self.assertIsNotNone(re.search('--unknown', str(ctx.exception)))

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

        cs = sysdic.charset.lower()
        self.assertIn(cs, ['utf-16', 'utf-8', 'utf8', 'shift-jis', 'euc-jp'])
        self.assertIsNotNone(re.search('sys.dic$', sysdic.filename.decode()))
        self.assertEqual(sysdic.type, 0)
        self.assertEqual(sysdic.version, 102)

#    def test_parse(self):
#        morphs = ['日本語', 'だ', 'よ', '、', 'これ', 'が', '。', 'EOS']
#        txt = "".join(morphs[0:-1])
#        res = self.nm.parse(txt)
#        
#        lines = res.split("\n")
#        for i, l in enumerate(lines):
#            print morphs[i]
#            print l
#            self.assertIsNotNone(re.search(morphs[i], l))
            