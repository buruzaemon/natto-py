# -*- coding: utf-8 -*-
import codecs
import sys

if sys.version < '3':
    def _u(s, enc):
        """Transforms encoded byte string into Unicode."""
        return s.decode(enc)
    def _b(x, enc):
        """Transforms Unicode string into encoded bytes."""
        return x.encode(enc)
else:
    def _u(x, enc):
        """Identity function. Python3 strings are Unicode."""
        return x
    def _b(x, enc):
        """Transforms Unicode string into encoded bytes."""
        #return codecs.encode(x, enc)
        return x
