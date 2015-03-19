# -*- coding: utf-8 -*-
'''Tests for natto.mecab.'''
import codecs
import os
import re
import sys
import yaml
import unittest
import natto.api as api
import natto.environment as env
import natto.mecab as mecab
from subprocess import Popen, PIPE
from tests import Test23Support

class TestMecab(unittest.TestCase, Test23Support):
    '''Tests the behavior of the natto.mecab.MeCab class.

    Assumes that the MECAB_PATH and MECAB_CHARSET environment variables have
    been set.
    '''
    def setUp(self):
        cwd = os.getcwd()
        if sys.platform == 'win32':
            self.textfile = os.path.join(cwd, 'tests', 'test_sjis.txt')
        else:
            self.textfile = os.path.join(cwd, 'tests', 'test_utf8.txt')

        self.yamlfile = os.path.join(cwd, 'tests', 'test_utf8.yml')
        self.env = env.MeCabEnv()

        with codecs.open(self.textfile, 'r') as f:
            self.text = f.readlines()[0].strip()

        with codecs.open(self.yamlfile, 'r', encoding='utf-8') as f:
            self.yaml = yaml.load(f)

    def tearDown(self):
        self.textfile = None
        self.text = None
        self.yaml = None
        self.env = None

    def _mecab_parse(self, options):
        cmd = ['mecab']
        if sys.platform == 'win32':
            if len(options) > 0:
                cmd.append(options)
            cmd.append(self.textfile)
            mout = Popen(cmd, stdout=PIPE, shell=True).communicate()
        else:
            if len(options) > 0:
                cmd.append(options)
            cmd.append(self.textfile)
            mout = Popen(cmd, stdout=PIPE).communicate()

        res = mout[0].strip()
        return res

    def _23support_prep(self, morphs):
        if sys.version < '3':
            morphs = [e.decode('utf-8').encode(self.env.charset) for e in morphs]
        return morphs


    # ------------------------------------------------------------------------

    def test_init_unknownoption(self):
        '''Test instantiation of MeCab with unrecognized option.'''
        with self.assertRaises(api.MeCabError) as ctx:
            with mecab.MeCab('--unknown'):
                self.assertIsNotNone(re.search('--unknown', str(ctx.exception)))

    def test_init_libunset(self):
        '''Test for load error when MeCab lib is not found.'''
        try:
            orig_env = os.getenv(mecab.MeCab.MECAB_PATH)
            os.environ[mecab.MeCab.MECAB_PATH] = '/foo/bar'

            with self.assertRaises(api.MeCabError) as cm:
                with mecab.MeCab():
                    self.assertIsNotNone(
                        re.search('cannot load library /foo/bar',
                        str(cm.exception)))
        finally:
            os.environ[mecab.MeCab.MECAB_PATH] = orig_env

    # ------------------------------------------------------------------------
    def test_version(self):
        '''Test mecab_version.'''
        with mecab.MeCab() as nm:
            res = Popen(['mecab', '-v'], stdout=PIPE).communicate()
            expected = self._b2u(res[0])
            self.assertIsNotNone(re.search(nm.version, expected))

    # ------------------------------------------------------------------------
    def test_parse_unicodeRstr(self):
        '''Test parse: unicode input (Python 2) and bytes input (Python 3).'''
        s = '日本語だよ、これが。'
        with mecab.MeCab() as nm:
            if sys.version < '3':
                b = s.decode('utf-8')
            else:
                b = s.encode('utf-8')

            with self.assertRaises(api.MeCabError):
                nm.parse(b)

    def test_null_text_error(self):
        '''Test invocation of parse with null argument.'''
        with mecab.MeCab() as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse(None)

    # ------------------------------------------------------------------------
    def test_parse_tostr_default(self):
        '''Test simple default parsing.'''
        with mecab.MeCab() as nm:
            expected = nm.parse(self.text).strip()
            expected = expected.replace('\n', os.linesep)                 # ???

            actual = self._2bytes(self._mecab_parse(''))

            self.assertEqual(expected, actual)

    def test_parse_tostr(self):
        '''Test default parsing, across different output formats.'''
        formats = ['',
                   '-Owakati',
                   '-Oyomi',
                   '-Ochasen2',
                   '-N2',
                   r'-F%m\t%h\t%f[0]\n']
        for argf in formats:
            with mecab.MeCab(argf) as nm:
                expected = nm.parse(self.text)
                expected = expected.replace('\n', os.linesep)

                actual = self._2bytes(self._mecab_parse(argf))

                self.assertEqual(expected, actual)

    # ------------------------------------------------------------------------
    def test_parse_tonode_default(self):
        '''Test node parsing, skipping over any BOS or EOS nodes.'''
        formats = ['', '-N2']
        for argf in formats:
            with mecab.MeCab(argf) as nm:
                expected = nm.parse(self.text, as_nodes=True)
                expected = [e for e in expected if e.stat == 0]

                actual = self._2bytes(self._mecab_parse(argf))
                actual = [e for e in actual.split(os.linesep) if e != 'EOS']

                for i, e in enumerate(actual):
                    s, f = actual[i].split()
                    self.assertEqual(expected[i].surface, s)
                    self.assertEqual(expected[i].feature, f)

    # ------------------------------------------------------------------------
    def test_bcparse_tostr(self):
        '''Test boundary constraint parsing to string (output format does NOT apply).'''
        with mecab.MeCab() as nm:
            # simple pattern
            yml1 = self.yaml.get('text1')
            txt1 = self._u2str(yml1.get('text'))
            pat1 = self._u2str(yml1.get('pattern'))
            expected = [self._u2str(e) for e in yml1.get('expected')]

            actual = nm.parse(txt1, boundary_constraints=pat1)
            lines = actual.split(os.linesep)

            for i, e in enumerate(lines):
                self.assertTrue(lines[i].startswith(expected[i]))

            # slightly more complex pattern
            yml2 = self.yaml.get('text2')
            txt2 = self._u2str(yml2.get('text'))
            pat2 = self._u2str(yml2.get('pattern'))
            expected = [self._u2str(e) for e in yml2.get('expected')]

            actual = nm.parse(txt2, boundary_constraints=pat2)
            lines = actual.split(os.linesep)

            for i, e in enumerate(lines):
                self.assertTrue(lines[i].startswith(expected[i]))

            # complex pattern requiring RegExp compiled with re.U flag
            yml3 = self.yaml.get('text3')
            txt3 = self._u2str(yml3.get('text'))
            pat3 = self._u2str(yml3.get('pattern'))
            expected = [self._u2str(e) for e in yml3.get('expected')]

            actual = nm.parse(txt3, boundary_constraints=re.compile(pat3, re.U))
            lines = actual.split(os.linesep)

            for i, e in enumerate(lines):
                self.assertTrue(lines[i].startswith(expected[i]))

        with mecab.MeCab('-N2') as nm:
            # 2-Best
            yml = self.yaml.get('text4')
            txt = self._u2str(yml.get('text'))
            pat = self._u2str(yml.get('pattern'))
            expected = [self._u2str(e) for e in yml.get('expected')]

            actual = nm.parse(txt, boundary_constraints=pat)
            #lines = actual.split(os.linesep)
            lines = actual.splitlines()

            for i, e in enumerate(lines):
                self.assertTrue(lines[i].endswith(expected[i]))

    # ------------------------------------------------------------------------
    def test_bcparse_tonodes(self):
        '''Test boundary constraint parsing as nodes (output format does NOT apply).'''
        with mecab.MeCab() as nm:
            # simple node-parsing, no N-Best or output formatting
            yml1 = self.yaml.get('text1')
            txt1 = self._u2str(yml1.get('text'))
            pat1 = self._u2str(yml1.get('pattern'))
            expected = [self._u2str(e) for e in yml1.get('expected')]

            gen = nm.parse(txt1, boundary_constraints=pat1, as_nodes=True)
            for i, node in enumerate(gen):
                if not node.is_eos():
                    self.assertEqual(node.surface, expected[i])

            # slightly more complex pattern
            yml2 = self.yaml.get('text2')
            txt2 = self._u2str(yml2.get('text'))
            pat2 = self._u2str(yml2.get('pattern'))
            expected = [self._u2str(e) for e in yml2.get('expected')]

            gen = nm.parse(txt2, boundary_constraints=pat2, as_nodes=True)
            for i, node in enumerate(gen):
                if not node.is_eos():
                    self.assertEqual(node.surface, expected[i])

        with mecab.MeCab(r'-F%m\s%s') as nm:
            # with output formatting
            yml1 = self.yaml.get('text5')
            txt1 = self._u2str(yml1.get('text'))
            pat1 = self._u2str(yml1.get('pattern'))
            expected = [self._u2str(e) for e in yml1.get('expected')]

            gen = nm.parse(txt1, boundary_constraints=pat1, as_nodes=True)
            for i, node in enumerate(gen):
                if not node.is_eos():
                    self.assertEqual(node.feature, expected[i])

        with mecab.MeCab(r'-F%m\s%F\s[0,1]\s%s -N2') as nm:
            # with N-best and output formatting
            yml1 = self.yaml.get('text6')
            txt1 = self._u2str(yml1.get('text'))
            pat1 = self._u2str(yml1.get('pattern'))
            expected = [self._u2str(e) for e in yml1.get('expected')]

            i = 0
            for node in nm.parse(txt1, boundary_constraints=pat1, as_nodes=True):
                if not node.is_eos():
                    self.assertEqual(node.feature, expected[i])
                    i += 1

'''
Copyright (c) 2015, Brooke M. Fujita.
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
