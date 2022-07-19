# -*- coding: utf-8 -*-
'''Tests for natto.support.'''
import codecs
import os
import re
import sys
import yaml
import unittest
import natto.environment as env
import natto.support as support
from tests import TestStringSupport
from yaml import CLoader as Loader

class TestSupport(unittest.TestCase, TestStringSupport):
    '''Tests the behavior of the natto.mecab.Support module. '''

    def setUp(self):
        self.env = env.MeCabEnv()
        enc = self.env.charset

        self.bytes2str, self.str2bytes = support.string_support(enc)
        self.split_pattern, self.split_features = support.splitter_support()

        cwd = os.getcwd()
        yamlfile = os.path.join(cwd, 'tests', 'test_utf8.yml')

        with codecs.open(yamlfile, 'r', encoding='utf-8') as f:
            self.yaml = yaml.load(f, Loader=Loader)

    def tearDown(self):
        self.yaml = None
        self.env = None
        self.bytes2str = None
        self.str2bytes = None
        self.splitter_support = None

    # ------------------------------------------------------------------------

    def test_bytes2str(self):
        '''Test behavior of string support for MeCab output:
           bytes.decode(enc) to Unicode
        '''
        yml = self.yaml.get('text1')
        txt = self._mecab_input(yml.get('text'))
        self.assertEqual(self._mecab_output(txt), self.bytes2str(txt))

    def test_str2bytes(self):
        '''Test behavior of string support for MeCab input:
           str.encode(enc) to bytes
        '''
        yml = self.yaml.get('text1')
        txt = self._u2str(yml.get('text'))
        self.assertEqual(self._mecab_input(txt), self.str2bytes(txt))

    def test_splitter_str(self):
        '''Test behavior of splitter support for MeCab boundary constraint
           parsing.
        '''
        yml = self.yaml.get('text7')
        text = self._u2str(yml.get('text'))
        pat1 = self._u2str(yml.get('pattern'))

        tokens = [self._u2str(e) for e in yml.get('tokens')]
        matches = [e for e in yml.get('matches')]
        expected = list(zip(tokens, matches))
        actual = list(self.split_pattern(text, pat1))

        self.assertEqual(expected, actual)

    def test_splitter_re(self):
        '''Test behavior of splitter support for MeCab boundary constraint
           parsing.
        '''
        yml = self.yaml.get('text7')
        text = self._u2str(yml.get('text'))
        pat1 = re.compile(yml.get('pattern'))

        tokens = [self._u2str(e) for e in yml.get('tokens')]
        matches = [e for e in yml.get('matches')]
        expected = list(zip(tokens, matches))
        actual = list(self.split_pattern(text, pat1))

        self.assertEqual(expected, actual)

    def test_splitter_reU(self):
        '''Test behavior of splitter support for MeCab boundary constraint
           parsing.
        '''
        yml = self.yaml.get('text8')
        text = self._u2str(yml.get('text'))
        pat1 = re.compile(yml.get('pattern'), re.U)

        tokens = [self._u2str(e) for e in yml.get('tokens')]
        matches = [e for e in yml.get('matches')]
        expected = list(zip(tokens, matches))
        actual = list(self.split_pattern(text, pat1))

        self.assertEqual(expected, actual)

'''
Copyright (c) 2022, Brooke M. Fujita.
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
