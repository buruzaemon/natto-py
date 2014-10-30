# -*- coding: utf-8 -*-
import unittest
from .test_api import TestApi

def test_suite():
    suite = unittest.makeSuite(TestApi)
    return suite