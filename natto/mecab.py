# -*- coding: utf-8 -*-
'''The main interface to MeCab via natto-py.'''
import os
from .api import MeCabError
from .binding import _ffi_libmecab
from .dictionary import DictionaryInfo
from .environment import MeCabEnv
from .lattice import Lattice
from .node import MeCabNode
from .option_parse import OptionParse
from .support import string_support

class MeCab(object):
    '''The main interface to the MeCab library, wrapping the MeCab Tagger.

    Instantiate this once, per any MeCab options you wish to use.
    This interface allows for parsing Japanese into simple strings of morpheme
    surface and related features, or for iterating over MeCabNode instances
    which contain detailed information about the morphemes encompassed.

    Use the debug keyword argument when instantiating MeCab to output
    debugging messages to stderr.

    Example usage::

        from natto import MeCab

        # Use a Python with-statement to ensure mecab_destroy is invoked
        #
        with MeCab() as nm:

            # print MeCab version
            print(nm.version)
            ...
            0.996

            # print absolute path to MeCab library
            print(nm.libpath)
            ...
            /usr/local/lib/libmecab.so

            # parse text and print result
            print(nm.parse('この星の一等賞になりたいの卓球で俺は、そんだけ！'))
            ...
            この    連体詞,*,*,*,*,*,この,コノ,コノ
            星      名詞,一般,*,*,*,*,星,ホシ,ホシ
            の      助詞,連体化,*,*,*,*,の,ノ,ノ
            一等    名詞,一般,*,*,*,*,一等,イットウ,イットー
            賞      名詞,接尾,一般,*,*,*,賞,ショウ,ショー
            に      助詞,格助詞,一般,*,*,*,に,ニ,ニ
            なり    動詞,自立,*,*,五段・ラ行,連用形,なる,ナリ,ナリ
            たい    助動詞,*,*,*,特殊・タイ,基本形,たい,タイ,タイ
            の      助詞,連体化,*,*,*,*,の,ノ,ノ
            卓球    名詞,サ変接続,*,*,*,*,卓球,タッキュウ,タッキュー
            で      助詞,格助詞,一般,*,*,*,で,デ,デ
            俺      名詞,代名詞,一般,*,*,*,俺,オレ,オレ
            は      助詞,係助詞,*,*,*,*,は,ハ,ワ
            、      記号,読点,*,*,*,*,、,、,、
            そん    名詞,一般,*,*,*,*,そん,ソン,ソン
            だけ    助詞,副助詞,*,*,*,*,だけ,ダケ,ダケ
            ！      記号,一般,*,*,*,*,！,！,！
            EOS

            # parse text into Python Generator yielding MeCabNode instances,
            # and display much more detailed information about each morpheme
            for n in nm.parse('飛べねえ鳥もいるってこった。', as_nodes=True):
                if n.is_nor():
            ...     # morpheme surface
            ...     # part-of-speech ID (IPADIC)
            ...     # word cost
            ...     print("{}\\t{}\\t{}".format(n.surface, n.posid, n.wcost))
            ...
            飛べ    31      7175
            ねえ    25      6661
            鳥      38      4905
            も      16      4669
            いる    31      9109
            って    15      6984
            こっ    31      9587
            た      25      5500
            。      7       215

    '''
    MECAB_PATH = 'MECAB_PATH'
    MECAB_CHARSET = 'MECAB_CHARSET'

    _ERROR_EMPTY_STR = 'Text to parse cannot be None'
    _ERROR_INIT = 'Could not initialize MeCab: {}'
    _ERROR_NOTSTR = 'Text should be of type str'
    _ERROR_NULLPTR = 'Could not initialize MeCab'

    _REPR_FMT = ('<{}.{} pointer={}, libpath="{}", options={}, dicts={},'
                 ' version={}>')

    _FN_NBEST_TOSTR = 'mecab_nbest_sparse_tostr'
    _FN_NBEST_TONODE = 'mecab_nbest_init'
    _FN_TOSTR = 'mecab_sparse_tostr'
    _FN_TONODE = 'mecab_sparse_tonode'
    _FN_BCNBEST_TOSTR = 'mecab_lattice_nbest_tostr'
    _FN_BCTOSTR = 'mecab_lattice_tostr'
    
    _KW_ASNODES = 'as_nodes'
    _KW_CONSTRAINTS = 'morpheme_constraints'
    _KW_ANYBOUNDARY = 'any_boundary'

    MECAB_LATTICE_ONE_BEST = 1
    MECAB_LATTICE_NBEST = 2
    MECAB_LATTICE_PARTIAL = 4
    MECAB_LATTICE_MARGINAL_PROB = 8
    MECAB_LATTICE_ALTERNATIVE = 16
    MECAB_LATTICE_ALL_MORPHS = 32
    MECAB_LATTICE_ALLOCATE_SENTENCE = 64

    def __init__(self, options=None, **kwargs):
        '''Initializes the MeCab instance with the given options.

        Args:
            options: Optional string or dictionary of the MeCab options to be
                     used.
        Kwargs:
            debug (bool): Flag for outputting debug messages to stderr.

        Raises:
            SystemExit: An unrecognized option was passed in.
            MeCabError: An error occurred in locating the MeCab library;
                        or the FFI handle to MeCab could not be created.
        '''
        try:
            env = MeCabEnv(**kwargs)
            self.__ffi = _ffi_libmecab()
            self.__mecab = self.__ffi.dlopen(env.libpath)
            self.libpath = env.libpath

            # Python 2/3 string support
            self.__bytes2str, self.__str2bytes = string_support(env.charset)

            # Set up dictionary of MeCab options to use
            op = OptionParse(env.charset)
            self.options = op.parse_mecab_options(options)

            # Set up tagger pointer
            ostr = op.build_options_str(self.options)
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
            self.__bcparse2str = self.__bcparse_tostr(self._FN_BCNBEST_TOSTR)
            self.__bcparse2nodes = self.__bcparse_tonodes(format_feature)
        else:
            self.__parse2str = self.__parse_tostr(self._FN_TOSTR)
            self.__parse2nodes = self.__parse_tonodes(self._FN_TONODE,
                                                      format_feature)
            self.__bcparse2str = self.__bcparse_tostr(self._FN_BCTOSTR)
            self.__bcparse2nodes = self.__bcparse_tonodes(format_feature)

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
        if hasattr(self, '_MeCab__pointer') and hasattr(self, '_MeCab__mecab') and \
           hasattr(self, '_MeCab__ffi'):
            if self.pointer != self.__ffi.NULL and \
               self.__mecab != self.__ffi.NULL:
                self.__mecab.mecab_destroy(self.pointer)
        if hasattr(self, '_MeCab__mecab'):
            del self.__mecab
        if hasattr(self, '_MeCab__ffi'):
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
            feature: flag indicating whether or not to format the feature
                value for each node yielded.

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
                            yield mnode
                        nptr = getattr(nptr, 'next')

                    if fn_name == self._FN_NBEST_TONODE:
                        nptr = self.__mecab.mecab_nbest_next_tonode(
                            self.pointer)
            else:
                err = self.__mecab.mecab_strerror((self.pointer))
                raise MeCabError(self.__bytes2str(self.__ffi.string(err)))
        return _fn

    def __bcparse_tostr(self, fn_name):
        '''Builds and returns the MeCab function for boundary-constraint
        parsing Unicode text.

        Args:
            fn_name: MeCab function name that determines the function
                behavior, either 'mecab_lattice_tostr' or
                'mecab_lattice_nbest_tostr'.

        Returns:
            A function definition, tailored to boundary constraint parsing
            Unicode text and returning the result as a string suitable for
            display on stdout, using either the default or N-best behavior.
        '''
        def _fn(text, **kwargs):
            '''Boundary constraint parse text and return MeCab result as a string.'''
            with Lattice(self.__mecab, self.pointer, self.__ffi, fn_name, self.__enc) as lattice:
                morpheme_constraint = kwargs.get(self._KW_CONSTRAINTS, '.')
                any_boundary = kwargs.get(self._KW_ANYBOUNDARY, True)

                #if fn_name == self._FN_BCNBEST_TOSTR:
                n = self.options.get('nbest', 1)
                if n > 1:
                    lattice.set_nbest(n)
                    lattice.set_request_type(self.MECAB_LATTICE_NBEST)
                else:
                    lattice.set_request_type(self.MECAB_LATTICE_ONE_BEST)

                lattice.set_sentence(text)
                lattice.set_boundary_constraints(morpheme_constraint, any_boundary)

                res = lattice.parse()
                print('parse result: {}'.format(res))
                if res != self.__ffi.NULL:
                    return lattice.get_string()
                else:
                    raise MeCabError(lattice.get_error())
        return _fn

    def __bcparse_tonodes(self, format_feature=False):
        '''Builds and returns the MeCab function for parsing to nodes using
        morpheme boundary constraints.

        Args:
            format_feature: flag indicating whether or not to format the feature
                value for each node yielded.

        Returns:
            A function which returns a Generator, tailored to using boundary
            constraints and parsing as nodes, using either the default or
            N-best behavior.
        '''
        def _fn(text, **kwargs):
            '''Boundary constraint parse text and return MeCab result Generator.'''
            with Lattice(self.__mecab, self.pointer, self.__ffi, None, self.__enc) as lattice:
                morpheme_constraint = kwargs.get(self._KW_CONSTRAINTS, '.')
                any_boundary = kwargs.get(self._KW_ANYBOUNDARY, True)

                n = self.options.get('nbest', 1)
                if n > 1:
                    lattice.set_nbest(n)
                    lattice.set_request_type(self.MECAB_LATTICE_NBEST)
                else:
                    print(self.options)
                    lattice.set_request_type(self.MECAB_LATTICE_ONE_BEST)

                lattice.set_sentence(text)
                lattice.set_boundary_constraints(morpheme_constraint, any_boundary)

                res = lattice.parse()
                if res != self.__ffi.NULL:
                    for _ in range(n):
                        check = lattice.next()
                        if n==1 or check:
                            nptr = lattice.bos_node()
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
                                    yield mnode
                                nptr = getattr(nptr, 'next')
                else:
                    raise MeCabError(lattice.get_error())
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

    def parse(self, text, **kwargs):
        '''Parse the given text and return result from MeCab.

        :param text: the text to parse.
        :type text: str
        :param as_nodes: return generator of MeCabNodes if True;
            or string if False.
        :type as_nodes: bool, defaults to False
        :param morpheme_constraints: regular expression for morpheme boundary
            splitting; if non-None, then boundary constraint parsing will be
            used.
        :type morpheme_constraints: str
        :param any_boundary: flag for indicating default boundary token when
            using boundary constraint parsing.
        :type any_boundary: bool, defaults to True        
        :return: A single string containing the entire MeCab output;
            or a Generator yielding the MeCabNode instances.
        :raises: MeCabError
        '''
        if text is None:
            raise MeCabError(self._ERROR_EMPTY_STR)
        if not isinstance(text, str):
            raise MeCabError(self._ERROR_NOTSTR)

        as_nodes = kwargs.get(self._KW_ASNODES, False)

        #btext = self.__str2bytes(text)
        if as_nodes:
            if self._KW_CONSTRAINTS in kwargs:
                return self.__bcparse2nodes(text, **kwargs)
            else:
                return self.__parse2nodes(self.__str2bytes(text))
        else:
            if self._KW_CONSTRAINTS in kwargs:
                return self.__bcparse2str(text, **kwargs)
            else:
                return self.__parse2str(self.__str2bytes(text))


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
