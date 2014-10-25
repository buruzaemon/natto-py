# -*- coding: utf-8 -*-
"""Test for natto.binding."""
import unittest

import natto.binding as binding

class TestBinding(unittest.TestCase):
    """Tests the  functions in the natto.binding module."""

    def test_ffi_libmecab(self):
        ffi = binding._ffi_libmecab()
        self.assertIsNotNone(ffi)
