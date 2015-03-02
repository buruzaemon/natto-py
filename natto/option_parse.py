# -*- coding: utf-8 -*-
import argparse
import sys
from .support import string_support

class OptionParse(object):
    # Mapping of mecab short-style configuration options to the `mecab`
    # tagger. See the `mecab` help for more details.
    _SUPPORTED_OPTS = {'-d' : 'dicdir',
                       '-u' : 'userdic',
                       '-l' : 'lattice_level',
                       '-O' : 'output_format_type',
                       '-a' : 'all_morphs',
                       '-N' : 'nbest',
                       '-p' : 'partial',
                       '-m' : 'marginal',
                       '-M' : 'max_grouping_size',
                       '-F' : 'node_format',
                       '-U' : 'unk_format',
                       '-B' : 'bos_format',
                       '-E' : 'eos_format',
                       '-S' : 'eon_format',
                       '-x' : 'unk_feature',
                       '-b' : 'input_buffer_size',
                       '-C' : 'allocate_sentence',
                       '-t' : 'theta',
                       '-c' : 'cost_factor'}
                       
    _BOOLEAN_OPTIONS = ['all-morphs', 'partial', 'marginal', 'allocate-sentence']      
    
    _NBEST_MAX = 512          
    
    _ERROR_NVALUE = 'Invalid N value'  
    _WARN_LATTICE_LEVEL = 'lattice-level is DEPRECATED, please use marginal or nbest'    
    
    def __init__(self, envch): 
        self.__bytes2str, self.__str2bytes = string_support(envch)
    
    def parse_mecab_options(self, options):
        '''Parses the MeCab options, returning them in a dictionary.
    
        Lattice-level option has been deprecated; please use marginal or nbest
        instead.
    
        :options string or dictionary of options to use when instantiating
                the MeCab instance. May be in short- or long-form, or in a
                Python dictionary.
    
        Returns:
            A dictionary of the specified MeCab options, where the keys are
            snake-cased names of the long-form of the option names.
    
        Raises:
            MeCabError: An invalid value for N-best was passed in.
        '''
        class MeCabArgumentParser(argparse.ArgumentParser):
            '''MeCab option parser for natto-py.'''
    
            def error(self, message):
                '''error(message: string)
    
                Raises ValueError.
                '''
                raise ValueError(message)
    
        options = options or {}
        dopts = {}
    
        if type(options) is dict:
            for name in iter(list(self._SUPPORTED_OPTS.values())):
                if name in options:
                    if options[name]:
                        val = options[name]
                        if isinstance(val, bytes):
                            val = self.__bytes2str(options[name])
                        dopts[name] = val
        else:
            p = MeCabArgumentParser()
            p.add_argument('-d', '--dicdir',
                           help='set DIR as a system dicdir',
                           action='store', dest='dicdir')
            p.add_argument('-u', '--userdic',
                           help='use FILE as a user dictionary',
                           action='store', dest='userdic')
            p.add_argument('-l', '--lattice-level',
                           help='lattice information level (DEPRECATED)',
                           action='store', dest='lattice_level', type=int)
            p.add_argument('-O', '--output-format-type',
                           help='set output format type (wakati, none,...)',
                           action='store', dest='output_format_type')
            p.add_argument('-a', '--all-morphs',
                           help='output all morphs (default false)',
                           action='store_true', default=False)
            p.add_argument('-N', '--nbest',
                           help='output N best results (default 1)',
                           action='store', dest='nbest', type=int)
            p.add_argument('-p', '--partial',
                           help='partial parsing mode (default false)',
                           action='store_true', default=False)
            p.add_argument('-m', '--marginal',
                           help='output marginal probability (default false)',
                           action='store_true', default=False)
            p.add_argument('-M', '--max-grouping-size',
                           help=('maximum grouping size for unknown words '
                                 '(default 24)'),
                           action='store', dest='max_grouping_size', type=int)
            p.add_argument('-F', '--node-format',
                           help='use STR as the user-defined node format',
                           action='store', dest='node_format')
            p.add_argument('-U', '--unk-format',
                           help=('use STR as the user-defined unknown '
                                 'node format'),
                           action='store', dest='unk_format')
            p.add_argument('-B', '--bos-format',
                           help=('use STR as the user-defined '
                                 'beginning-of-sentence format'),
                           action='store', dest='bos_format')
            p.add_argument('-E', '--eos-format',
                           help=('use STR as the user-defined '
                                 'end-of-sentence format'),
                           action='store', dest='eos_format')
            p.add_argument('-S', '--eon-format',
                           help=('use STR as the user-defined end-of-NBest '
                                 'format'),
                           action='store', dest='eon_format')
            p.add_argument('-x', '--unk-feature',
                           help='use STR as the feature for unknown word',
                           action='store', dest='unk_feature')
            p.add_argument('-b', '--input-buffer-size',
                           help='set input buffer size (default 8192)',
                           action='store', dest='input_buffer_size', type=int)
            p.add_argument('-C', '--allocate-sentence',
                           help='allocate new memory for input sentence',
                           action='store_true', dest='allocate_sentence',
                           default=False)
            p.add_argument('-t', '--theta',
                           help=('set temperature parameter theta '
                                 '(default 0.75)'),
                           action='store', dest='theta', type=float)
            p.add_argument('-c', '--cost-factor',
                           help='set cost factor (default 700)',
                           action='store', dest='cost_factor', type=int)
    
            opts = p.parse_args(options.split())
    
            for name in iter(list(self._SUPPORTED_OPTS.values())):
                if hasattr(opts, name):
                    v = getattr(opts, name)
                    if v:
                        dopts[name] = v
    
        # final checks
        if 'nbest' in dopts \
            and (dopts['nbest'] < 1 or dopts['nbest'] > self._NBEST_MAX):
            raise ValueError(self._ERROR_NVALUE)
    
        # warning for lattice-level deprecation
        if 'lattice_level' in dopts:
            sys.stderr.write('WARNING: {}\n'.format(self._WARN_LATTICE_LEVEL))
    
        return dopts
    
    def build_options_str(self, options):
        '''Returns a string concatenation of the MeCab options.
    
        Args:
            options: dictionary of options to use when instantiating the MeCab
                instance.
    
        Returns:
            A string concatenation of the options used when instantiating the
            MeCab instance, in long-form.
        '''
        opts = []
        for name in iter(list(self._SUPPORTED_OPTS.values())):
            if name in options:
                key = name.replace('_', '-')
                if key in self._BOOLEAN_OPTIONS:
                    if options[name]:
                        opts.append('--{}'.format(key))
                else:
                    opts.append('--{}={}'.format(key, options[name]))
    
        return self.__str2bytes(' '.join(opts))    