#!/usr/bin/env python3

"""Unit tests for configuration handling."""

import os
import tempfile
import unittest

from ucm.UserConfig import UserConfig


class TestUserConfig(unittest.TestCase):
    """Test UserConfig singleton and methods."""

    def test_singleton_pattern(self):
        """Test that UserConfig is a singleton."""
        config1 = UserConfig()
        config2 = UserConfig()
        self.assertIs(config1, config2)

    def test_set_and_get(self):
        """Test setting and getting values."""
        config = UserConfig()
        config.set("test_key", "test_value")
        self.assertEqual(config.get("test_key"), "test_value")

    def test_set_no_overwrite(self):
        """Test that overwrite=False preserves existing values."""
        config = UserConfig()
        config.set("test_key2", "original")
        config.set("test_key2", "new", overwrite=False)
        self.assertEqual(config.get("test_key2"), "original")

    def test_get_nonexistent(self):
        """Test getting non-existent key returns None."""
        config = UserConfig()
        self.assertIsNone(config.get("nonexistent_key_12345"))

    def test_load_yaml_valid(self):
        """Test loading valid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("test: value\nlist:\n  - item1\n  - item2\n")
            temp_file = f.name

        try:
            data = UserConfig.load_yaml(temp_file)
            self.assertIsNotNone(data)
            self.assertEqual(data["test"], "value")
            self.assertEqual(len(data["list"]), 2)
        finally:
            os.unlink(temp_file)

    def test_load_yaml_nonexistent(self):
        """Test loading non-existent file without must_exist."""
        data = UserConfig.load_yaml("/nonexistent/file.yml", must_exist=False)
        self.assertIsNone(data)

    def test_load_yaml_nonexistent_must_exist(self):
        """Test loading non-existent file with must_exist raises error."""
        with self.assertRaises(RuntimeError) as context:
            UserConfig.load_yaml("/nonexistent/file.yml", must_exist=True)
        self.assertIn("NOT FOUND", str(context.exception))


if __name__ == "__main__":
    unittest.main()
