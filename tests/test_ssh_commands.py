#!/usr/bin/env python3

"""Unit tests for SSH command building."""

import unittest

from ucm.services import SSHService


class TestSshCommandBuilding(unittest.TestCase):
    """Test SSH command construction."""

    def setUp(self):
        """Set up test fixtures."""
        self.ssh_service = SSHService()

    def test_basic_ssh_command(self):
        """Test basic SSH command with only address."""
        data = {"address": "192.168.1.100"}
        cmd = self.ssh_service.build_ssh_command(data)
        self.assertEqual(cmd, "ssh    192.168.1.100")

    def test_ssh_command_with_user(self):
        """Test SSH command with user and address."""
        data = {"address": "192.168.1.100", "user": "admin"}
        cmd = self.ssh_service.build_ssh_command(data)
        self.assertEqual(cmd, "ssh    admin@192.168.1.100")

    def test_ssh_command_with_port(self):
        """Test SSH command with custom port."""
        data = {"address": "192.168.1.100", "user": "admin", "port": "2222"}
        cmd = self.ssh_service.build_ssh_command(data)
        self.assertEqual(cmd, "ssh  -p 2222  admin@192.168.1.100")

    def test_ssh_command_with_identity(self):
        """Test SSH command with identity file."""
        data = {"address": "192.168.1.100", "user": "admin", "identity": "~/.ssh/mykey.pem"}
        cmd = self.ssh_service.build_ssh_command(data)
        self.assertEqual(cmd, "ssh -i ~/.ssh/mykey.pem   admin@192.168.1.100")

    def test_ssh_command_with_options(self):
        """Test SSH command with additional options."""
        data = {"address": "192.168.1.100", "user": "admin", "options": "-X -o StrictHostKeyChecking=no"}
        cmd = self.ssh_service.build_ssh_command(data)
        self.assertEqual(cmd, "ssh   -X -o StrictHostKeyChecking=no admin@192.168.1.100")

    def test_ssh_command_full(self):
        """Test SSH command with all parameters."""
        data = {
            "address": "192.168.1.100",
            "user": "admin",
            "port": "2222",
            "identity": "~/.ssh/mykey.pem",
            "options": "-X",
        }
        cmd = self.ssh_service.build_ssh_command(data)
        self.assertEqual(cmd, "ssh -i ~/.ssh/mykey.pem -p 2222 -X admin@192.168.1.100")


if __name__ == "__main__":
    unittest.main()
