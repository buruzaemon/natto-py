# -*- coding: utf-8 -*-
'''Internal-use functions for Mecab-Python string- and byte-conversion.'''
import re

REGEXTYPE = type(re.compile(''))

def string_support(enc):
    '''Create byte-to-string and string-to-byte conversion functions for
    internal use.

    :param enc: Character encoding
    :type enc: str
    '''

    def bytes2str(b):
        '''Transforms bytes into string (Unicode).'''
        return b.decode(enc)
    def str2bytes(u):
        '''Transforms Unicode into string (bytes).'''
        return u.encode(enc)

    return (bytes2str, str2bytes)

def splitter_support():
    '''Create tokenizer for use in boundary constraint parsing.'''

    def _fn_tokenize_pattern(text, pattern):
        pos = 0
        for m in re.finditer(pattern, text):
            if pos < m.start():
                token = text[pos:m.start()]
                yield (token.strip(), False)
                pos = m.start()
            token = text[pos:m.end()]
            yield (token.strip(), True)
            pos = m.end()
        if pos < len(text):
            token = text[pos:]
            yield (token.strip(), False)

    def _fn_tokenize_features(text, features):
        acc = []
        acc.append((text.strip(), False))

        for feat in features:
            for i,e in enumerate(acc):
                if e[1]==False:
                    tmp = list(_fn_tokenize_pattern(e[0], feat))
                    if len(tmp) > 0:
                        acc.pop(i)
                        acc[i:i] = tmp
        return acc

    return _fn_tokenize_pattern, _fn_tokenize_features

'''
Copyright (c) 2022, Brooke M. Fujita.
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
