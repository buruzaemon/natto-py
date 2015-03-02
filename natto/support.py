# -*- coding: utf-8 -*-
import sys

def string_support(py3enc):
    # Set up byte/Unicode converters (Python 3 support)
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
