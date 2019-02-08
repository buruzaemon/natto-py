import os
import sys
from natto.mecab import MeCab
from subprocess import Popen, PIPE

__all__ = ['Test23Support']

class Test23Support(object):
    def _u2str(self, text):
        if sys.version < '3':
            return text.encode(self.env.charset)
        else:
            return text

    def _b2u(self, text):
        return text.decode(self.env.charset)

    def _2unicode(self, text):
        if sys.version < '3':
            return text.decode(self.env.charset)
        else:
            return text

    #def _2str(self, text):
    def _mecab_input(self, text):
        if sys.version < '3':
            return text
        else:
            return text.encode(self.env.charset)

    def _2bytes(self, text):
        if sys.version < '3':
            return text
        else:
            return text.decode(self.env.charset)

    def _mecab_output(self, text):
        return self._2bytes(text)


# full path to MeCab library is required for testing...
if not os.getenv(MeCab.MECAB_PATH):
    raise EnvironmentError('Please set MECAB_PATH before running the tests')
# as well as the character encoding used internally by MeCab...
if not os.getenv(MeCab.MECAB_CHARSET):
    raise EnvironmentError('Please set MECAB_CHARSET before running the tests')

# and the mecab 0.996 executable is invoked during the tests...
try:
    res = Popen(['mecab', '-v'], stdout=PIPE).communicate()
    line = res[0]
    exp = 'mecab of 0.996'
    if sys.version >= '3':
        line = line.decode(os.getenv(MeCab.MECAB_CHARSET))
    if not line.startswith(exp):
        raise EnvironmentError('Please check your mecab installation')
except StandardError as err:
    raise EnvironmentError(err)

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
