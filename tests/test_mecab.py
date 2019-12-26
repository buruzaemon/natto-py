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
import natto.support as support
from os import path
from string import Template
from subprocess import Popen, PIPE
from tests import Test23Support
from yaml import FullLoader

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

        yamlfile = os.path.join(cwd, 'tests', 'test_utf8.yml')
        self.env = env.MeCabEnv()

        self.b2s, self.s2b = support.string_support(self.env.charset)

        self.testrc = os.path.join(cwd, 'tests', 'testmecabrc')

        with codecs.open(self.textfile, 'r') as f:
            self.text = f.readlines()[0].strip(os.linesep)

        with codecs.open(yamlfile, 'r', encoding='utf-8') as f:
            self.yaml = yaml.load(f, Loader=FullLoader)

        cmd = ['mecab', '-P']
        mout = Popen(cmd, stdout=PIPE).communicate()
        res = self.b2s(mout[0])
        m = re.search('(?<=dicdir:\s).*', res)
        ipadic = path.abspath(m.group(0).strip(os.linesep))
        with open(path.join(os.getcwd(), 'tests', 'mecabrc.tmp'), 'r') as fin:
            tmpl = Template(fin.read())

            tmpl = tmpl.substitute({'ipadic': ipadic})

            with open(self.testrc, 'w') as fout:
                fout.write(tmpl)


    def tearDown(self):
        self.textfile = None
        self.text = None
        self.yaml = None
        self.env = None
        self.testrc = None

    def _mecab_parse(self, options):
        cmd = ['mecab']

        if type(options) is str:
            if len(options) > 0:
                cmd.append(options)
        elif type(options) is list:
            cmd.extend(options)
        cmd.append(self.textfile)

        if sys.platform == 'win32':
            mout = Popen(cmd, stdout=PIPE, shell=True).communicate()
        else:
            mout = Popen(cmd, stdout=PIPE).communicate()

        res = mout[0].strip(os.linesep.encode())
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
    def test_parse_args(self):
        '''Test invocation of parse with bad arguments.'''
        # None text
        with mecab.MeCab() as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse(None)

        # text must be str
        with mecab.MeCab() as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse(99)

        # boundary_constraints must be re or str
        with mecab.MeCab() as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse('foo', boundary_constraints=99.99)

        # feature_constraints must be tuple
        with mecab.MeCab() as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse('foo', feature_constraints=[])

        # -p / --partial, text must end with \n
        with mecab.MeCab('--partial') as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse('foo')


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

    # ------------------------------------------------------------------------
    def test_parse_tostr_default(self):
        '''Test simple default parsing.'''
        with mecab.MeCab() as nm:
            expected = nm.parse(self.text).strip(os.linesep)
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

                for i in range(len(actual)):
                    s, f = actual[i].split('\t')
                    self.assertEqual(expected[i].surface, s)
                    self.assertEqual(expected[i].feature, f)

    def test_parse_tonode_outputformat_errors(self):
        '''Test node parsing with output formatting errors:
           1. unknown node has no pronunciation value 
           2. format missing leading [
           3. format missing ending ]
        '''
        s = '私はブルザエモンです。'
        formats = ['-F%f[8]', '-F%f1]', '-F%f[1']
        for argf in formats:
            with mecab.MeCab(argf) as nm:
                with self.assertRaises(api.MeCabError):
                    list(nm.parse('私はブルザエモンです。', as_nodes=True))

    # ------------------------------------------------------------------------
    def test_parse_tostr_partial(self):
        '''Test -p / --partial parsing to string.'''
        with mecab.MeCab('-p') as nm:
            yml = self.yaml.get('text10')
            txt = self._u2str(yml.get('text'))
            actual = nm.parse(txt).split('\n')
            expected = [self._u2str(e) for e in yml.get('expected').get('str').split(',')]

            for i in range(len(actual)):
                self.assertTrue(actual[i].startswith(expected[i]))

    # ------------------------------------------------------------------------
    def test_parse_tostr_boundary(self):
        '''Test boundary constraint parsing to string (output format does NOT apply).'''
        with mecab.MeCab() as nm:
            # simple pattern
            yml1 = self.yaml.get('text1')
            txt1 = self._u2str(yml1.get('text'))
            pat1 = self._u2str(yml1.get('pattern'))
            expected = [self._u2str(e) for e in yml1.get('expected')]

            actual = nm.parse(txt1, boundary_constraints=pat1)
            lines = actual.split(os.linesep)

            for i in range(len(lines)):
                self.assertTrue(lines[i].startswith(expected[i]))

            # slightly more complex pattern
            yml2 = self.yaml.get('text2')
            txt2 = self._u2str(yml2.get('text'))
            pat2 = self._u2str(yml2.get('pattern'))
            expected = [self._u2str(e) for e in yml2.get('expected')]

            actual = nm.parse(txt2, boundary_constraints=pat2)
            lines = actual.split(os.linesep)

            for i in range(len(lines)):
                self.assertTrue(lines[i].startswith(expected[i]))

            # complex pattern requiring RegExp compiled with re.U flag
            yml3 = self.yaml.get('text3')
            txt3 = self._u2str(yml3.get('text'))
            pat3 = self._u2str(yml3.get('pattern'))
            expected = [self._u2str(e) for e in yml3.get('expected')]

            actual = nm.parse(txt3, boundary_constraints=re.compile(pat3, re.U))
            lines = actual.split(os.linesep)

            for i in range(len(lines)):
                self.assertTrue(lines[i].startswith(expected[i]))

            # text includes trailing whitespace char in token
#            yml9 = self.yaml.get('text9')
#            txt9 = self._u2str(yml9.get('text'))
#            pat9 = self._u2str(yml9.get('pattern'))
#            expected = [self._u2str(e) for e in yml9.get('expected')]
#            print("??? '{}'".format(type(pat9)))
#
#            actual = nm.parse(txt9, boundary_constraints=pat9)
#            lines = actual.split(os.linesep)
#
#            for i in range(len(lines)):
#                self.assertTrue(lines[i].startswith(expected[i]))

        with mecab.MeCab('-N2') as nm:
            # 2-Best
            yml = self.yaml.get('text4')
            txt = self._u2str(yml.get('text'))
            pat = self._u2str(yml.get('pattern'))
            expected = [self._u2str(e) for e in yml.get('expected')]

            actual = nm.parse(txt, boundary_constraints=pat)
            lines = actual.splitlines()

            for i in range(len(lines)):
                self.assertTrue(lines[i].endswith(expected[i]))

        # with theta option
        for t in [ 0.5, 0.75, 0.99 ]:
            with mecab.MeCab("-t {}".format(t)) as nm:
                # simple pattern
                yml1 = self.yaml.get('text1')
                txt1 = self._u2str(yml1.get('text'))
                pat1 = self._u2str(yml1.get('pattern'))
                expected = [self._u2str(e) for e in yml1.get('expected')]

                actual = nm.parse(txt1, boundary_constraints=pat1)
                lines = actual.split(os.linesep)

                for i in range(len(lines)):
                    self.assertTrue(lines[i].startswith(expected[i]))

    # ------------------------------------------------------------------------
    def test_parse_tonodes_boundary(self):
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

#            # text includes trailing whitespace char in token
#            yml9 = self.yaml.get('text9')
#            txt9 = self._u2str(yml9.get('text'))
#            pat9 = self._u2str(yml9.get('pattern'))
#            expected = [self._u2str(e) for e in yml9.get('expected')]
#
#            print(type(pat9))
#
#            gen = nm.parse(txt9, boundary_constraints=pat2, as_nodes=True)
#            for i, node in enumerate(gen):
#                if not node.is_eos():
#                    self.assertEqual(node.surface, expected[i])

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

        # with theta option
        for t in [ 0.5, 0.75, 0.99 ]:
            with mecab.MeCab("-t {}".format(t)) as nm:
                # simple node-parsing, no N-Best or output formatting
                yml1 = self.yaml.get('text1')
                txt1 = self._u2str(yml1.get('text'))
                pat1 = self._u2str(yml1.get('pattern'))
                expected = [self._u2str(e) for e in yml1.get('expected')]

                gen = nm.parse(txt1, boundary_constraints=pat1, as_nodes=True)
                for i, node in enumerate(gen):
                    if not node.is_eos():
                        self.assertEqual(node.surface, expected[i])

    # ------------------------------------------------------------------------
#    def test_parse_tostr_feature(self):
#        '''Test feature constraint parsing to string (output format does NOT apply).'''
#        with mecab.MeCab(r'-F%m,%f[0],%s\n') as nm:
#            yml = self.yaml.get('text11')
#            txt = self._u2str(yml.get('text'))
#            feat = (tuple(self._u2str(yml.get('feature')).split(',')) ,)
#            expected = [self._u2str(e) for e in yml.get('expected')]
#
#            actual = nm.parse(txt, feature_constraints=feat).split('\n')
#
#            for i in range(len(actual)):
#                self.assertEqual(actual[i], expected[i])
#
    # ------------------------------------------------------------------------
    def test_parse_override_node_format(self):
        '''Test node-format override when default is defined in rcfile'''
        with mecab.MeCab(r'-r {} -O "" -F%m!\n'.format(self.testrc)) as nm:
            expected = nm.parse(self.text, as_nodes=True)
            expected = [e.feature for e in expected if e.stat == 0]

            argf = ['-r', self.testrc, '-O', '', '-F%m!\\n']
            actual = self._2bytes(self._mecab_parse(argf))
            #actual = [e for e in actual.split('\n') if not e.startswith('EOS')]
            actual = [e for e in actual.split(os.linesep) if not e.startswith('EOS')]

            for i,e in enumerate(actual):
                self.assertEqual(e, expected[i])
    

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
