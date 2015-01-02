# -*- coding: utf-8 -*-
'''The main interface to MeCab via natto-py.'''
import argparse
import os
import sys
from .api import MeCabError
from .binding import _ffi_libmecab
from .dictionary import DictionaryInfo
from .environment import MeCabEnv
from .node import MeCabNode

class MeCab(object):
    '''The main interface to the MeCab library, wrapping the MeCab Tagger.

    Instantiate this once, per any MeCab options you wish to use.
    This interface allows for parsing Japanese into simple strings of morpheme
    surface and related features, or for parsing as MeCab nodes which contain
    detailed information about the morphemes encompassed.

    Example usage::

        from natto import MeCab

        with MeCab() as nm:

            # output MeCab version
            print(nm.version)

            # output absolute path to MeCab library
            print(nm.libpath)

            # output file path and charset for the MeCab system dictionary
            sysdic = nm.dicts[0]
            print(sysdic.filepath)
            print(sysdic.charset)

            # parse a string
            print(nm.parse('この星の一等賞になりたいの卓球で俺は、そんだけ！'))

            # parse text into Python Generator yielding MeCabNode instances,
            # and display much more detailed information about each morpheme
            for n in nm.parse('飛べねえ鳥もいるってこった。', as_nodes=True):
                if n.is_nor():
                    print("{}\\t{}\\t{}".format(n.surface, n.posid, n.wcost))
    '''
    MECAB_PATH = 'MECAB_PATH'
    MECAB_CHARSET = 'MECAB_CHARSET'

    _ERROR_EMPTY_STR = 'Text to parse cannot be None'
    _ERROR_INIT = 'Could not initialize MeCab: {}'
    _ERROR_NOTSTR = 'Text should be of type str'
    _ERROR_NULLPTR = 'Could not initialize MeCab'
    _ERROR_NVALUE = 'Invalid N value'

    _REPR_FMT = ('<{}.{} pointer={}, libpath="{}", options={}, dicts={},'
                 ' version={}>')

    _FN_NBEST_TOSTR = 'mecab_nbest_sparse_tostr'
    _FN_NBEST_TONODE = 'mecab_nbest_init'
    _FN_TOSTR = 'mecab_sparse_tostr'
    _FN_TONODE = 'mecab_sparse_tonode'

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

    _BOOLEAN_OPTIONS = ['all-morphs', 'partial', 'marginal',
                        'allocate-sentence']

    _NBEST_MAX = 512

    _WARN_LATTICE_LEVEL = ('lattice-level is DEPRECATED, '
                           'please use marginal or nbest')

    def __parse_mecab_options(self, options):
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
            for name in iter(list(MeCab._SUPPORTED_OPTS.values())):
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

            for name in iter(list(MeCab._SUPPORTED_OPTS.values())):
                if hasattr(opts, name):
                    v = getattr(opts, name)
                    if v:
                        dopts[name] = v

        # final checks
        if 'nbest' in dopts \
            and (dopts['nbest'] < 1 or dopts['nbest'] > MeCab._NBEST_MAX):
            raise ValueError(self._ERROR_NVALUE)

        # warning for lattice-level deprecation
        if 'lattice_level' in dopts:
            sys.stderr.write('WARNING: {}\n'.format(MeCab._WARN_LATTICE_LEVEL))

        return dopts

    def __build_options_str(self, options):
        '''Returns a string concatenation of the MeCab options.

        Args:
            options: dictionary of options to use when instantiating the MeCab
                instance.

        Returns:
            A string concatenation of the options used when instantiating the
            MeCab instance, in long-form.
        '''
        opts = []
        for name in iter(list(MeCab._SUPPORTED_OPTS.values())):
            if name in options:
                key = name.replace('_', '-')
                if key in self._BOOLEAN_OPTIONS:
                    if options[name]:
                        opts.append('--{}'.format(key))
                else:
                    opts.append('--{}={}'.format(key, options[name]))

        return self.__str2bytes(' '.join(opts))

    def __init__(self, options=None):
        '''Initializes the MeCab instance with the given options.

        Args:
            options: Optional string or dictionary of the MeCab options to be
                     used.

        Raises:
            SystemExit: An unrecognized option was passed in.
            MeCabError: An error occurred in locating the MeCab library;
                        or the FFI handle to MeCab could not be created.
        '''
        try:
            env = MeCabEnv()
            self.__ffi = _ffi_libmecab()
            self.__mecab = self.__ffi.dlopen(env.libpath)
            self.libpath = env.libpath

            # Set up byte/Unicode converters (Python 3 support)
            def __23_support():
                if sys.version < '3':
                    def bytes2str(b):
                        '''Identity, returns the argument string (bytes).'''
                        return b
                    def str2bytes(s):
                        '''Identity, returns the argument string (bytes).'''
                        return s
                else:
                    def bytes2str(b):
                        '''Transforms bytes into string (Unicode).'''
                        return b.decode(env.charset)
                    def str2bytes(u):
                        '''Transforms Unicode into string (bytes).'''
                        return u.encode(env.charset)
                return(bytes2str, str2bytes)
            self.__bytes2str, self.__str2bytes = __23_support()

            # Set up dictionary of MeCab options to use
            self.options = self.__parse_mecab_options(options)

            # Set up tagger pointer
            ostr = self.__build_options_str(self.options)
            self.pointer = self.__mecab.mecab_new2(ostr)

            if self.pointer == self.__ffi.NULL:
                raise MeCabError(self._ERROR_NULLPTR)
        except EnvironmentError as err:
            raise MeCabError(err)
        except ValueError as verr:
            raise MeCabError(self._ERROR_INIT.format(str(verr)))

        # Set add'l MeCab options on the tagger as needed
        if 'partial' in self.options:
            self.__mecab.mecab_set_partial(self.pointer,
                                           self.options['partial'])
        if 'theta' in self.options:
            self.__mecab.mecab_set_theta(self.pointer, self.options['theta'])
        if 'lattice_level' in self.options:
            self.__mecab.mecab_set_lattice_level(self.pointer,
                                                 self.options['lattice_level'])
        if 'all_morphs' in self.options:
            self.__mecab.mecab_set_all_morphs(self.pointer,
                                              self.options['all_morphs'])

        format_feature = True if 'output_format_type' in self.options or \
            'node_format' in self.options else False

        # Set parsing routines for both parsing as strings and nodes
        # for both N-best and non-N-best
        if 'nbest' in self.options and self.options['nbest'] > 1:
            # N-best parsing requires lattice-level to be set
            if 'lattice_level' in self.options:
                lat = self.options['lattice_level']
            else:
                lat = 1
            self.__mecab.mecab_set_lattice_level(self.pointer, lat)

            self.__parse2str = self.__parse_tostr(self._FN_NBEST_TOSTR)
            self.__parse2nodes = self.__parse_tonodes(self._FN_NBEST_TONODE,
                                                      format_feature)
        else:
            self.__parse2str = self.__parse_tostr(self._FN_TOSTR)
            self.__parse2nodes = self.__parse_tonodes(self._FN_TONODE,
                                                      format_feature)

        # Prepare copy for list of MeCab dictionaries
        self.dicts = []
        dptr = self.__mecab.mecab_dictionary_info(self.pointer)
        while dptr != self.__ffi.NULL:
            fpath = self.__bytes2str(self.__ffi.string(dptr.filename))
            fpath = os.path.abspath(fpath)
            chset = self.__bytes2str(self.__ffi.string(dptr.charset))
            self.dicts.append(DictionaryInfo(dptr, fpath, chset))
            dptr = getattr(dptr, 'next')

        # Save value for MeCab's internal character encoding
        self.__enc = self.dicts[0].charset

        # Set MeCab version string
        self.version = self.__bytes2str( \
                            self.__ffi.string(self.__mecab.mecab_version()))

    def __del__(self):
        if hasattr(self, 'pointer') and hasattr(self, 'mecab') and \
           hasattr(self, 'ffi'):
            if self.pointer != self.__ffi.NULL and \
               self.__mecab != self.__ffi.NULL:
                self.__mecab.mecab_destroy(self.pointer)
        if hasattr(self, 'mecab'):
            del self.__mecab
        if hasattr(self, 'ffi'):
            del self.__ffi

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__del__()

    def __parse_tostr(self, fn_name):
        '''Builds and returns the MeCab function for parsing Unicode text.

        Args:
            fn_name: MeCab function name that determines the function
                behavior, either 'mecab_sparse_tostr' or
                'mecab_nbest_sparse_tostr'.

        Returns:
            A function definition, tailored to parsing Unicode text and
            returning the result as a string suitable for display on stdout,
            using either the default or N-best behavior.
        '''
        def _fn(text):
            '''Parse text and return MeCab result as a string.'''
            args = [self.pointer]
            if fn_name == self._FN_NBEST_TOSTR:
                args.append(self.options['nbest'])
            args.append(text)

            res = getattr(self.__mecab, fn_name)(*args)
            if res != self.__ffi.NULL:
                raw = self.__ffi.string(res)
                return self.__bytes2str(raw).strip()
            else:
                err = self.__mecab.mecab_strerror((self.pointer))
                raise MeCabError(self.__bytes2str(self.__ffi.string(err)))
        return _fn

    def __parse_tonodes(self, fn_name, format_feature=False):
        '''Builds and returns the MeCab function for parsing to nodes.

        Args:
            fn_name: MeCab function name that determines the function
                behavior, either 'mecab_sparse_tonode' or 'mecab_nbest_init'.

        Returns:
            A function which returns a Generator, tailored to parsing as nodes,
            using either the default or N-best behavior.
        '''
        def _fn(text):
            '''Parse text and return MeCab result as a node.'''
            if fn_name == self._FN_NBEST_TONODE:
                # N-best node parsing
                getattr(self.__mecab, fn_name)(self.pointer, text)
                nptr = self.__mecab.mecab_nbest_next_tonode(self.pointer)
                count = self.options['nbest']
            else:
                # default string-based node parsing
                nptr = getattr(self.__mecab, fn_name)(self.pointer, text)
                count = 1

            if nptr != self.__ffi.NULL:
                for _ in range(count):
                    while nptr != self.__ffi.NULL:
                        # skip over any BOS nodes, since mecab does
                        if nptr.stat != MeCabNode.BOS_NODE:
                            raws = self.__ffi.string(
                                nptr.surface[0:nptr.length])
                            surf = self.__bytes2str(raws).strip()

                            if format_feature:
                                sp = self.__mecab.mecab_format_node(
                                    self.pointer, nptr)
                                rawf = self.__ffi.string(sp)
                            else:
                                rawf = self.__ffi.string(nptr.feature)
                            feat = self.__bytes2str(rawf).strip()

                            mnode = MeCabNode(nptr, surf, feat)
                            yield(mnode)
                        nptr = getattr(nptr, 'next')

                    if fn_name == self._FN_NBEST_TONODE:
                        nptr = self.__mecab.mecab_nbest_next_tonode(
                            self.pointer)
            else:
                err = self.__mecab.mecab_strerror((self.pointer))
                raise MeCabError(self.__bytes2str(self.__ffi.string(err)))
        return _fn

    def __repr__(self):
        '''Returns a string representation of this MeCab instance.'''
        return self._REPR_FMT.format(type(self).__module__,
                                     type(self).__name__,
                                     self.pointer,
                                     self.libpath,
                                     self.options,
                                     self.dicts,
                                     self.version)

    def parse(self, text, as_nodes=False):
        '''Parse the given text.

        :param text: the text to parse.
        :type text: str
        :param as_nodes: flag indicating whether to parse as nodes or strings;
        :type as_nodes: bool, defaults to False
        :return: A single string containing the entire MeCab output;
            or a Generator yielding the MeCabNode instances.
        :raises: MeCabError
        '''
        if text is None:
            raise MeCabError(self._ERROR_EMPTY_STR)
        if not isinstance(text, str):
            raise MeCabError(self._ERROR_NOTSTR)

        btext = self.__str2bytes(text)
        if as_nodes:
            return self.__parse2nodes(btext)
        else:
            return self.__parse2str(btext)


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
