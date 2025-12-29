#!/usr/bin/env python3

"""SSH service for connection operations."""

import logging
import os
from typing import Any, Dict


class SSHService:
    """Service for SSH connection operations."""

    def build_ssh_command(self, connection: Dict[str, Any]) -> str:
        """Build SSH command from connection data.

        Args:
            connection: Connection dictionary with keys: address, user, port, identity, options

        Returns:
            Formatted SSH command string
        """
        user_at_host = (
            connection["address"] if "user" not in connection else f"{connection['user']}@{connection['address']}"
        )
        ident = f"-i {connection['identity']}" if "identity" in connection else ""
        port = f"-p {connection['port']}" if "port" in connection else ""
        opts = f"{connection['options']}" if "options" in connection else ""
        return f"ssh {ident} {port} {opts} {user_at_host}"

    def connect(self, connection: Dict[str, Any]) -> int:
        """Execute SSH connection to remote host.

        Args:
            connection: Connection dictionary containing connection parameters

        Returns:
            Exit code from SSH command (0 = success)
        """
        if not connection:
            logging.error("No connection data provided")
            return 1

        if "address" not in connection:
            logging.error(f"Missing 'address' field in connection data: {connection}")
            return 1

        cmd = self.build_ssh_command(connection)
        print(f"Executing: {cmd}")
        logging.info(f"SSH command: {cmd}")

        return os.system(cmd)

    def validate_connection(self, connection: Dict[str, Any]) -> bool:
        """Validate connection data.

        Args:
            connection: Connection dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not connection:
            return False
        if "address" not in connection:
            return False
        return True
