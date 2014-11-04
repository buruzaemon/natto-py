# -*- coding: utf-8 -*-
"""Test for natto.option_parse."""
import os
import re
import sys
import unittest
from StringIO import StringIO
from natto.environment import MeCabEnv
from natto.py3support import _u, _b
import natto.option_parse as op


print("\n=== Test Environment ===")
print("Platform: {0}".format(sys.platform))
print("MECAB_PATH: {0}".format(os.environ['MECAB_PATH']))
print("MECAB_CHARSET: {0}".format(os.environ['MECAB_CHARSET']))

class TestOptionParse(unittest.TestCase):
    """Tests the  functions in the natto.option_parse module."""

    def setUp(self):
        self.env = MeCabEnv()

    def test_parse_mecab_options_none(self):
        dopts = op._parse_mecab_options(None, self.env.charset, _b)
        self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_emptystr(self):
        dopts = op._parse_mecab_options("", self.env.charset, _b)
        self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_emptydict(self):
        dopts = op._parse_mecab_options({}, self.env.charset, _b)
        self.assertEqual(len(dopts), 0)

    def test_parse_mecab_options_dicdir(self):
        dopts = op._parse_mecab_options("-d/foo/bar", self.env.charset, _b)
        self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

        dopts = op._parse_mecab_options("-d /foo/bar",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

        dopts = op._parse_mecab_options("--dicdir=/foo/bar",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'dicdir':'/foo/bar'})

        dopts = op._parse_mecab_options({'dicdir':'/foo/bar'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'dicdir': _b('/foo/bar', self.env.charset)})

    def test_parse_mecab_options_userdic(self):
        dopts = op._parse_mecab_options("-u/baz/qux.dic",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

        dopts = op._parse_mecab_options("-u /baz/qux.dic",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

        dopts = op._parse_mecab_options("--userdic=/baz/qux.dic",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'userdic':'/baz/qux.dic'})

        dopts = op._parse_mecab_options({'userdic':'/baz/qux.dic'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'userdic':_b('/baz/qux.dic', self.env.charset)})

    def test_parse_mecab_options_latticelevel(self):
        # setting lattice-level issues warning on stderr
        orig_err = sys.stderr
        try:
            tmp_err = StringIO()
            sys.stderr = tmp_err

            dopts = op._parse_mecab_options("-l 777",
                                            self.env.charset, _b)
            self.assertDictEqual(dopts, {'lattice_level':777})

            res = re.search(op._WARN_LATTICE_LEVEL,
                            tmp_err.getvalue().strip())
            self.assertIsNotNone(res)
        finally:
            sys.stderr = orig_err

    def test_parse_mecab_options_outputformattype(self):
        dopts = op._parse_mecab_options("-Owakati",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'output_format_type':'wakati'})

        dopts = op._parse_mecab_options("-O wakati",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'output_format_type':'wakati'})

        dopts = op._parse_mecab_options("--output-format-type=wakati",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'output_format_type':'wakati'})

        dopts = op._parse_mecab_options({'output_format_type':'wakati'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'output_format_type':_b('wakati', self.env.charset)})

    def test_parse_mecab_options_allmorphs(self):
        dopts = op._parse_mecab_options("-a",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'all_morphs':True})

        dopts = op._parse_mecab_options("--all-morphs",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'all_morphs':True})

        dopts = op._parse_mecab_options({'all_morphs':True},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'all_morphs':True})

    def test_parse_mecab_options_nbest(self):
        dopts = op._parse_mecab_options("-N2",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'nbest':2})

        dopts = op._parse_mecab_options("-N 2",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'nbest':2})

        dopts = op._parse_mecab_options("--nbest=2",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'nbest':2})

        dopts = op._parse_mecab_options({'nbest':2},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'nbest':2})

        # ValueError with message if nbest is not an int
        with self.assertRaises(ValueError) as ctx:
            op._parse_mecab_options("-N0.99",
                                        self.env.charset, _b)
        self.assertIsNotNone(re.search('--nbest', str(ctx.exception)))


    def test_parse_mecab_options_partial(self):
        dopts = op._parse_mecab_options("-p",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'partial':True})

        dopts = op._parse_mecab_options("--partial",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'partial':True})

        dopts = op._parse_mecab_options({'partial':True},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'partial':True})

    def test_parse_mecab_options_marginal(self):
        dopts = op._parse_mecab_options("-m",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'marginal':True})

        dopts = op._parse_mecab_options("--marginal",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'marginal':True})

        dopts = op._parse_mecab_options({'marginal':True},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'marginal':True})

    def test_parse_mecab_options_maxgroupingsize(self):
        dopts = op._parse_mecab_options("-M99",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        dopts = op._parse_mecab_options("-M 99",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        dopts = op._parse_mecab_options("--max-grouping-size=99",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        dopts = op._parse_mecab_options({'max_grouping_size':99},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'max_grouping_size':99})

        # ValueError with message if max_grouping_size is not an int
        with self.assertRaises(ValueError) as ctx:
            op._parse_mecab_options("-M0.99",
                                        self.env.charset, _b)
        self.assertIsNotNone(re.search('--max-grouping-size',
                                       str(ctx.exception)))


    def test_parse_mecab_options_nodeformat(self):
        dopts = op._parse_mecab_options("-F%m\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'node_format':'%m\\n'})

        dopts = op._parse_mecab_options("-F %m\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'node_format':'%m\\n'})

        dopts = op._parse_mecab_options("--node-format=%m\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'node_format':'%m\\n'})

        dopts = op._parse_mecab_options({'node_format':'%m\\n'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'node_format':_b('%m\\n', self.env.charset)})

    def test_parse_mecab_options_unkformat(self):
        dopts = op._parse_mecab_options("-U???\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_format':'???\\n'})

        dopts = op._parse_mecab_options("-U ???\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_format':'???\\n'})

        dopts = op._parse_mecab_options("--unk-format=???\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_format':'???\\n'})

        dopts = op._parse_mecab_options({'unk_format':'???\\n'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_format':_b('???\\n', self.env.charset)})

    def test_parse_mecab_options_bosformat(self):
        dopts = op._parse_mecab_options("-B>>>\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

        dopts = op._parse_mecab_options("-B >>>\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

        dopts = op._parse_mecab_options("--bos-format=>>>\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'bos_format':'>>>\\n'})

        dopts = op._parse_mecab_options({'bos_format':'>>>\\n'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'bos_format':_b('>>>\\n', self.env.charset)})

    def test_parse_mecab_options_eosformat(self):
        dopts = op._parse_mecab_options("-E<<<\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

        dopts = op._parse_mecab_options("-E <<<\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

        dopts = op._parse_mecab_options("--eos-format=<<<\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eos_format':'<<<\\n'})

        dopts = op._parse_mecab_options({'eos_format':'<<<\\n'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eos_format': _b('<<<\\n', self.env.charset)})

    def test_parse_mecab_options_eonformat(self):
        dopts = op._parse_mecab_options("-S___\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eon_format':'___\\n'})

        dopts = op._parse_mecab_options("-S ___\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eon_format':'___\\n'})

        dopts = op._parse_mecab_options("--eon-format=___\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eon_format':'___\\n'})

        dopts = op._parse_mecab_options({'eon_format':'___\\n'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'eon_format': _b('___\\n', self.env.charset)})

    def test_parse_mecab_options_unkfeature(self):
        dopts = op._parse_mecab_options("-x!!!\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

        dopts = op._parse_mecab_options("-x !!!\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

        dopts = op._parse_mecab_options("--unk-feature=!!!\\n",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_feature':'!!!\\n'})

        dopts = op._parse_mecab_options({'unk_feature':'!!!\\n'},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'unk_feature': _b('!!!\\n', self.env.charset)})

    def test_parse_mecab_options_inputbuffersize(self):
        dopts = op._parse_mecab_options("-b8888",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        dopts = op._parse_mecab_options("-b 8888",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        dopts = op._parse_mecab_options("--input-buffer-size=8888",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        dopts = op._parse_mecab_options({'input_buffer_size':8888},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'input_buffer_size':8888})

        # ValueError with message if input_buffer_size is not an int
        with self.assertRaises(ValueError) as ctx:
            op._parse_mecab_options("-b0.99",
                                        self.env.charset, _b)
        self.assertIsNotNone(re.search('--input-buffer-size',
                                       str(ctx.exception)))

    def test_parse_mecab_options_allocatesentence(self):
        dopts = op._parse_mecab_options("-C",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'allocate_sentence':True})

        dopts = op._parse_mecab_options("--allocate-sentence",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'allocate_sentence':True})

        dopts = op._parse_mecab_options({'allocate_sentence':True},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'allocate_sentence':True})

    def test_parse_mecab_options_theta(self):
        dopts = op._parse_mecab_options("-t0.777",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'theta':0.777})

        dopts = op._parse_mecab_options("-t 0.777",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'theta':0.777})

        dopts = op._parse_mecab_options("--theta=0.777",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'theta':0.777})

        dopts = op._parse_mecab_options({'theta':0.777},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'theta':0.777})

        # ValueError and message on stderr if theta is not a float
        with self.assertRaises(ValueError) as ctx:
            op._parse_mecab_options("--theta=XXX",
                                        self.env.charset, _b)
        self.assertIsNotNone(re.search('--theta',
                                       str(ctx.exception)))

    def test_parse_mecab_options_costfactor(self):
        dopts = op._parse_mecab_options("-c666",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'cost_factor':666})

        dopts = op._parse_mecab_options("-c 666",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'cost_factor':666})

        dopts = op._parse_mecab_options("--cost-factor=666",
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'cost_factor':666})

        dopts = op._parse_mecab_options({'cost_factor':666},
                                        self.env.charset, _b)
        self.assertDictEqual(dopts, {'cost_factor':666})

        # ValueError with message if cost_factor is not an int
        with self.assertRaises(ValueError) as ctx:
            op._parse_mecab_options("-c0.99",
                                        self.env.charset, _b)
        self.assertIsNotNone(re.search('--cost-factor',
                                       str(ctx.exception)))

    def test_build_options_str(self):
        opts = op._build_options_str({'dicdir':'/foo',
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
                                      'unknown':1000}, self.env.charset, _b)
        self.assertIsNotNone(re.search(_b('--dicdir=/foo', self.env.charset), opts))
#        self.assertIsNotNone(re.search('--userdic=/bar', opts))
#        self.assertIsNotNone(re.search('--lattice-level=444', opts))
#        self.assertIsNotNone(re.search('--output-format-type=yomi', opts))
#        self.assertIsNotNone(re.search('--all-morphs', opts))
#        self.assertIsNotNone(re.search('--nbest=555', opts))
#        self.assertIsNotNone(re.search('--partial', opts))
#        self.assertIsNotNone(re.search('--marginal', opts))
#        self.assertIsNotNone(re.search('--max-grouping-size=666', opts))
#        self.assertIsNotNone(re.search('--node-format=node\\\\n', opts))
#        self.assertIsNotNone(re.search('--unk-format=unk\\\\n', opts))
#        self.assertIsNotNone(re.search('--bos-format=bos\\\\n', opts))
#        self.assertIsNotNone(re.search('--eos-format=eos\\\\n', opts))
#        self.assertIsNotNone(re.search('--eon-format=eon\\\\n', opts))
#        self.assertIsNotNone(re.search('--unk-feature=unkf\\\\n', opts))
#        self.assertIsNotNone(re.search('--input-buffer-size=777', opts))
#        self.assertIsNotNone(re.search('--allocate-sentence', opts))
#        self.assertIsNotNone(re.search('--theta=0.999', opts))
#        self.assertIsNotNone(re.search('--cost-factor=888', opts))
#        self.assertIsNone(re.search('--unknown', opts))
