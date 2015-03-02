# -*- coding: utf-8 -*-
'''Internal-use wrapper interface to Lattice.'''
import re
from .support import string_support

class Lattice(object):
    '''Wrapper interface to the MeCab Lattice class.'''

    MECAB_ANY_BOUNDARY = 0
    MECAB_TOKEN_BOUNDARY = 1
    MECAB_INSIDE_TOKEN = 2

    def __init__(self, mecab, tagger, ffi, fn_name, envch):
        self.__mecab = mecab
        self.__tagger = tagger
        self.__ffi = ffi
        self.__fn_name = fn_name
        self.__lattice = self.__mecab.mecab_lattice_new()
        self.__bytes2str, self.__str2bytes = string_support(envch)

    def __del__(self):
        if hasattr(self, '_Lattice__mecab') and hasattr(self, '_Lattice__lattice'):
            if self.__lattice != self.__ffi.NULL:
                self.__mecab.mecab_lattice_destroy(self.__lattice)
                del self.__lattice

            if hasattr(self, '_Lattice__mecab'):
                del self.__mecab
            if hasattr(self, '_Lattice__tagger'):
                del self.__tagger
            if hasattr(self, '_Lattice__ffi'):
                del self.__ffi
            if hasattr(self, '_Lattice__fn_name'):
                del self.__fn_name
            if hasattr(self, '_Lattice__bytes2str'):
                del self.__bytes2str
            if hasattr(self, '_Lattice__str2bytes'):
                del self.__str2bytes

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__del__()

    def __split(self, pattern, text):
        '''Split text using the given pattern and return list of tuples of
        token and boolean indicating a pattern match.

        :param pattern: regular expression pattern.
        :type pattern: str
        :param text: text to split.
        :type text: str
        '''
        mark = 0
        patt = self.__str2bytes(pattern)
        for token in re.finditer(patt, text):
            if mark < token.start():
                yield (text[mark:token.start()], False)
                mark = token.start()
            yield (text[mark:token.end()], True)
            mark = token.end()
        if mark < len(text):
            yield (text[mark:], False)

    def set_request_type(self, req_type):
        '''Set request type for Lattice-based parsing.

        :param req_type: request type Lattice-based parsing.
        :type req_type: int
        '''
        self.__mecab.mecab_lattice_set_request_type(self.__lattice, req_type)

    def set_sentence(self, text):
        '''Set sentence text for Lattice-based parsing.

        :param text: target sentence for parsing.
        :type text: str
        '''
        self.__text = text
        self.__mecab.mecab_lattice_set_sentence(self.__lattice, self.__text)

    def set_boundary_constraints(self, morpheme_constraint, any_boundary):
        '''Set the morpheme constraint pattern and preferred boundary marker.

        :param morpheme_constraint: regular expression pattern for morpheme
            constraints.
        :type morpheme_constraint: str
        :param any_boundary: if True, use MECAB_ANY_BOUNDARY for default
            boundary marke; else use MECAB_INSIDE_TOKEN.
        :type any_boundary: bool
        '''
        if any_boundary:
            default_boundary = self.MECAB_ANY_BOUNDARY
        else:
            default_boundary = self.MECAB_INSIDE_TOKEN

        pos = 0
        self.__mecab.mecab_lattice_set_boundary_constraint(self.__lattice,
                                                           pos,
                                                           self.MECAB_TOKEN_BOUNDARY)

        for (token, match) in self.__split(morpheme_constraint, self.__text):
            pos += 1
            if match:
                boundary_constraint = self.MECAB_INSIDE_TOKEN
            else:
                boundary_constraint = default_boundary

            for _ in range(1, len(token)):
                self.__mecab.mecab_lattice_set_boundary_constraint(self.__lattice,
                                                                   pos,
                                                                   boundary_constraint)
                pos += 1
            self.__mecab.mecab_lattice_set_boundary_constraint(self.__lattice,
                                                               pos,
                                                               self.MECAB_TOKEN_BOUNDARY)

    def parse(self):
        '''Return result of applying Lattice-based node parsing. Parse result
        is obtained either thru get_string or by enumerating the nodes in the
        linked list from bos_node. c.f `mecab_parse_lattice in mecab.h <https://code.google.com/p/mecab/source/browse/trunk/mecab/src/mecab.h>`_.

        :return: Lattice-based parse result.
        '''
        return self.__mecab.mecab_parse_lattice(self.__tagger, self.__lattice)

    def get_string(self):
        '''Return string result of Lattice-based node parsing. c.f
        `mecab_lattice_tostr in mecab.h <https://code.google.com/p/mecab/source/browse/trunk/mecab/src/mecab.h>`_.

        :return: pointer to beginning-of-sentence node.
        '''
        args = [self.__lattice]
        res = getattr(self.__mecab, self.__fn_name)(*args)
        raw = self.__ffi.string(res)
        return self.__bytes2str(raw).strip()

    def next(self):
        '''Return pointer to next node in linked list when node parsing. c.f
        `mecab_lattice_next in mecab.h <https://code.google.com/p/mecab/source/browse/trunk/mecab/src/mecab.h>`_.

        :return: pointer to beginning-of-sentence node.
        '''
        return self.__mecab.mecab_lattice_next(self.__lattice)

    def bos_node(self):
        '''Return pointer to beginning-of-sentence node when node parsing. c.f
        `mecab_lattice_get_bos_node in mecab.h <https://code.google.com/p/mecab/source/browse/trunk/mecab/src/mecab.h>`_.

        :return: pointer to beginning-of-sentence node.
        '''
        return self.__mecab.mecab_lattice_get_bos_node(self.__lattice)

    def get_error(self):
        '''Return error string from Lattice. c.f. `mecab_lattice_strerror in
        mecab.h <https://code.google.com/p/mecab/source/browse/trunk/mecab/src/mecab.h>`_.

        :return: error string from Lattice.
        '''
        err = self.__lattice.strerror()
        return self.__bytes2str(self.__ffi.string(err))

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
