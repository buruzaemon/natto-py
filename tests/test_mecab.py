# -*- coding: utf-8 -*-
'''Tests for natto.mecab.'''
import codecs
import os
import re
import sys
import unittest
import natto.api as api
import natto.environment as env
import natto.mecab as mecab
from StringIO import StringIO
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
            self.testfile = os.path.join(cwd, 'tests', 'test_sjis')
        else:
            self.testfile = os.path.join(cwd, 'tests', 'test_utf8')
        
        self.env = env.MeCabEnv()
        self.text = self._read_text()

    def tearDown(self):
        self.testfile = None
        self.text = None
        self.env = None

    def _read_text(self):
        with codecs.open(self.testfile, 'r') as f:
            text = f.readlines()
        return self._2unicode(text[0].strip())

    def _mecab_parse(self, options):
        cmd = ['mecab']
        if sys.platform == 'win32':
            if len(options) > 0:
                cmd.append(options)
            cmd.append(self.testfile)
            mout = Popen(cmd, stdout=PIPE, shell=True).communicate()
        else:
            if len(options) > 0:
                cmd.append(options)
            cmd.append(self.testfile)
            mout = Popen(cmd, stdout=PIPE).communicate()

        res = mout[0].strip()
        return res
        
    def _23support_prep(self, morphs):
        if sys.version < '3':
            morphs = [e.decode('utf-8').encode(self.env.charset) for e in morphs]
        return morphs


#
#    def _23support_encode(self, b):
#        if sys.version < '3':
#            return b
#        else:
#            return b.encode(self.env.charset)

    # ------------------------------------------------------------------------
    def test_parse_unicode(self):
        s = '日本語だよ、これが。' 
        with mecab.MeCab() as nm:
            if sys.version < '3':
                with self.assertRaises(api.MeCabError):                
                    nm.parse(s)
            else:
                self.assertIsNotNone(nm.parse(s))     

    def test_parse_mecab_options_none(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options(None)
            self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_emptystr(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('')
            self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_emptydict(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options({})
            self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_dicdir(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-d/foo/bar')
            self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

            dopts = nm._MeCab__parse_mecab_options('-d /foo/bar')
            self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

            dopts = nm._MeCab__parse_mecab_options('--dicdir=/foo/bar')
            self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

            dopts = nm._MeCab__parse_mecab_options({'dicdir':'/foo/bar'})
            self.assertDictEqual(dopts, {'dicdir': '/foo/bar'})

    def test_parse_mecab_options_userdic(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-u/baz/qux.dic')
            self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

            dopts = nm._MeCab__parse_mecab_options('-u /baz/qux.dic')
            self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

            dopts = nm._MeCab__parse_mecab_options('--userdic=/baz/qux.dic')
            self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

            dopts = nm._MeCab__parse_mecab_options({'userdic':'/baz/qux.dic'})
            self.assertDictEqual(dopts, {'userdic': '/baz/qux.dic'})

    def test_parse_mecab_options_latticelevel(self):
        with mecab.MeCab() as nm:
            # setting lattice-level issues warning on stderr
            orig_err = sys.stderr
            try:
                tmp_err = StringIO()
                sys.stderr = tmp_err

                dopts = nm._MeCab__parse_mecab_options('-l 777')
                self.assertDictEqual(dopts, {'lattice_level':777})

                res = re.search(nm._WARN_LATTICE_LEVEL,
                                tmp_err.getvalue().strip())
                self.assertIsNotNone(res)
            finally:
                sys.stderr = orig_err

    def test_parse_mecab_options_outputformattype(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-Owakati')
            self.assertDictEqual(dopts, {'output_format_type':'wakati'})

            dopts = nm._MeCab__parse_mecab_options('-O wakati')
            self.assertDictEqual(dopts, {'output_format_type':'wakati'})

            dopts = nm._MeCab__parse_mecab_options('--output-format-type=wakati')
            self.assertDictEqual(dopts, {'output_format_type':'wakati'})

            dopts = nm._MeCab__parse_mecab_options({'output_format_type':'wakati'})
            self.assertDictEqual(dopts, {'output_format_type': 'wakati'})

    def test_parse_mecab_options_allmorphs(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-a')
            self.assertDictEqual(dopts, {'all_morphs':True})

            dopts = nm._MeCab__parse_mecab_options('--all-morphs')
            self.assertDictEqual(dopts, {'all_morphs':True})

            dopts = nm._MeCab__parse_mecab_options({'all_morphs':True})
            self.assertDictEqual(dopts, {'all_morphs':True})

    def test_parse_mecab_options_nbest(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-N2')
            self.assertDictEqual(dopts, {'nbest':2})

            dopts = nm._MeCab__parse_mecab_options('-N 2')
            self.assertDictEqual(dopts, {'nbest':2})

            dopts = nm._MeCab__parse_mecab_options('--nbest=2')
            self.assertDictEqual(dopts, {'nbest':2})

            dopts = nm._MeCab__parse_mecab_options({'nbest':2})
            self.assertDictEqual(dopts, {'nbest':2})

            # ValueError with message if nbest is not an int
            with self.assertRaises(ValueError) as ctx:
                nm._MeCab__parse_mecab_options('-N0.99')
            self.assertIsNotNone(re.search('--nbest', str(ctx.exception)))

    def test_parse_mecab_options_partial(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-p')
            self.assertDictEqual(dopts, {'partial':True})

            dopts = nm._MeCab__parse_mecab_options('--partial')
            self.assertDictEqual(dopts, {'partial':True})

            dopts = nm._MeCab__parse_mecab_options({'partial':True})
            self.assertDictEqual(dopts, {'partial':True})

    def test_parse_mecab_options_marginal(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-m')
            self.assertDictEqual(dopts, {'marginal':True})

            dopts = nm._MeCab__parse_mecab_options('--marginal')
            self.assertDictEqual(dopts, {'marginal':True})

            dopts = nm._MeCab__parse_mecab_options({'marginal':True})
            self.assertDictEqual(dopts, {'marginal':True})

    def test_parse_mecab_options_maxgroupingsize(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-M99')
            self.assertDictEqual(dopts, {'max_grouping_size':99})

            dopts = nm._MeCab__parse_mecab_options('-M 99')
            self.assertDictEqual(dopts, {'max_grouping_size':99})

            dopts = nm._MeCab__parse_mecab_options('--max-grouping-size=99')
            self.assertDictEqual(dopts, {'max_grouping_size':99})

            dopts = nm._MeCab__parse_mecab_options({'max_grouping_size':99})
            self.assertDictEqual(dopts, {'max_grouping_size':99})

            # ValueError with message if max_grouping_size is not an int
            with self.assertRaises(ValueError) as ctx:
                nm._MeCab__parse_mecab_options('-M0.99')
            self.assertIsNotNone(re.search('--max-grouping-size',
                                           str(ctx.exception)))

    def test_parse_mecab_options_nodeformat(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-F%m\\n')
            self.assertDictEqual(dopts, {'node_format':'%m\\n'})

            dopts = nm._MeCab__parse_mecab_options('-F %m\\n')
            self.assertDictEqual(dopts, {'node_format':'%m\\n'})

            dopts = nm._MeCab__parse_mecab_options('--node-format=%m\\n')
            self.assertDictEqual(dopts, {'node_format':'%m\\n'})

            dopts = nm._MeCab__parse_mecab_options({'node_format':'%m\\n'})
            self.assertDictEqual(dopts, {'node_format': '%m\\n'})

    def test_parse_mecab_options_unkformat(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-U???\\n')
            self.assertDictEqual(dopts, {'unk_format':'???\\n'})

            dopts = nm._MeCab__parse_mecab_options('-U ???\\n')
            self.assertDictEqual(dopts, {'unk_format':'???\\n'})

            dopts = nm._MeCab__parse_mecab_options('--unk-format=???\\n')
            self.assertDictEqual(dopts, {'unk_format':'???\\n'})

            dopts = nm._MeCab__parse_mecab_options({'unk_format':'???\\n'})
            self.assertDictEqual(dopts, {'unk_format': '???\\n'})

    def test_parse_mecab_options_bosformat(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-B>>>\\n')
            self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

            dopts = nm._MeCab__parse_mecab_options('-B >>>\\n')
            self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

            dopts = nm._MeCab__parse_mecab_options('--bos-format=>>>\\n')
            self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

            dopts = nm._MeCab__parse_mecab_options({'bos_format':'>>>\\n'})
            self.assertDictEqual(dopts, {'bos_format': '>>>\\n'})

    def test_parse_mecab_options_eosformat(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-E<<<\\n')
            self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

            dopts = nm._MeCab__parse_mecab_options('-E <<<\\n')
            self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

            dopts = nm._MeCab__parse_mecab_options('--eos-format=<<<\\n')
            self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

            dopts = nm._MeCab__parse_mecab_options({'eos_format':'<<<\\n'})
            self.assertDictEqual(dopts, {'eos_format': '<<<\\n'})

    def test_parse_mecab_options_eonformat(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-S___\\n')
            self.assertDictEqual(dopts, {'eon_format':'___\\n'})

            dopts = nm._MeCab__parse_mecab_options('-S ___\\n')
            self.assertDictEqual(dopts, {'eon_format':'___\\n'})

            dopts = nm._MeCab__parse_mecab_options('--eon-format=___\\n')
            self.assertDictEqual(dopts, {'eon_format':'___\\n'})

            dopts = nm._MeCab__parse_mecab_options({'eon_format':'___\\n'})
            self.assertDictEqual(dopts, {'eon_format': '___\\n'})

    def test_parse_mecab_options_unkfeature(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-x!!!\\n')
            self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

            dopts = nm._MeCab__parse_mecab_options('-x !!!\\n')
            self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

            dopts = nm._MeCab__parse_mecab_options('--unk-feature=!!!\\n')
            self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

            dopts = nm._MeCab__parse_mecab_options({'unk_feature':'!!!\\n'})
            self.assertDictEqual(dopts, {'unk_feature': '!!!\\n'})

    def test_parse_mecab_options_inputbuffersize(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-b8888')
            self.assertDictEqual(dopts, {'input_buffer_size':8888})

            dopts = nm._MeCab__parse_mecab_options('-b 8888')
            self.assertDictEqual(dopts, {'input_buffer_size':8888})

            dopts = nm._MeCab__parse_mecab_options('--input-buffer-size=8888')
            self.assertDictEqual(dopts, {'input_buffer_size':8888})

            dopts = nm._MeCab__parse_mecab_options({'input_buffer_size':8888})
            self.assertDictEqual(dopts, {'input_buffer_size':8888})

            # ValueError with message if input_buffer_size is not an int
            with self.assertRaises(ValueError) as ctx:
                nm._MeCab__parse_mecab_options('-b0.99')
            self.assertIsNotNone(re.search('--input-buffer-size',
                                           str(ctx.exception)))

    def test_parse_mecab_options_allocatesentence(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-C')
            self.assertDictEqual(dopts, {'allocate_sentence':True})

            dopts = nm._MeCab__parse_mecab_options('--allocate-sentence')
            self.assertDictEqual(dopts, {'allocate_sentence':True})

            dopts = nm._MeCab__parse_mecab_options({'allocate_sentence':True})
            self.assertDictEqual(dopts, {'allocate_sentence':True})

    def test_parse_mecab_options_theta(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-t0.777')
            self.assertDictEqual(dopts, {'theta':0.777})

            dopts = nm._MeCab__parse_mecab_options('-t 0.777')
            self.assertDictEqual(dopts, {'theta':0.777})

            dopts = nm._MeCab__parse_mecab_options('--theta=0.777')
            self.assertDictEqual(dopts, {'theta':0.777})

            dopts = nm._MeCab__parse_mecab_options({'theta':0.777})
            self.assertDictEqual(dopts, {'theta':0.777})

            # ValueError and message on stderr if theta is not a float
            with self.assertRaises(ValueError) as ctx:
                nm._MeCab__parse_mecab_options('--theta=XXX')
            self.assertIsNotNone(re.search('--theta', str(ctx.exception)))

    def test_parse_mecab_options_costfactor(self):
        with mecab.MeCab() as nm:
            dopts = nm._MeCab__parse_mecab_options('-c666')
            self.assertDictEqual(dopts, {'cost_factor':666})

            dopts = nm._MeCab__parse_mecab_options('-c 666')
            self.assertDictEqual(dopts, {'cost_factor':666})

            dopts = nm._MeCab__parse_mecab_options('--cost-factor=666')
            self.assertDictEqual(dopts, {'cost_factor':666})

            dopts = nm._MeCab__parse_mecab_options({'cost_factor':666})
            self.assertDictEqual(dopts, {'cost_factor':666})

            # ValueError with message if cost_factor is not an int
            with self.assertRaises(ValueError) as ctx:
                nm._MeCab__parse_mecab_options('-c0.99')
            self.assertIsNotNone(re.search('--cost-factor', str(ctx.exception)))

    # ------------------------------------------------------------------------
    def test_build_options_str(self):
        with mecab.MeCab() as nm:
            opts = nm._MeCab__build_options_str(
                                         {'dicdir':'/foo',
                                          'userdic':'/bar',
                                          'lattice_level': 444,
                                          'output_format_type':'yomi',
                                          'all_morphs': True,
                                          'nbest': 555,
                                          'partial': True,
                                          'marginal': True,
                                          'max_grouping_size': 666,
                                          'node_format': 'node\\n',
                                          'unk_format': 'unk\\n',
                                          'bos_format': 'bos\\n',
                                          'eos_format': 'eos\\n',
                                          'eon_format': 'eon\\n',
                                          'unk_feature': 'unkf\\n',
                                          'input_buffer_size': 777,
                                          'allocate_sentence': True,
                                          'theta': 0.999,
                                          'cost_factor': 888,
                                          'unknown':1000})
            expected = self._2bytes(opts)

            actual = ['--dicdir=/foo',
                      '--userdic=/bar',
                      '--lattice-level=444',
                      '--output-format-type=yomi',
                      '--all-morphs',
                      '--nbest=555',
                      '--partial',
                      '--marginal',
                      '--max-grouping-size=666',
                      '--node-format=node\\\\n',
                      '--unk-format=unk\\\\n',
                      '--bos-format=bos\\\\n', 
                      '--eos-format=eos\\\\n',
                      '--eon-format=eon\\\\n',
                      '--unk-feature=unkf\\\\n',
                      '--input-buffer-size=777',
                      '--allocate-sentence',
                      '--theta=0.999',
                      '--cost-factor=888']
            for option in actual:
                self.assertIsNotNone(re.search(option, expected))
            self.assertIsNone(re.search('--unknown', expected))

    # ------------------------------------------------------------------------
    def test_init_unknownoption(self):
        # MeCabError if unrecognized option passed in
        with self.assertRaises(api.MeCabError) as ctx:
            with mecab.MeCab('--unknown'):
                self.assertIsNotNone(re.search('--unknown', str(ctx.exception)))

    def test_init_libunset(self):
        # load error when MeCab lib is not found
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
        with mecab.MeCab() as nm:
            res = Popen(['mecab', '-v'], stdout=PIPE).communicate()
            expected = self._b2u(res[0])
            print(isinstance(nm.version, str))
            print(isinstance(expected, str))
            self.assertIsNotNone(re.search(nm.version, expected))

    # ------------------------------------------------------------------------
    def test_null_text_error(self):
        with mecab.MeCab() as nm:
            with self.assertRaises(api.MeCabError):
                nm.parse(None)

    def test_parse_tostr_default(self):
        with mecab.MeCab() as nm:
            expected = nm.parse(self.text).strip()
            expected = expected.replace('\n', os.linesep)                 # ???

            actual = self._b2u(self._mecab_parse(''))

            self.assertEqual(expected, actual)

    def test_parse_tostr(self):
        formats = ['',
                   '-Owakati',
                   '-Oyomi',
                   '-Ochasen2',
                   '-N2',
                   '-F%m\\t%h\\t%f[0]\\n']
        for argf in formats:
            with mecab.MeCab(argf) as nm:
                expected = nm.parse(self.text)
                expected = expected.replace('\n', os.linesep)

                actual = self._b2u(self._mecab_parse(argf))

                self.assertEqual(expected, actual)

    def test_parse_tonode_default(self):
        formats = ['', '-N2']
        for argf in formats:
            with mecab.MeCab(argf) as nm:
                expected = nm.parse(self.text, as_nodes=True)
                expected = [e for e in expected if not e.is_eos()]

                actual = self._b2u(self._mecab_parse(argf))
                actual = [e for e in actual.split(os.linesep) if e != 'EOS']

                for i, e in enumerate(actual):
                    s, f = actual[i].split()
                    self.assertEqual(expected[i].surface, s)
                    self.assertEqual(expected[i].feature, f)


'''
Copyright (c) 2014, Brooke M. Fujita.
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
