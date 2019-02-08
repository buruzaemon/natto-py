# -*- coding: utf-8 -*-
'''Wrapper for MeCab dictionary information.'''

class DictionaryInfo(object):
    '''Representation of a MeCab DictionaryInfo struct.

    A list of dictionaries used by MeCab is returned by the dicts attribute of
    MeCab. Each dictionary information includes the attributes listed below.

    :ivar ptr: FFI pointer to the mecab_dictionary_info_t.
    :ivar filepath: Full path to the dictionary file.
    :ivar charset: Dictionary character set, e.g., SHIFT-JIS, UTF-8.
    :ivar size: Number of words registered in this dictionary.
    :ivar type: Dictionary type; 0 (SYS_DIC), 1 (USR_DIC), 2 (UNK_DIC)
    :ivar lsize: Left attributes size.
    :ivar rsize: Right attributes size.
    :ivar version: Dictionary version.
    :ivar next: Pointer to next dictionary information struct.

    Example usage::

        from natto import MeCab

        with MeCab() as nm:

            # first dictionary info is MeCab's system dictionary
            sysdic = nm.dicts[0]

            # print absolute path to system dictionary
            print(sysdic.filepath)
            ...
            /usr/local/lib/mecab/dic/ipadic/sys.dic

            # print system dictionary character encoding
            print(sysdic.charset)
            ...
            utf8

            # is this really the system dictionary?
            print(sysdic.is_sysdic())
            ...
            True
    '''
    _REPR_FMT = '<{}.{} dictionary={}, filepath="{}", charset={}, type={}>'

    # System dictionary
    SYS_DIC = 0
    # User dictionary.
    USR_DIC = 1
    # Unknown dictionary.
    UNK_DIC = 2

    def __init__(self, dptr, filepath, charset):
        self.ptr = dptr
        self.filepath = filepath
        self.charset = charset
        self.size = dptr.size
        self.type = dptr.type
        self.lsize = dptr.lsize
        self.rsize = dptr.rsize
        self.version = dptr.version
        self.next = getattr(dptr, 'next')

    def is_sysdic(self):
        '''Is this a system dictionary?

        :return: True if system dictionary, False otherwise.
        '''
        return self.type == self.SYS_DIC

    def is_usrdic(self):
        '''Is this a user-defined dictionary?

        :return: True if user-defined dictionary, False otherwise.
        '''
        return self.type == self.USR_DIC

    def is_unkdic(self):
        '''Is this an unknown dictionary?

        :return: True if unknown dictionary, False otherwise.
        '''
        return self.type == self.UNK_DIC

    def __repr__(self):
        '''Return a string representation of this MeCab dictionary.

        :return: str - string representation.
        '''
        return self._REPR_FMT.format(type(self).__module__,
                                     type(self).__name__,
                                     self.ptr,
                                     self.filepath,
                                     self.charset,
                                     self.type)

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
