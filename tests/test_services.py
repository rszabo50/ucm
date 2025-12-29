#!/usr/bin/env python3

"""Tests for service layer."""

import unittest

from ucm.services import DockerService, SSHService


class TestSSHService(unittest.TestCase):
    """Test SSHService functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = SSHService()

    def test_validate_connection_valid(self):
        """Test validating a valid connection."""
        conn = {"name": "test", "address": "example.com"}
        self.assertTrue(self.service.validate_connection(conn))

    def test_validate_connection_missing_address(self):
        """Test validating connection without address."""
        conn = {"name": "test"}
        self.assertFalse(self.service.validate_connection(conn))

    def test_validate_connection_none(self):
        """Test validating None connection."""
        self.assertFalse(self.service.validate_connection(None))

    def test_validate_connection_empty_dict(self):
        """Test validating empty connection."""
        self.assertFalse(self.service.validate_connection({}))

    def test_build_ssh_command(self):
        """Test building SSH command."""
        conn = {"address": "example.com", "user": "testuser"}
        cmd = self.service.build_ssh_command(conn)
        self.assertIn("ssh", cmd)
        self.assertIn("testuser@example.com", cmd)


class TestDockerService(unittest.TestCase):
    """Test DockerService functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = DockerService("docker")

    def test_validate_container_valid(self):
        """Test validating a valid container."""
        container = {"name": "test_container"}
        self.assertTrue(self.service.validate_container(container))

    def test_validate_container_missing_name(self):
        """Test validating container without name."""
        container = {"id": "abc123"}
        self.assertFalse(self.service.validate_container(container))

    def test_validate_container_none(self):
        """Test validating None container."""
        self.assertFalse(self.service.validate_container(None))

    def test_validate_container_empty_dict(self):
        """Test validating empty container."""
        self.assertFalse(self.service.validate_container({}))


if __name__ == "__main__":
    unittest.main()
