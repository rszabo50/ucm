#!/usr/bin/env python3

"""Tmux integration service for managing terminal sessions."""

import logging
import os
import subprocess
from typing import Optional


class TmuxService:
    """Service for tmux terminal integration."""

    @staticmethod
    def is_tmux_available() -> bool:
        """Check if tmux is installed and available.

        Returns:
            True if tmux is available, False otherwise
        """
        try:
            result = subprocess.run(
                ["which", "tmux"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except Exception as e:
            logging.debug(f"Tmux availability check failed: {e}")
            return False

    @staticmethod
    def is_inside_tmux() -> bool:
        """Check if currently running inside a tmux session.

        Returns:
            True if inside tmux, False otherwise
        """
        return "TMUX" in os.environ

    @staticmethod
    def get_current_session() -> Optional[str]:
        """Get the current tmux session name.

        Returns:
            Session name if inside tmux, None otherwise
        """
        if not TmuxService.is_inside_tmux():
            return None

        try:
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#S"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception as e:
            logging.error(f"Failed to get tmux session: {e}")
            return None

    def create_window(self, command: str, name: Optional[str] = None) -> int:
        """Create a new tmux window and execute command.

        Args:
            command: Command to execute in the new window
            name: Optional window name

        Returns:
            Exit code (0 = success)
        """
        if not self.is_inside_tmux():
            logging.error("Not inside a tmux session")
            return 1

        tmux_cmd = ["tmux", "new-window"]

        if name:
            tmux_cmd.extend(["-n", name])

        tmux_cmd.append(command)

        logging.info(f"Creating tmux window: {' '.join(tmux_cmd)}")

        try:
            result = subprocess.run(tmux_cmd, check=False)
            return result.returncode
        except Exception as e:
            logging.error(f"Failed to create tmux window: {e}")
            return 1

    def create_pane(self, command: str) -> int:
        """Split current tmux window and execute command in new pane.

        Args:
            command: Command to execute in the new pane

        Returns:
            Exit code (0 = success)
        """
        if not self.is_inside_tmux():
            logging.error("Not inside a tmux session")
            return 1

        tmux_cmd = ["tmux", "split-window", command]

        logging.info(f"Creating tmux pane: {' '.join(tmux_cmd)}")

        try:
            result = subprocess.run(tmux_cmd, check=False)
            return result.returncode
        except Exception as e:
            logging.error(f"Failed to create tmux pane: {e}")
            return 1

    def launch_ssh_connection(
        self,
        ssh_command: str,
        connection_name: str,
        mode: str = "window",
        auto_name: bool = True,
    ) -> int:
        """Launch SSH connection in tmux window or pane.

        Args:
            ssh_command: Full SSH command to execute
            connection_name: Name of the connection (for window naming)
            mode: "window" or "pane"
            auto_name: Whether to auto-name the window

        Returns:
            Exit code (0 = success)
        """
        window_name = f"🐧 {connection_name}" if auto_name else None

        if mode == "pane":
            return self.create_pane(ssh_command)
        else:
            return self.create_window(ssh_command, name=window_name)

    def launch_docker_connection(
        self,
        docker_command: str,
        container_name: str,
        mode: str = "window",
        auto_name: bool = True,
    ) -> int:
        """Launch Docker connection in tmux window or pane.

        Args:
            docker_command: Full docker exec command to execute
            container_name: Name of the container (for window naming)
            mode: "window" or "pane"
            auto_name: Whether to auto-name the window

        Returns:
            Exit code (0 = success)
        """
        window_name = f"🐳 {container_name}" if auto_name else None

        if mode == "pane":
            return self.create_pane(docker_command)
        else:
            return self.create_window(docker_command, name=window_name)


# vim: ts=4 sw=4 et
