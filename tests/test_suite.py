# -*- coding: utf-8 -*-
import unittest
from .test_api import TestApi
#from .test_binding import TestBinding
#from .test_option_parse import TestOptionParse

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(TestApi)
#    suite.addTest(TestBinding)
#    suite.addTest(TestOptionParse)
    return suite