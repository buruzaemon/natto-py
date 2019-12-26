# -*- coding: utf-8 -*-
'''The main interface to MeCab via natto-py.'''
import logging
import os
import re
from .api import MeCabError
from .binding import _ffi_libmecab
from .dictionary import DictionaryInfo
from .environment import MeCabEnv
from .node import MeCabNode
from .option_parse import OptionParse
from .support import string_support, splitter_support

logging.basicConfig()
logger = logging.getLogger('natto.mecab')

class MeCab(object):
    '''The main interface to the MeCab library, wrapping the MeCab Tagger.

    Instantiate this once, per any MeCab options you wish to use.
    This interface allows for parsing Japanese into simple strings of morpheme
    surface and related features, or for iterating over MeCabNode instances
    which contain detailed information about the morphemes encompassed.

    Configure logging before instantiating MeCab to see debug messages::
    
        import logging

        fmt='%(asctime)s : %(levelname)s : %(message)s'

        logging.basicConfig(format=fmt, level=logging.DEBUG)

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
    _ERROR_NULLPTR = 'Could not initialize MeCab {}'
    _ERROR_MISSING_NL = 'Partial-parsing requires new-line char at end of text'
    _ERROR_BOUNDARY = 'boundary_constraints must be re or str'
    _ERROR_FEATURE = 'feature_constraints must be tuple'
    _ERROR_NODEFORMAT = 'Could not format node with surface {}: {}'

    _REPR_FMT = ('<{}.{} model={}, tagger={}, lattice={},'
                 ' libpath="{}", options={}, dicts={}, version={}>')

    _FN_NBEST_TOSTR = 'mecab_nbest_sparse_tostr'
    _FN_NBEST_TONODE = 'mecab_nbest_init'
    _FN_TOSTR = 'mecab_sparse_tostr'
    _FN_TONODE = 'mecab_sparse_tonode'
    _FN_BCNBEST_TOSTR = 'mecab_lattice_nbest_tostr'
    _FN_BCTOSTR = 'mecab_lattice_tostr'

    _KW_ASNODES = 'as_nodes'
    _KW_BOUNDARY = 'boundary_constraints'
    _KW_FEATURE = 'feature_constraints'

    _REGEXTYPE = type(re.compile(''))

    MECAB_LATTICE_ONE_BEST = 1
    MECAB_LATTICE_NBEST = 2
    MECAB_LATTICE_PARTIAL = 4
    MECAB_LATTICE_MARGINAL_PROB = 8
    MECAB_LATTICE_ALTERNATIVE = 16
    MECAB_LATTICE_ALL_MORPHS = 32
    MECAB_LATTICE_ALLOCATE_SENTENCE = 64

    MECAB_ANY_BOUNDARY = 0
    MECAB_TOKEN_BOUNDARY = 1
    MECAB_INSIDE_TOKEN = 2

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

            # Python 2/3 sentence splitter/tokenizer support
            self.__split_pattern, self.__split_features = splitter_support(env.charset)

            # Set up dictionary of MeCab options to use
            op = OptionParse(env.charset)
            self.options = op.parse_mecab_options(options)

            # Set up tagger pointer
            ostr = op.build_options_str(self.options)

            self.model = self.__mecab.mecab_model_new2(ostr)
            if self.model == self.__ffi.NULL:
                logger.error(self._ERROR_NULLPTR.format('Model'))
                raise MeCabError(self._ERROR_NULLPTR.format('Model'))

            self.tagger = self.__mecab.mecab_model_new_tagger(self.model)
            if self.tagger == self.__ffi.NULL:
                logger.error(self._ERROR_NULLPTR.format('Tagger'))
                raise MeCabError(self._ERROR_NULLPTR.format('Tagger'))

            self.lattice = self.__mecab.mecab_model_new_lattice(self.model)
            if self.lattice == self.__ffi.NULL:
                logger.error(self._ERROR_NULLPTR.format('Lattice'))
                raise MeCabError(self._ERROR_NULLPTR.format('Lattice'))

            n = self.options.get('nbest', 1)
            if n > 1:
                req_type = self.MECAB_LATTICE_NBEST
            else:
                req_type = self.MECAB_LATTICE_ONE_BEST
            self.__mecab.mecab_lattice_set_request_type(self.lattice, req_type)

            if 'partial' in self.options:
                self.__mecab.mecab_lattice_add_request_type(
                    self.lattice, self.MECAB_LATTICE_PARTIAL)

            if 'marginal' in self.options:
                self.__mecab.mecab_lattice_add_request_type(
                    self.lattice, self.MECAB_LATTICE_MARGINAL_PROB)

            if 'all_morphs' in self.options:
                # required when node parsing
                self.__mecab.mecab_lattice_add_request_type(
                    self.lattice, self.MECAB_LATTICE_ALL_MORPHS)

            if 'allocate_sentence' in self.options:
                self.__mecab.mecab_lattice_add_request_type(
                    self.lattice, self.MECAB_LATTICE_ALLOCATE_SENTENCE)

            # Prepare copy for list of MeCab dictionaries
            self.dicts = []
            dptr = self.__mecab.mecab_model_dictionary_info(self.model)
            while dptr != self.__ffi.NULL:
                fpath = self.__bytes2str(self.__ffi.string(dptr.filename))
                fpath = os.path.abspath(fpath)
                chset = self.__bytes2str(self.__ffi.string(dptr.charset))
                self.dicts.append(DictionaryInfo(dptr, fpath, chset))
                dptr = getattr(dptr, 'next')

            # Save value for MeCab's internal character encoding
            self.__enc = self.dicts[0].charset

            # Set MeCab version string
            self.version = self.__bytes2str(
                self.__ffi.string(self.__mecab.mecab_version()))
        except EnvironmentError as err:
            logger.error(self._ERROR_INIT.format(str(err)))
            raise MeCabError(err)
        except ValueError as verr:
            logger.error(self._ERROR_INIT.format(str(verr)))
            raise MeCabError(self._ERROR_INIT.format(str(verr)))

    def __del__(self):
        if hasattr(self, 'lattice') and hasattr(self, '_MeCab__ffi'):
            if self.lattice != self.__ffi.NULL:
                self.__mecab.mecab_lattice_destroy(self.lattice)
        if hasattr(self, 'tagger') and hasattr(self, '_MeCab__ffi'):
            if self.tagger != self.__ffi.NULL:
                self.__mecab.mecab_destroy(self.tagger)
        if hasattr(self, 'model') and hasattr(self, '_MeCab__ffi'):
            if self.model != self.__ffi.NULL:
                self.__mecab.mecab_model_destroy(self.model)
        if hasattr(self, '_MeCab__mecab'):
            del self.__mecab
        if hasattr(self, '_MeCab__ffi'):
            del self.__ffi

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__del__()

    def __parse_tostr(self, text, **kwargs):
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
        n = self.options.get('nbest', 1)

        if self._KW_BOUNDARY in kwargs:
            patt = kwargs.get(self._KW_BOUNDARY, '.')
            tokens = list(self.__split_pattern(text, patt))
            text = ''.join([t[0] for t in tokens])

            btext = self.__str2bytes(text)
            self.__mecab.mecab_lattice_set_sentence(self.lattice, btext)

            bpos = 0
            self.__mecab.mecab_lattice_set_boundary_constraint(
                self.lattice, bpos, self.MECAB_TOKEN_BOUNDARY)

            for (token, match) in tokens:
                bpos += 1
                if match:
                    mark = self.MECAB_INSIDE_TOKEN
                else:
                    mark = self.MECAB_ANY_BOUNDARY

                for _ in range(1, len(self.__str2bytes(token))):
                    self.__mecab.mecab_lattice_set_boundary_constraint(
                        self.lattice, bpos, mark)
                    bpos += 1
                self.__mecab.mecab_lattice_set_boundary_constraint(
                    self.lattice, bpos, self.MECAB_TOKEN_BOUNDARY)
        elif self._KW_FEATURE in kwargs:
            features = kwargs.get(self._KW_FEATURE, ())
            fd = {morph: self.__str2bytes(feat) for morph, feat in features}

            tokens = self.__split_features(text, [e[0] for e in features])
            text = ''.join([t[0] for t in tokens])

            btext = self.__str2bytes(text)
            self.__mecab.mecab_lattice_set_sentence(self.lattice, btext)

            bpos = 0
            for chunk, match in tokens:
                c = len(self.__str2bytes(chunk))
                if match == True:
                    self.__mecab.mecab_lattice_set_feature_constraint(
                        self.lattice, bpos, bpos+c, fd[chunk])
                bpos += c
        else:
            btext = self.__str2bytes(text)
            self.__mecab.mecab_lattice_set_sentence(self.lattice, btext)

        self.__mecab.mecab_parse_lattice(self.tagger, self.lattice)

        if n > 1:
            res = self.__mecab.mecab_lattice_nbest_tostr(self.lattice, n)
        else:
            res = self.__mecab.mecab_lattice_tostr(self.lattice)

        if res != self.__ffi.NULL:
            raw = self.__ffi.string(res)
            return self.__bytes2str(raw).strip(os.linesep)
        else:
            err = self.__mecab.mecab_lattice_strerror(self.lattice)
            logger.error(self.__bytes2str(self.__ffi.string(err)))
            raise MeCabError(self.__bytes2str(self.__ffi.string(err)))

    def __parse_tonodes(self, text, **kwargs):
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
        n = self.options.get('nbest', 1)

        try:
            if self._KW_BOUNDARY in kwargs:
                patt = kwargs.get(self._KW_BOUNDARY, '.')
                tokens = list(self.__split_pattern(text, patt))
                text = ''.join([t[0] for t in tokens])

                btext = self.__str2bytes(text)
                self.__mecab.mecab_lattice_set_sentence(self.lattice, btext)

                bpos = 0
                self.__mecab.mecab_lattice_set_boundary_constraint(
                    self.lattice, bpos, self.MECAB_TOKEN_BOUNDARY)

                for (token, match) in tokens:
                    bpos += 1
                    if match:
                        mark = self.MECAB_INSIDE_TOKEN
                    else:
                        mark = self.MECAB_ANY_BOUNDARY

                    for _ in range(1, len(self.__str2bytes(token))):
                        self.__mecab.mecab_lattice_set_boundary_constraint(
                            self.lattice, bpos, mark)
                        bpos += 1
                    self.__mecab.mecab_lattice_set_boundary_constraint(
                        self.lattice, bpos, self.MECAB_TOKEN_BOUNDARY)
            elif self._KW_FEATURE in kwargs:
                features = kwargs.get(self._KW_FEATURE, ())
                fd = {morph: self.__str2bytes(feat) for morph, feat in features}

                tokens = self.__split_features(text, [e[0] for e in features])
                text = ''.join([t[0] for t in tokens])

                btext = self.__str2bytes(text)
                self.__mecab.mecab_lattice_set_sentence(self.lattice, btext)

                bpos = 0
                for chunk, match in tokens:
                    c = len(self.__str2bytes(chunk))
                    if match:
                        self.__mecab.mecab_lattice_set_feature_constraint(
                            self.lattice, bpos, bpos+c, fd[chunk])
                    bpos += c
            else:
                btext = self.__str2bytes(text)
                self.__mecab.mecab_lattice_set_sentence(self.lattice, btext)

            self.__mecab.mecab_parse_lattice(self.tagger, self.lattice)

            for _ in range(n):
                check = self.__mecab.mecab_lattice_next(self.lattice)
                if n == 1 or check:
                    nptr = self.__mecab.mecab_lattice_get_bos_node(self.lattice)
                    while nptr != self.__ffi.NULL:
                        # skip over any BOS nodes, since mecab does
                        if nptr.stat != MeCabNode.BOS_NODE:
                            raws = self.__ffi.string(
                                nptr.surface[0:nptr.length])
                            surf = self.__bytes2str(raws).strip(os.linesep)

                            if 'output_format_type' in self.options or \
                               'node_format' in self.options:
                                sp = self.__mecab.mecab_format_node(
                                    self.tagger, nptr)
                                if sp != self.__ffi.NULL:
                                    rawf = self.__ffi.string(sp)
                                else:
                                    err = self.__mecab.mecab_strerror(
                                            self.tagger)
                                    err = self.__bytes2str(
                                            self.__ffi.string(err))
                                    msg = self._ERROR_NODEFORMAT.format(
                                            surf, err)
                                    raise MeCabError(msg)
                            else:
                                rawf = self.__ffi.string(nptr.feature)
                            feat = self.__bytes2str(rawf).strip(os.linesep)

                            mnode = MeCabNode(nptr, surf, feat)
                            yield mnode
                        nptr = getattr(nptr, 'next')
        except GeneratorExit:
            logger.debug('close invoked on generator')
        except MeCabError:
            raise
        except:
            err = self.__mecab.mecab_lattice_strerror(self.lattice)
            logger.error(self.__bytes2str(self.__ffi.string(err)))
            raise MeCabError(self.__bytes2str(self.__ffi.string(err)))

    def __repr__(self):
        '''Returns a string representation of this MeCab instance.'''
        return self._REPR_FMT.format(type(self).__module__,
                                     type(self).__name__,
                                     self.model,
                                     self.tagger,
                                     self.lattice,
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
        :param boundary_constraints: regular expression for morpheme boundary
            splitting; if non-None and feature_constraints is None, then
            boundary constraint parsing will be used.
        :type boundary_constraints: str or re
        :param feature_constraints: tuple containing tuple instances of
            target morpheme and corresponding feature string in order
            of precedence; if non-None and boundary_constraints is None,
            then feature constraint parsing will be used.
        :type feature_constraints: tuple
        :return: A single string containing the entire MeCab output;
            or a Generator yielding the MeCabNode instances.
        :raises: MeCabError
        '''
        if text is None:
            logger.error(self._ERROR_EMPTY_STR)
            raise MeCabError(self._ERROR_EMPTY_STR)
        elif not isinstance(text, str):
            logger.error(self._ERROR_NOTSTR)
            raise MeCabError(self._ERROR_NOTSTR)
        elif 'partial' in self.options and not text.endswith("\n"):
            logger.error(self._ERROR_MISSING_NL)
            raise MeCabError(self._ERROR_MISSING_NL)

        if self._KW_BOUNDARY in kwargs:
            val = kwargs[self._KW_BOUNDARY]
            if not isinstance(val, self._REGEXTYPE) and not isinstance(val, str):
                logger.error(self._ERROR_BOUNDARY)
                raise MeCabError(self._ERROR_BOUNDARY)
        elif self._KW_FEATURE in kwargs:
            val = kwargs[self._KW_FEATURE]
            if not isinstance(val, tuple):
                logger.error(self._ERROR_FEATURE)
                raise MeCabError(self._ERROR_FEATURE)

        as_nodes = kwargs.get(self._KW_ASNODES, False)

        if as_nodes:
            return self.__parse_tonodes(text, **kwargs)
        else:
            return self.__parse_tostr(text, **kwargs)

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
