# -*- coding: utf-8 -*-
"""Test for natto.binding."""
import natto.binding as binding
import unittest

class TestBinding(unittest.TestCase):
    """Tests the functions in the natto.binding module."""

    def test_ffi_libmecab(self):
        ffi = binding._ffi_libmecab()
        self.assertIsNotNone(ffi)
