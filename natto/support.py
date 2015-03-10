# -*- coding: utf-8 -*-
'''Internal-use functions for string- and byte-conversion for supporting Python
2 and 3.'''
import sys

def string_support(py3enc):
    '''Create byte-to-string and string-to-byte conversion functions for
    internal use.

    :param py3enc: Encoding used by Python 3 environment.
    :type py3enc: str
    '''
    # Set up byte-str converters (Python 3 support)
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
    return(bytes2str, str2bytes)

def unicode_support(enc):
    '''Create string-to-Unicode and Unicode-to-byte conversion functions for
    internal use.

    :param enc: Encoding used.
    :type enc: str
    '''
    # Set up byte-Unicode converters (Python 3 support)
    if sys.version < '3':
        def str2unicode(b):
            '''Transforms bytes (str) into Unicode.'''
            return b.decode(enc)
        def unicode2bytes(u):
            '''Transforms Unicode into bytes (str).'''
            return u.encode(enc)
    else:
        def str2unicode(s):
            '''Identity, returns the argument string (Unicode).'''
            return s
        def unicode2bytes(u):
            '''Transforms Unicode into bytes (str).'''
            return u.encode(enc)
    return(str2unicode, unicode2bytes)
    
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
