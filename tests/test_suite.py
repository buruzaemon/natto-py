# -*- coding: utf-8 -*-
'''Test suite for natto-py'''
import unittest
from .test_binding import TestBinding
from .test_dictionary import TestDictionary
from .test_mecab import TestMecab

def test_suite():
    '''Returns suite of tests for natto-py'''
    suite = unittest.TestSuite()
    suite.addTest(TestBinding)
    suite.addTest(TestDictionary)
    suite.addTest(TestMecab)
    return suite
