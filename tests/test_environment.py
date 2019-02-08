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

    # ------------------------------------------------------------------------

    def test_charset_defaulting(self):
        '''Test automatic charset defaulting.'''
        orig = os.getenv(environment.MeCabEnv.MECAB_CHARSET)

        try:
            del os.environ[environment.MeCabEnv.MECAB_CHARSET]
            noenv = environment.MeCabEnv()

            res = Popen(['mecab', '-D'], stdout=PIPE).communicate()
            lines = res[0].decode()
            dicinfo = lines.split(os.linesep)
            t = [t for t in dicinfo if t.startswith('charset')]
            expected = t[0].split('\t')[1].strip()

            self.assertEqual(noenv.charset.lower(), expected.lower())
        finally:
            os.environ[environment.MeCabEnv.MECAB_CHARSET] = orig

    def test_libpath_defaulting(self):
        '''Test automatic library path defaulting.'''
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
