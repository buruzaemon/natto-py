# -*- coding: utf-8 -*-
'''Internal-use functions for string- and byte-conversion for supporting Python
2 and 3.'''
import re
import sys

REGEXTYPE = type(re.compile(''))

def string_support(py3enc):
    '''Create byte-to-string and string-to-byte conversion functions for
    internal use.

    :param py3enc: Encoding used by Python 3 environment.
    :type py3enc: str
    '''
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
            return b.decode(py3enc)
        def str2bytes(u):
            '''Transforms Unicode into string (bytes).'''
            return u.encode(py3enc)
    return (bytes2str, str2bytes)

def splitter_support(py2enc):
    '''Create tokenizer for use in boundary constraint parsing.

    :param py2enc: Encoding used by Python 2 environment.
    :type py2enc: str
    '''
    if sys.version < '3':
        def _fn_sentence(pattern, sentence):
            if REGEXTYPE == type(pattern):
                if pattern.flags & re.UNICODE:
                    return sentence.decode(py2enc)
                else:
                    return sentence
            else:
                return sentence
        def _fn_token2str(pattern):
            if REGEXTYPE == type(pattern):
                if pattern.flags & re.UNICODE:
                    def _fn(token):
                        return token.encode(py2enc)
                else:
                    def _fn(token):
                        return token
            else:
                def _fn(token):
                    return token
            return _fn
    else:
        def _fn_sentence(pattern, sentence):
            return sentence
        def _fn_token2str(pattern):
            def _fn(token):
                return token
            return _fn

    def _fn_tokenize_pattern(text, pattern):
        pos = 0
        sentence = _fn_sentence(pattern, text)
        postprocess = _fn_token2str(pattern)
        for m in re.finditer(pattern, sentence):
            if pos < m.start():
                token = postprocess(sentence[pos:m.start()])
                yield (token.strip(), False)
                pos = m.start()
            token = postprocess(sentence[pos:m.end()])
            yield (token.strip(), True)
            pos = m.end()
        if pos < len(sentence):
            token = postprocess(sentence[pos:])
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
