# -*- coding: utf-8 -*-
'''Tests for natto.environment.'''
import natto.environment as environment
import os
import sys
import unittest
from subprocess import Popen, PIPE

class TestMeCabEnv(unittest.TestCase):
    '''Tests the behavior of the natto.environment.MeCabEnv class.

    Assumes that the MECAB_PATH and MECAB_CHARSET environment variables have
    been set.
    '''

    def setUp(self):
        self.env = environment.MeCabEnv()

        if sys.platform == 'win32':
            self.default_charset = 'shift-jis'
        elif sys.platform == 'darwin':
            self.default_charset = 'utf8'
        else:
            self.default_charset = 'euc-jp'

    # ------------------------------------------------------------------------

    def test_charset_defaulting(self):
        orig = os.getenv(environment.MeCabEnv.MECAB_CHARSET)

        try:
            del os.environ[environment.MeCabEnv.MECAB_CHARSET]
            noenv = environment.MeCabEnv()
            self.assertEqual(noenv.charset, self.default_charset)
        finally:
            os.environ[environment.MeCabEnv.MECAB_CHARSET] = orig

    def test_libpath_defaulting(self):
        orig = os.getenv(environment.MeCabEnv.MECAB_PATH)

        try:
            del os.environ[environment.MeCabEnv.MECAB_PATH]
            noenv = environment.MeCabEnv()

            if sys.platform == 'win32':
                res = Popen(['mecab', '-D'], stdout=PIPE).communicate()
                lines = res[0].decode()
                dicinfo = lines.split(os.linesep)
                t = [t for t in dicinfo if t.startswith('filename')]
                ldir = t[0].split('etc')[0][10:].strip()
                expected = os.path.join(ldir, 'bin', 'libmecab.dll')
            else:
                if sys.platform == 'darwin':
                    lib = 'libmecab.dylib'
                else:
                    lib = 'libmecab.so'

                res = Popen(['mecab-config', '--libs-only-L'],
                            stdout=PIPE).communicate()
                lines = res[0].decode()
                linfo = lines.strip()
                expected = os.path.join(linfo, lib)

            self.assertEqual(noenv.libpath, expected)
        finally:
            os.environ[environment.MeCabEnv.MECAB_PATH] = orig
