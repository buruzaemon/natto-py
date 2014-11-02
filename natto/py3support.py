# -*- coding: utf-8 -*-
import codecs
import sys

if sys.version < '3':
    def _u(s, enc):
        return s.decode(enc)
    def _b(x, enc):
        return x.encode(enc)
else:
    def _u(x, enc):
        return x
    def _b(x, enc):
        return codecs.encode(x, enc)
