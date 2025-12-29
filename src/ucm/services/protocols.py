#!/usr/bin/env python3

"""Protocol definitions for UCM services."""

from typing import Any, Dict, List, Protocol


class SSHServiceProtocol(Protocol):
    """Protocol for SSH service operations."""

    def build_ssh_command(self, connection: Dict[str, Any]) -> str:
        """Build SSH command from connection data.

        Args:
            connection: Connection dictionary with connection parameters

        Returns:
            Formatted SSH command string
        """
        ...

    def connect(self, connection: Dict[str, Any]) -> int:
        """Execute SSH connection to remote host.

        Args:
            connection: Connection dictionary containing connection parameters

        Returns:
            Exit code from SSH command
        """
        ...


class DockerServiceProtocol(Protocol):
    """Protocol for Docker service operations."""

    def list_containers(self) -> List[Dict[str, Any]]:
        """Fetch list of running Docker containers.

        Returns:
            List of container dictionaries
        """
        ...

    def connect(self, container: Dict[str, Any], shell: str = "bash") -> int:
        """Connect to a Docker container with an interactive shell.

        Args:
            container: Container data dictionary
            shell: Shell to use (default: 'bash')

        Returns:
            Exit code from docker exec command
        """
        ...

    def inspect(self, container: Dict[str, Any]) -> str:
        """Inspect a Docker container.

        Args:
            container: Container data dictionary

        Returns:
            JSON output from docker inspect
        """
        ...
