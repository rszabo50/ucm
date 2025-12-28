#!/usr/bin/env python3

"""Unit tests for configuration validators."""

import unittest

from ucm.validators import ConfigValidationError, SshConnectionValidator


class TestSshConnectionValidator(unittest.TestCase):
    """Test SSH connection validation."""

    def test_valid_minimal_connection(self):
        """Test valid connection with only required fields."""
        conn = {"name": "server1", "address": "192.168.1.100"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_valid_full_connection(self):
        """Test valid connection with all fields."""
        conn = {
            "name": "server1",
            "address": "192.168.1.100",
            "user": "admin",
            "port": 22,
            "identity": "~/.ssh/id_rsa",
            "options": "-X",
            "category": "production",
        }
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_missing_name(self):
        """Test that missing name field is rejected."""
        conn = {"address": "192.168.1.100"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("name", error)
        self.assertIn("required", error.lower())

    def test_missing_address(self):
        """Test that missing address field is rejected."""
        conn = {"name": "server1"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("address", error)
        self.assertIn("required", error.lower())

    def test_empty_name(self):
        """Test that empty name is rejected."""
        conn = {"name": "", "address": "192.168.1.100"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("name", error)
        self.assertIn("empty", error.lower())

    def test_empty_address(self):
        """Test that empty address is rejected."""
        conn = {"name": "server1", "address": ""}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("address", error)
        self.assertIn("empty", error.lower())

    def test_invalid_port_too_low(self):
        """Test that port < 1 is rejected."""
        conn = {"name": "server1", "address": "192.168.1.100", "port": 0}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("port", error)

    def test_invalid_port_too_high(self):
        """Test that port > 65535 is rejected."""
        conn = {"name": "server1", "address": "192.168.1.100", "port": 70000}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("port", error)

    def test_valid_port_string(self):
        """Test that port as string is accepted."""
        conn = {"name": "server1", "address": "192.168.1.100", "port": "2222"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_invalid_port_string(self):
        """Test that non-numeric port string is rejected."""
        conn = {"name": "server1", "address": "192.168.1.100", "port": "abc"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("port", error)
        self.assertIn("number", error.lower())

    def test_not_dict(self):
        """Test that non-dict connection is rejected."""
        conn = "not a dict"
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("dictionary", error.lower())

    def test_validate_connections_valid_list(self):
        """Test validating a valid list of connections."""
        connections = [
            {"name": "server1", "address": "192.168.1.100"},
            {"name": "server2", "address": "192.168.1.101", "user": "admin"},
        ]
        result = SshConnectionValidator.validate_connections(connections)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, connections)

    def test_validate_connections_none(self):
        """Test that None connections raises error."""
        with self.assertRaises(ConfigValidationError) as context:
            SshConnectionValidator.validate_connections(None)
        self.assertIn("empty", str(context.exception).lower())

    def test_validate_connections_not_list(self):
        """Test that non-list connections raises error."""
        with self.assertRaises(ConfigValidationError) as context:
            SshConnectionValidator.validate_connections({"name": "server1"})
        self.assertIn("list", str(context.exception).lower())

    def test_validate_connections_empty_list(self):
        """Test that empty list raises error."""
        with self.assertRaises(ConfigValidationError) as context:
            SshConnectionValidator.validate_connections([])
        self.assertIn("empty", str(context.exception).lower())

    def test_validate_connections_multiple_errors(self):
        """Test that multiple validation errors are reported."""
        connections = [
            {"address": "192.168.1.100"},  # Missing name
            {"name": "server2"},  # Missing address
            {"name": "", "address": "192.168.1.102"},  # Empty name
        ]
        with self.assertRaises(ConfigValidationError) as context:
            SshConnectionValidator.validate_connections(connections)
        error_msg = str(context.exception)
        # Should mention multiple errors
        self.assertIn("3", error_msg)
        # Should mention the specific issues
        self.assertIn("name", error_msg.lower())
        self.assertIn("address", error_msg.lower())

    def test_validate_connection_index_in_error(self):
        """Test that connection index appears in error messages."""
        conn = {"address": "192.168.1.100"}
        is_valid, error = SshConnectionValidator.validate_connection(conn, index=5)
        self.assertFalse(is_valid)
        self.assertIn("#6", error)  # index 5 = connection #6

    def test_name_type_validation(self):
        """Test that name must be a string."""
        conn = {"name": 123, "address": "192.168.1.100"}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("string", error.lower())

    def test_address_type_validation(self):
        """Test that address must be a string."""
        conn = {"name": "server1", "address": 192168}
        is_valid, error = SshConnectionValidator.validate_connection(conn)
        self.assertFalse(is_valid)
        self.assertIn("string", error.lower())


if __name__ == "__main__":
    unittest.main()
