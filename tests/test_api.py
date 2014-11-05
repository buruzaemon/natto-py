# -*- coding: utf-8 -*-
import os
import re
import sys
import unittest
import natto.api as api
import natto.environment as env
from subprocess import Popen, PIPE


class TestApi(unittest.TestCase):
    
    def _23support_prep(self, morphs):
        if sys.version < '3':
            morphs = [e.decode('utf-8').encode(self.env.charset) for e in morphs]
        return morphs
    
    def _23support_decode(self, b):    
        if sys.version < '3':
            return b
        else:
            return b.decode(self.env.charset)

    def setUp(self):
        self.nm = api.MeCab()
        self.env = env.MeCabEnv()            
        
    # ------------------------------------------------------------------------    
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
        res = Popen(['mecab', '-v'], stdout=PIPE).communicate()
        actual = self._23support_decode(res[0])
        self.assertIsNotNone(re.search(self.nm.version, actual))
        
    def test_sysdic(self):
        sysdic = self.nm.dicts[0]

        cs = sysdic.charset.lower()
        self.assertIn(cs, ['utf-16', 'utf-8', 'utf8', 'shift-jis', 'euc-jp'])
        self.assertIsNotNone(re.search('sys.dic$', sysdic.filename))
        self.assertEqual(sysdic.type, 0)
        self.assertEqual(sysdic.version, 102)

    def test_parse_tostr(self):
        toks = self._23support_prep(['日本語', 
                                     'だ', 
                                     'よ', 
                                     '、', 
                                     'これ', 
                                     'が', 
                                     '。', 
                                     'EOS'])
        
        txt = "".join(toks[0:-1])
        res = self.nm.parse(txt)
        
        lines = res.split("\n")
        for i, l in enumerate(lines):
            self.assertIsNotNone(re.search(toks[i], l))
            