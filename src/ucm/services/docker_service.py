#!/usr/bin/env python3

"""Docker service for container operations."""

import logging
import os
import subprocess
import traceback
from typing import Any, Dict, List, Tuple


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

    def list_all_containers(self) -> List[Dict[str, Any]]:
        """Fetch list of all Docker containers (including stopped).

        Returns:
            List of container dictionaries with containerId, name, image, and status fields
        """
        data = []
        if not self.docker_cmd:
            logging.error("Docker command not available")
            return data

        try:
            proc = subprocess.Popen(
                [self.docker_cmd, "ps", "-a", "--format", "{{.ID}}|||{{.Names}}|||{{.Image}}|||{{.Status}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = proc.communicate()

            if proc.returncode != 0:
                logging.error(f"Docker ps -a failed: {stderr.decode('utf-8')}")
                return data

            for line in stdout.decode("UTF-8").splitlines():
                if not line.strip():
                    continue
                parts = line.split("|||")
                if len(parts) >= 4:
                    data.append(
                        {
                            "containerId": parts[0].strip(),
                            "name": parts[1].strip(),
                            "image": parts[2].strip(),
                            "status": parts[3].strip(),
                        }
                    )
        except FileNotFoundError:
            logging.error(f"Docker command not found: {self.docker_cmd}")
        except Exception as e:
            logging.error(f"Error fetching Docker containers: {e}\n{traceback.format_exc()}")

        return data

    def logs(self, container: Dict[str, Any], lines: int = 100, follow: bool = False) -> subprocess.Popen:
        """Get container logs.

        Args:
            container: Container data dictionary
            lines: Number of lines to tail (default: 100)
            follow: If True, follow log output (stream)

        Returns:
            Popen process for streaming logs

        Raises:
            ValueError: If container data is invalid
            FileNotFoundError: If docker command not found
        """
        if not self.validate_container(container):
            raise ValueError(f"Invalid container data: {container}")

        if not self.docker_cmd:
            raise FileNotFoundError("Docker command not found")

        cmd = [self.docker_cmd, "logs"]
        if follow:
            cmd.append("-f")
        cmd.extend(["--tail", str(lines), container["name"]])

        logging.info(f"Docker logs command: {' '.join(cmd)}")
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def stop(self, container: Dict[str, Any], timeout: int = 10) -> Tuple[int, str]:
        """Stop a running container.

        Args:
            container: Container data
            timeout: Seconds to wait before killing (default: 10)

        Returns:
            Tuple of (exit_code, message)
        """
        if not self.validate_container(container):
            return (1, f"Invalid container data: {container}")

        if not self.docker_cmd:
            return (1, "Docker command not found")

        cmd = [self.docker_cmd, "stop", "-t", str(timeout), container["name"]]
        logging.info(f"Stopping container: {' '.join(cmd)}")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                msg = f"Successfully stopped container: {container['name']}"
                logging.info(msg)
                return (0, msg)
            else:
                error = proc.stderr.strip() or proc.stdout.strip()
                msg = f"Failed to stop container {container['name']}: {error}"
                logging.error(msg)
                return (proc.returncode, msg)
        except Exception as e:
            msg = f"Error stopping container {container['name']}: {e}"
            logging.error(msg)
            return (1, msg)

    def start(self, container: Dict[str, Any]) -> Tuple[int, str]:
        """Start a stopped container.

        Args:
            container: Container data

        Returns:
            Tuple of (exit_code, message)
        """
        if not self.validate_container(container):
            return (1, f"Invalid container data: {container}")

        if not self.docker_cmd:
            return (1, "Docker command not found")

        cmd = [self.docker_cmd, "start", container["name"]]
        logging.info(f"Starting container: {' '.join(cmd)}")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                msg = f"Successfully started container: {container['name']}"
                logging.info(msg)
                return (0, msg)
            else:
                error = proc.stderr.strip() or proc.stdout.strip()
                msg = f"Failed to start container {container['name']}: {error}"
                logging.error(msg)
                return (proc.returncode, msg)
        except Exception as e:
            msg = f"Error starting container {container['name']}: {e}"
            logging.error(msg)
            return (1, msg)

    def restart(self, container: Dict[str, Any], timeout: int = 10) -> Tuple[int, str]:
        """Restart a container.

        Args:
            container: Container data
            timeout: Seconds to wait before killing (default: 10)

        Returns:
            Tuple of (exit_code, message)
        """
        if not self.validate_container(container):
            return (1, f"Invalid container data: {container}")

        if not self.docker_cmd:
            return (1, "Docker command not found")

        cmd = [self.docker_cmd, "restart", "-t", str(timeout), container["name"]]
        logging.info(f"Restarting container: {' '.join(cmd)}")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                msg = f"Successfully restarted container: {container['name']}"
                logging.info(msg)
                return (0, msg)
            else:
                error = proc.stderr.strip() or proc.stdout.strip()
                msg = f"Failed to restart container {container['name']}: {error}"
                logging.error(msg)
                return (proc.returncode, msg)
        except Exception as e:
            msg = f"Error restarting container {container['name']}: {e}"
            logging.error(msg)
            return (1, msg)

    def remove(self, container: Dict[str, Any], force: bool = False) -> Tuple[int, str]:
        """Remove a container.

        Args:
            container: Container data
            force: If True, force removal even if running

        Returns:
            Tuple of (exit_code, message)
        """
        if not self.validate_container(container):
            return (1, f"Invalid container data: {container}")

        if not self.docker_cmd:
            return (1, "Docker command not found")

        cmd = [self.docker_cmd, "rm"]
        if force:
            cmd.append("-f")
        cmd.append(container["name"])

        logging.info(f"Removing container: {' '.join(cmd)}")

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                msg = f"Successfully removed container: {container['name']}"
                logging.info(msg)
                return (0, msg)
            else:
                error = proc.stderr.strip() or proc.stdout.strip()
                msg = f"Failed to remove container {container['name']}: {error}"
                logging.error(msg)
                return (proc.returncode, msg)
        except Exception as e:
            msg = f"Error removing container {container['name']}: {e}"
            logging.error(msg)
            return (1, msg)
