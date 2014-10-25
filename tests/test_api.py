# -*- coding: utf-8 -*-
import os
import re
import sys
from StringIO import StringIO
import unittest

import natto.api as api

class TestApi(unittest.TestCase):

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