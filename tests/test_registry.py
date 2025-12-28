#!/usr/bin/env python3

"""Unit tests for Registry singleton."""

import unittest

from ucm.Registry import Registry


class TestRegistry(unittest.TestCase):
    """Test Registry singleton functionality."""

    def test_singleton_pattern(self):
        """Test that Registry is a singleton."""
        reg1 = Registry()
        reg2 = Registry()
        self.assertIs(reg1, reg2)

    def test_set_and_get(self):
        """Test setting and getting registry values."""
        reg = Registry()
        reg.set("test_item", "test_value")
        self.assertEqual(reg.get("test_item"), "test_value")

    def test_get_nonexistent(self):
        """Test getting non-existent key returns None."""
        reg = Registry()
        self.assertIsNone(reg.get("this_key_definitely_does_not_exist_12345"))

    def test_overwrite_behavior(self):
        """Test overwrite parameter behavior."""
        reg = Registry()
        reg.set("overwrite_test", "first")
        reg.set("overwrite_test", "second", overwrite=False)
        self.assertEqual(reg.get("overwrite_test"), "first")

        reg.set("overwrite_test", "third", overwrite=True)
        self.assertEqual(reg.get("overwrite_test"), "third")


if __name__ == "__main__":
    unittest.main()
