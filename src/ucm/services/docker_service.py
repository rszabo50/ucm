#!/usr/bin/env python3

"""Docker service for container operations."""

import logging
import os
import subprocess
import traceback
from typing import Any, Dict, List


class DockerService:
    """Service for Docker container operations."""

    def __init__(self, docker_cmd: str = "docker"):
        """Initialize Docker service.

        Args:
            docker_cmd: Docker command to use (default: 'docker')
        """
        self.docker_cmd = docker_cmd

    def list_containers(self) -> List[Dict[str, Any]]:
        """Fetch list of running Docker containers.

        Returns:
            List of container dictionaries with containerId, name, and image fields
        """
        data = []
        if not self.docker_cmd:
            logging.error("Docker command not available")
            return data

        try:
            proc = subprocess.Popen(
                [self.docker_cmd, "ps", "--format", "table {{.ID}}\t{{.Names}}\t{{.Image}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                logging.error(f"Docker ps failed: {stderr.decode('utf-8')}")
                return data

            for line in stdout.decode("UTF-8").splitlines():
                parts = line.split()
                if parts and "CONTAINER" not in parts[0]:
                    if len(parts) >= 3:
                        data.append(
                            {"containerId": parts[0].strip(), "name": parts[1].strip(), "image": parts[2].strip()}
                        )
        except FileNotFoundError:
            logging.error(f"Docker command not found: {self.docker_cmd}")
        except Exception as e:
            logging.error(f"Error fetching Docker containers: {e}\n{traceback.format_exc()}")

        return data

    def connect(self, container: Dict[str, Any], shell: str = "bash") -> int:
        """Connect to a Docker container with an interactive shell.

        Args:
            container: Container data dictionary with 'name' key
            shell: Shell to use (default: 'bash', fallback: 'sh')

        Returns:
            Exit code from docker exec command (0 = success)
        """
        if not container or "name" not in container:
            logging.error(f"Invalid container data: {container}")
            return 1

        if not self.docker_cmd:
            logging.error("Docker command not found")
            return 1

        cmd = f"{self.docker_cmd} exec -it {container['name']} {shell}"
        print(f"Executing: {cmd}")
        logging.info(f"Docker exec: {cmd}")

        rc = os.system(cmd)
        if rc == 32256:  # Shell not found, try 'sh'
            cmd = f"{self.docker_cmd} exec -it {container['name']} sh"
            logging.info(f"Retrying with sh: {cmd}")
            rc = os.system(cmd)

        return rc

    def inspect(self, container: Dict[str, Any]) -> str:
        """Inspect a Docker container and return JSON output.

        Args:
            container: Container data dictionary with 'name' key

        Returns:
            JSON output from docker inspect command
        """
        if not self.docker_cmd:
            return '{"error": "Docker command not found"}'

        if not container or "name" not in container:
            return f'{{"error": "Invalid container data: {container}"}}'

        try:
            proc = subprocess.Popen(
                [self.docker_cmd, "inspect", container["name"]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, _ = proc.communicate()
            return output.decode("utf-8")
        except Exception as e:
            logging.error(f"Docker inspect error: {e}")
            return f'{{"error": "Error inspecting container: {e}"}}'

    def validate_container(self, container: Dict[str, Any]) -> bool:
        """Validate container data.

        Args:
            container: Container dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not container:
            return False
        if "name" not in container:
            return False
        return True
