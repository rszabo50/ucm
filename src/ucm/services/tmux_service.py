#!/usr/bin/env python3

"""Tmux integration service for managing terminal sessions."""

import logging
import os
import subprocess
from typing import Any, Dict, List, Optional


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

    @staticmethod
    def get_current_window_index() -> Optional[int]:
        """Get the current tmux window index.

        Returns:
            Window index if inside tmux, None otherwise
        """
        if not TmuxService.is_inside_tmux():
            return None

        try:
            result = subprocess.run(
                ["tmux", "display-message", "-p", "#I"],
                capture_output=True,
                text=True,
                check=True,
            )
            return int(result.stdout.strip())
        except Exception as e:
            logging.error(f"Failed to get current window index: {e}")
            return None

    @staticmethod
    def setup_ucm_return_key(window_index: int, key: str = "u") -> int:
        """Set up a tmux keybinding to return to UCM's window.

        Args:
            window_index: The window index where UCM is running
            key: The key to bind (default: 'u' for Ctrl+b u)

        Returns:
            Exit code (0 = success)
        """
        if not TmuxService.is_inside_tmux():
            logging.error("Not inside tmux session, cannot set up keybinding")
            return 1

        try:
            # Get the UCM process PID to send SIGWINCH signal
            ucm_pid = os.getpid()

            # Bind key to select UCM's window and send SIGWINCH to force screen redraw
            # SIGWINCH tells urwid the terminal size changed, forcing a complete redraw
            result = subprocess.run(
                [
                    "tmux",
                    "bind-key",
                    key,
                    "run-shell",
                    f"tmux select-window -t {window_index} && kill -WINCH {ucm_pid}",
                ],
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                logging.info(f"Set up Ctrl+b {key} to return to UCM window {window_index}")
            else:
                logging.error(f"Failed to set up keybinding, return code: {result.returncode}")
            return result.returncode
        except Exception as e:
            logging.error(f"Failed to set up UCM return key: {e}")
            return 1

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

        logging.debug(f"Creating tmux window: {' '.join(tmux_cmd)}")

        try:
            result = subprocess.run(tmux_cmd, capture_output=True, check=False)
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

        logging.debug(f"Creating tmux pane: {' '.join(tmux_cmd)}")

        try:
            result = subprocess.run(tmux_cmd, capture_output=True, check=False)
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
            mode: "window" (recommended) or "pane" (not actively supported)
            auto_name: Whether to auto-name the window

        Returns:
            Exit code (0 = success)

        Note:
            Only "window" mode is actively supported. Pane mode is kept for
            potential future use but does not support Ctrl+b u return keybinding.
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
            mode: "window" (recommended) or "pane" (not actively supported)
            auto_name: Whether to auto-name the window

        Returns:
            Exit code (0 = success)

        Note:
            Only "window" mode is actively supported. Pane mode is kept for
            potential future use but does not support Ctrl+b u return keybinding.
        """
        window_name = f"🐳 {container_name}" if auto_name else None

        if mode == "pane":
            return self.create_pane(docker_command)
        else:
            return self.create_window(docker_command, name=window_name)

    @staticmethod
    def list_windows() -> List[Dict[str, Any]]:
        """List all tmux windows in the current session.

        Returns:
            List of dictionaries containing window information:
            - index: Window index (0, 1, 2, etc.)
            - name: Window name
            - active: True if currently active window
            - panes: Number of panes in the window
        """
        if not TmuxService.is_inside_tmux():
            logging.warning("Not inside tmux session, cannot list windows")
            return []

        try:
            # Get window list with format: index:name:active:panes
            # Active window has '*' flag, others have '-' or empty
            result = subprocess.run(
                ["tmux", "list-windows", "-F", "#{window_index}:#{window_name}:#{window_active}:#{window_panes}"],
                capture_output=True,
                text=True,
                check=True,
            )

            windows = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split(":")
                if len(parts) >= 4:
                    windows.append(
                        {
                            "index": int(parts[0]),
                            "name": parts[1],
                            "active": parts[2] == "1",
                            "panes": int(parts[3]),
                        }
                    )

            logging.debug(f"Found {len(windows)} tmux windows")
            return windows

        except Exception as e:
            logging.error(f"Failed to list tmux windows: {e}")
            return []

    @staticmethod
    def switch_window(window_index: int) -> int:
        """Switch to a specific tmux window.

        Args:
            window_index: Index of the window to switch to

        Returns:
            Exit code (0 = success)
        """
        if not TmuxService.is_inside_tmux():
            logging.error("Not inside tmux session, cannot switch window")
            return 1

        try:
            result = subprocess.run(
                ["tmux", "select-window", "-t", str(window_index)],
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                logging.debug(f"Switched to tmux window {window_index}")
            return result.returncode

        except Exception as e:
            logging.error(f"Failed to switch tmux window: {e}")
            return 1

    @staticmethod
    def kill_window(window_index: int) -> int:
        """Close/kill a specific tmux window.

        Args:
            window_index: Index of the window to close

        Returns:
            Exit code (0 = success)
        """
        if not TmuxService.is_inside_tmux():
            logging.error("Not inside tmux session, cannot kill window")
            return 1

        try:
            result = subprocess.run(
                ["tmux", "kill-window", "-t", str(window_index)],
                capture_output=True,
                check=False,
            )
            if result.returncode == 0:
                logging.debug(f"Killed tmux window {window_index}")
            return result.returncode

        except Exception as e:
            logging.error(f"Failed to kill tmux window: {e}")
            return 1


# vim: ts=4 sw=4 et
