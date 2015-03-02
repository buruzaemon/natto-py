# -*- coding: utf-8 -*-
import re
from .node import MeCabNode
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
        print 'ok, let us go!'
        if hasattr(self, '_Lattice__mecab') and hasattr(self, '_Lattice__lattice'):
            if self.__lattice != self.__ffi.NULL:
                print 'cleaning up!'
                self.__mecab.mecab_lattice_destroy(self.__lattice)
                del self.__lattice

        if hasattr(self, '_Lattice__mecab'):
            print 'cleaning up! 1'
            del self.__mecab
        if hasattr(self, '_Lattice__tagger'):
            print 'cleaning up! 2'
            del self.__tagger
        if hasattr(self, '_Lattice__ffi'):
            print 'cleaning up! 3'
            del self.__ffi
        if hasattr(self, '_Lattice__fn_name'):
            print 'cleaning up! 4'
            del self.__fn_name
        if hasattr(self, '_Lattice__bytes2str'):
            print 'cleaning up! 5'
            del self.__bytes2str
        if hasattr(self, '_Lattice__str2bytes'):
            print 'cleaning up! 6'
            del self.__str2bytes

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__del__()

    def __split(self, pattern, text):
        '''Split text using the given pattern, return list of tuples
        (token, True/False) for boundary constraint parsing.'''
        # IFF using re.U, then text and constraints pattern should be unicode!
        mark = 0
        patt = self.__str2bytes(pattern)
        for t in re.finditer(patt, text):
            if mark < t.start():
                yield (text[mark:t.start()], False)
                mark = t.start()
            yield (text[mark:t.end()], True)
            mark = t.end()
        if mark < len(text):
            yield (text[mark:], False)

    def set_request_type(self, req_type):
        self.__mecab.mecab_lattice_set_request_type(self.__lattice, req_type)

    def set_sentence(self, text):
        self.__text = text
        self.__mecab.mecab_lattice_set_sentence(self.__lattice, text)

    def set_boundary_constraints(self, morpheme_constraint, any_boundary):    
        if any_boundary:
            default_boundary = self.MECAB_ANY_BOUNDARY
        else:
            default_boundary = self.MECAB_INSIDE_TOKEN
            
        pos = 0
        self.__mecab.mecab_lattice_set_boundary_constraint(self.__lattice,
                pos, self.MECAB_TOKEN_BOUNDARY)

        for (token, match) in self.__split(morpheme_constraint, self.__text):
            pos += 1
            if match:
                boundary_constraint = self.MECAB_INSIDE_TOKEN
            else:
                boundary_constraint = default_boundary
          
            for i in range(1, len(token)):
                self.__mecab.mecab_lattice_set_boundary_constraint(
                        self.__lattice, pos, boundary_constraint)
                pos += 1
            self.__mecab.mecab_lattice_set_boundary_constraint(self.__lattice,
                    pos, self.MECAB_TOKEN_BOUNDARY)

    def parse(self):
        return self.__mecab.mecab_parse_lattice(self.__tagger, self.__lattice)

    def get_string(self):
        args = [ self.__lattice ]
        res = getattr(self.__mecab, self.__fn_name)(*args)
        raw = self.__ffi.string(res)
        return self.__bytes2str(raw).strip()

    def next(self):
        return self.__mecab.mecab_lattice_next(self.__lattice)

    def bos_node(self):
        return self.__mecab.mecab_lattice_get_bos_node(self.__lattice)

    def get_error(self):
        err = self.__lattice.strerror()
        return self.__bytes2str(self.__ffi.string(err))
