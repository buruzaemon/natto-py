# -*- coding: utf-8 -*-
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


class TestMecab(unittest.TestCase):

    def setUp(self):
        self.text = self._read_text()
        self.nm = mecab.MeCab()  
        #self.nm_nbest = mecab.MeCab()
        self.env = env.MeCabEnv() 
       
    def _read_text(self):  
        cwd = os.getcwd()
        if sys.platform == 'win32':
            fn = os.path.join(cwd, 'tests', 'test_sjis')
        else:
            fn = os.path.join(cwd, 'tests', 'test_utf8')
        with codecs.open(fn, 'r') as f:
            text = f.readlines()    
        return text[0].strip()
        
    def _mecab_parse(self, options, text):
        cmd = []
        cwd = os.getcwd()
        if sys.platform == 'win32':
            cmd.append('type')
            cmd.append(os.path.join(cwd, 'tests', 'test_sjis'))
        else:
            cmd.append('cat')
            cmd.append(os.path.join(cwd, 'tests', 'test_utf8'))
        cmd.append('|')
        cmd.append('mecab')
        if len(options) > 0:
            cmd.append(options)

        out = Popen(cmd, stdout=PIPE, shell=True).communicate()
        res = out[0].strip()
        return res

    def _23support_prep(self, morphs):
        if sys.version < '3':
            morphs = [e.decode('utf-8').encode(self.env.charset) for e in morphs]
        return morphs

    def _23support_decode(self, b):
        if sys.version < '3':
            return b
        else:
            return b.decode(self.env.charset)

    def _23support_encode(self, b):
        if sys.version < '3':
            return b
        else:
            return b.encode(self.env.charset)

    # ------------------------------------------------------------------------
    def test_parse_mecab_options_none(self):
        dopts = self.nm._MeCab__parse_mecab_options(None)
        self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_emptystr(self):
        dopts = self.nm._MeCab__parse_mecab_options('')
        self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_emptydict(self):
        dopts = self.nm._MeCab__parse_mecab_options({})
        self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_dicdir(self):
        dopts = self.nm._MeCab__parse_mecab_options('-d/foo/bar')
        self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

        dopts = self.nm._MeCab__parse_mecab_options('-d /foo/bar')
        self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

        dopts = self.nm._MeCab__parse_mecab_options('--dicdir=/foo/bar')
        self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

        dopts = self.nm._MeCab__parse_mecab_options({'dicdir':'/foo/bar'})
        self.assertDictEqual(dopts, {'dicdir': '/foo/bar'})

    def test_parse_mecab_options_userdic(self):
        dopts = self.nm._MeCab__parse_mecab_options('-u/baz/qux.dic')
        self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

        dopts = self.nm._MeCab__parse_mecab_options('-u /baz/qux.dic')
        self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

        dopts = self.nm._MeCab__parse_mecab_options('--userdic=/baz/qux.dic')
        self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

        dopts = self.nm._MeCab__parse_mecab_options({'userdic':'/baz/qux.dic'})
        self.assertDictEqual(dopts, {'userdic': '/baz/qux.dic'})

    def test_parse_mecab_options_latticelevel(self):
        # setting lattice-level issues warning on stderr
        orig_err = sys.stderr
        try:
            tmp_err = StringIO()
            sys.stderr = tmp_err

            dopts = self.nm._MeCab__parse_mecab_options('-l 777')
            self.assertDictEqual(dopts, {'lattice_level':777})

            res = re.search(self.nm._WARN_LATTICE_LEVEL,
                            tmp_err.getvalue().strip())
            self.assertIsNotNone(res)
        finally:
            sys.stderr = orig_err

    def test_parse_mecab_options_outputformattype(self):
        dopts = self.nm._MeCab__parse_mecab_options('-Owakati')
        self.assertDictEqual(dopts, {'output_format_type':'wakati'})

        dopts = self.nm._MeCab__parse_mecab_options('-O wakati')
        self.assertDictEqual(dopts, {'output_format_type':'wakati'})

        dopts = self.nm._MeCab__parse_mecab_options('--output-format-type=wakati')
        self.assertDictEqual(dopts, {'output_format_type':'wakati'})

        dopts = self.nm._MeCab__parse_mecab_options({'output_format_type':'wakati'})
        self.assertDictEqual(dopts, {'output_format_type': 'wakati'})

    def test_parse_mecab_options_allmorphs(self):
        dopts = self.nm._MeCab__parse_mecab_options('-a')
        self.assertDictEqual(dopts, {'all_morphs':True})

        dopts = self.nm._MeCab__parse_mecab_options('--all-morphs')
        self.assertDictEqual(dopts, {'all_morphs':True})

        dopts = self.nm._MeCab__parse_mecab_options({'all_morphs':True})
        self.assertDictEqual(dopts, {'all_morphs':True})

    def test_parse_mecab_options_nbest(self):
        dopts = self.nm._MeCab__parse_mecab_options('-N2')
        self.assertDictEqual(dopts, {'nbest':2})

        dopts = self.nm._MeCab__parse_mecab_options('-N 2')
        self.assertDictEqual(dopts, {'nbest':2})

        dopts = self.nm._MeCab__parse_mecab_options('--nbest=2')
        self.assertDictEqual(dopts, {'nbest':2})

        dopts = self.nm._MeCab__parse_mecab_options({'nbest':2})
        self.assertDictEqual(dopts, {'nbest':2})

        # ValueError with message if nbest is not an int
        with self.assertRaises(ValueError) as ctx:
            self.nm._MeCab__parse_mecab_options('-N0.99')
        self.assertIsNotNone(re.search('--nbest', str(ctx.exception)))

    def test_parse_mecab_options_partial(self):
        dopts = self.nm._MeCab__parse_mecab_options('-p')
        self.assertDictEqual(dopts, {'partial':True})

        dopts = self.nm._MeCab__parse_mecab_options('--partial')
        self.assertDictEqual(dopts, {'partial':True})

        dopts = self.nm._MeCab__parse_mecab_options({'partial':True})
        self.assertDictEqual(dopts, {'partial':True})

    def test_parse_mecab_options_marginal(self):
        dopts = self.nm._MeCab__parse_mecab_options('-m')
        self.assertDictEqual(dopts, {'marginal':True})

        dopts = self.nm._MeCab__parse_mecab_options('--marginal')
        self.assertDictEqual(dopts, {'marginal':True})

        dopts = self.nm._MeCab__parse_mecab_options({'marginal':True})
        self.assertDictEqual(dopts, {'marginal':True})

    def test_parse_mecab_options_maxgroupingsize(self):
        dopts = self.nm._MeCab__parse_mecab_options('-M99')
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        dopts = self.nm._MeCab__parse_mecab_options('-M 99')
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        dopts = self.nm._MeCab__parse_mecab_options('--max-grouping-size=99')
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        dopts = self.nm._MeCab__parse_mecab_options({'max_grouping_size':99})
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        # ValueError with message if max_grouping_size is not an int
        with self.assertRaises(ValueError) as ctx:
            self.nm._MeCab__parse_mecab_options('-M0.99')
        self.assertIsNotNone(re.search('--max-grouping-size',
                                       str(ctx.exception)))

    def test_parse_mecab_options_nodeformat(self):
        dopts = self.nm._MeCab__parse_mecab_options('-F%m\\n')
        self.assertDictEqual(dopts, {'node_format':'%m\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('-F %m\\n')
        self.assertDictEqual(dopts, {'node_format':'%m\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('--node-format=%m\\n')
        self.assertDictEqual(dopts, {'node_format':'%m\\n'})

        dopts = self.nm._MeCab__parse_mecab_options({'node_format':'%m\\n'})
        self.assertDictEqual(dopts, {'node_format': '%m\\n'})

    def test_parse_mecab_options_unkformat(self):
        dopts = self.nm._MeCab__parse_mecab_options('-U???\\n')
        self.assertDictEqual(dopts, {'unk_format':'???\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('-U ???\\n')
        self.assertDictEqual(dopts, {'unk_format':'???\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('--unk-format=???\\n')
        self.assertDictEqual(dopts, {'unk_format':'???\\n'})

        dopts = self.nm._MeCab__parse_mecab_options({'unk_format':'???\\n'})
        self.assertDictEqual(dopts, {'unk_format': '???\\n'})

    def test_parse_mecab_options_bosformat(self):
        dopts = self.nm._MeCab__parse_mecab_options('-B>>>\\n')
        self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('-B >>>\\n')
        self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('--bos-format=>>>\\n')
        self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

        dopts = self.nm._MeCab__parse_mecab_options({'bos_format':'>>>\\n'})
        self.assertDictEqual(dopts, {'bos_format': '>>>\\n'})

    def test_parse_mecab_options_eosformat(self):
        dopts = self.nm._MeCab__parse_mecab_options('-E<<<\\n')
        self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('-E <<<\\n')
        self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('--eos-format=<<<\\n')
        self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

        dopts = self.nm._MeCab__parse_mecab_options({'eos_format':'<<<\\n'})
        self.assertDictEqual(dopts, {'eos_format': '<<<\\n'})

    def test_parse_mecab_options_eonformat(self):
        dopts = self.nm._MeCab__parse_mecab_options('-S___\\n')
        self.assertDictEqual(dopts, {'eon_format':'___\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('-S ___\\n')
        self.assertDictEqual(dopts, {'eon_format':'___\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('--eon-format=___\\n')
        self.assertDictEqual(dopts, {'eon_format':'___\\n'})

        dopts = self.nm._MeCab__parse_mecab_options({'eon_format':'___\\n'})
        self.assertDictEqual(dopts, {'eon_format': '___\\n'})

    def test_parse_mecab_options_unkfeature(self):
        dopts = self.nm._MeCab__parse_mecab_options('-x!!!\\n')
        self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('-x !!!\\n')
        self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

        dopts = self.nm._MeCab__parse_mecab_options('--unk-feature=!!!\\n')
        self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

        dopts = self.nm._MeCab__parse_mecab_options({'unk_feature':'!!!\\n'})
        self.assertDictEqual(dopts, {'unk_feature': '!!!\\n'})

    def test_parse_mecab_options_inputbuffersize(self):
        dopts = self.nm._MeCab__parse_mecab_options('-b8888')
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        dopts = self.nm._MeCab__parse_mecab_options('-b 8888')
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        dopts = self.nm._MeCab__parse_mecab_options('--input-buffer-size=8888')
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        dopts = self.nm._MeCab__parse_mecab_options({'input_buffer_size':8888})
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        # ValueError with message if input_buffer_size is not an int
        with self.assertRaises(ValueError) as ctx:
            self.nm._MeCab__parse_mecab_options('-b0.99')
        self.assertIsNotNone(re.search('--input-buffer-size',
                                       str(ctx.exception)))

    def test_parse_mecab_options_allocatesentence(self):
        dopts = self.nm._MeCab__parse_mecab_options('-C')
        self.assertDictEqual(dopts, {'allocate_sentence':True})

        dopts = self.nm._MeCab__parse_mecab_options('--allocate-sentence')
        self.assertDictEqual(dopts, {'allocate_sentence':True})

        dopts = self.nm._MeCab__parse_mecab_options({'allocate_sentence':True})
        self.assertDictEqual(dopts, {'allocate_sentence':True})

    def test_parse_mecab_options_theta(self):
        dopts = self.nm._MeCab__parse_mecab_options('-t0.777')
        self.assertDictEqual(dopts, {'theta':0.777})

        dopts = self.nm._MeCab__parse_mecab_options('-t 0.777')
        self.assertDictEqual(dopts, {'theta':0.777})

        dopts = self.nm._MeCab__parse_mecab_options('--theta=0.777')
        self.assertDictEqual(dopts, {'theta':0.777})

        dopts = self.nm._MeCab__parse_mecab_options({'theta':0.777})
        self.assertDictEqual(dopts, {'theta':0.777})

        # ValueError and message on stderr if theta is not a float
        with self.assertRaises(ValueError) as ctx:
            self.nm._MeCab__parse_mecab_options('--theta=XXX')
        self.assertIsNotNone(re.search('--theta', str(ctx.exception)))

    def test_parse_mecab_options_costfactor(self):
        dopts = self.nm._MeCab__parse_mecab_options('-c666')
        self.assertDictEqual(dopts, {'cost_factor':666})

        dopts = self.nm._MeCab__parse_mecab_options('-c 666')
        self.assertDictEqual(dopts, {'cost_factor':666})

        dopts = self.nm._MeCab__parse_mecab_options('--cost-factor=666')
        self.assertDictEqual(dopts, {'cost_factor':666})

        dopts = self.nm._MeCab__parse_mecab_options({'cost_factor':666})
        self.assertDictEqual(dopts, {'cost_factor':666})

        # ValueError with message if cost_factor is not an int
        with self.assertRaises(ValueError) as ctx:
            self.nm._MeCab__parse_mecab_options('-c0.99')
        self.assertIsNotNone(re.search('--cost-factor', str(ctx.exception)))

    # ------------------------------------------------------------------------
    def test_build_options_str(self):
        opts = self.nm._MeCab__build_options_str(
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
        actual = self._23support_decode(opts)

        expected = ['--dicdir=/foo',
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
        for option in expected:
            self.assertIsNotNone(re.search(option, actual))
        self.assertIsNone(re.search('--unknown', actual))

    # ------------------------------------------------------------------------
    def test_init_unknownoption(self):
        # MeCabError if unrecognized option passed in
        with self.assertRaises(api.MeCabError) as ctx:
            mecab.MeCab('--unknown')

        self.assertIsNotNone(re.search('--unknown', str(ctx.exception)))

    def test_init_libunset(self):
        # load error when MeCab lib is not found
        try:
            orig_env = os.getenv(mecab.MeCab.MECAB_PATH)
            os.environ[mecab.MeCab.MECAB_PATH] = '/foo/bar'

            with self.assertRaises(api.MeCabError) as cm:
                mecab.MeCab()

            self.assertIsNotNone(re.search('cannot load library /foo/bar',
                                           str(cm.exception)))
        finally:
            os.environ[mecab.MeCab.MECAB_PATH] = orig_env

    # ------------------------------------------------------------------------
    def test_version(self):
        res = Popen(['mecab', '-v'], stdout=PIPE).communicate()
        actual = self._23support_decode(res[0])
        self.assertIsNotNone(re.search(self.nm.version, actual))

    # ------------------------------------------------------------------------
    def test_null_text_error(self):
        with self.assertRaises(api.MeCabError):
            self.nm.parse(None)

    def test_parse_tostr_default(self):
        actual = self.nm.parse(self.text).strip()        
        actual = actual.replace('\n', os.linesep)                    # ???
        
        expected = self._23support_decode(self._mecab_parse('', self.text))

        self.assertEqual(actual, expected)
        
    def test_parse_tonode_default(self):
        mec = mecab.MeCab('-N2')
        actual = mec.parse(self.text, as_nodes=True)
        actual = [e for e in actual if not e.is_eos()]
        
        expected = self._23support_decode(self._mecab_parse('-N2', self.text)) 
        expected = [e for e in expected.split(os.linesep) if e != 'EOS']

        for i, e in enumerate(expected):
            s, f = expected[i].split()
            self.assertEqual(actual[i].surface, s)
            self.assertEqual(actual[i].feature, f)
        