#!/usr/bin/env python3

"""iTerm2 integration service for managing terminal sessions."""

import logging
import platform
import subprocess
from typing import Optional


class ITerm2Service:
    """Service for iTerm2 terminal integration."""

    @staticmethod
    def is_iterm2_available() -> bool:
        """Check if iTerm2 is available.

        Returns:
            True if running on macOS and iTerm2 is installed, False otherwise
        """
        # Check if on macOS
        if platform.system() != "Darwin":
            logging.debug("Not on macOS, iTerm2 not available")
            return False

        # Check if iTerm2 application exists
        try:
            result = subprocess.run(
                ["osascript", "-e", 'exists application "iTerm"'],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip() == "true"
        except Exception as e:
            logging.debug(f"iTerm2 availability check failed: {e}")
            return False

    @staticmethod
    def is_inside_iterm2() -> bool:
        """Check if currently running inside iTerm2.

        Returns:
            True if inside iTerm2, False otherwise
        """
        try:
            result = subprocess.run(
                ["osascript", "-e", 'tell application "iTerm2" to get name'],
                capture_output=True,
                text=True,
                check=False,
            )
            # If we can successfully communicate with iTerm2, we're likely inside it
            return result.returncode == 0
        except Exception:
            return False

    def create_tab(
        self,
        command: str,
        name: Optional[str] = None,
        profile: str = "Default",
    ) -> int:
        """Create a new iTerm2 tab and execute command.

        Args:
            command: Command to execute in the new tab
            name: Optional tab name
            profile: iTerm2 profile to use (default: "Default")

        Returns:
            Exit code (0 = success)
        """
        if not self.is_iterm2_available():
            logging.error("iTerm2 is not available")
            return 1

        # Build AppleScript to create tab and run command
        # Note: iTerm2 AppleScript uses "write text" to send commands to sessions
        # Use exec so the shell closes when the command exits
        applescript = f"""
        tell application "iTerm2"
            tell current window
                create tab with profile "{profile}"
                tell current session of current tab
                    write text "exec {command}"
        """

        # Add tab naming if specified
        if name:
            # Escape double quotes in name
            escaped_name = name.replace('"', '\\"')
            applescript += f'                    set name to "{escaped_name}"\n'

        applescript += """
                end tell
            end tell
        end tell
        """

        logging.debug(f"Creating iTerm2 tab with profile '{profile}': {command}")

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                logging.error(f"Failed to create iTerm2 tab: {result.stderr.decode()}")
            return result.returncode
        except Exception as e:
            logging.error(f"Failed to create iTerm2 tab: {e}")
            return 1

    def create_split_pane(
        self,
        command: str,
        name: Optional[str] = None,
        profile: str = "Default",
        vertical: bool = True,
    ) -> int:
        """Create a split pane in current iTerm2 tab and execute command.

        Args:
            command: Command to execute in the new pane
            name: Optional pane name
            profile: iTerm2 profile to use (default: "Default")
            vertical: True for vertical split (side-by-side), False for horizontal

        Returns:
            Exit code (0 = success)
        """
        if not self.is_iterm2_available():
            logging.error("iTerm2 is not available")
            return 1

        # Build AppleScript to split pane and run command
        # Use exec so the pane closes when the command exits
        split_direction = "vertically" if vertical else "horizontally"
        applescript = f"""
        tell application "iTerm2"
            tell current window
                tell current session of current tab
                    set newSession to (split {split_direction} with profile "{profile}")
                    tell newSession
                        write text "exec {command}"
        """

        # Add pane naming if specified
        if name:
            # Escape double quotes in name
            escaped_name = name.replace('"', '\\"')
            applescript += f'                        set name to "{escaped_name}"\n'

        applescript += """
                    end tell
                end tell
            end tell
        end tell
        """

        logging.debug(f"Creating iTerm2 split pane ({split_direction}) with profile '{profile}': {command}")

        try:
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                logging.error(f"Failed to create iTerm2 split pane: {result.stderr.decode()}")
            return result.returncode
        except Exception as e:
            logging.error(f"Failed to create iTerm2 split pane: {e}")
            return 1

    def launch_ssh_connection(
        self,
        ssh_command: str,
        connection_name: str,
        profile: str = "Default",
        split_pane: Optional[str] = None,
    ) -> int:
        """Launch SSH connection in iTerm2 tab or split pane.

        Args:
            ssh_command: Full SSH command to execute
            connection_name: Name of the connection (for tab naming)
            profile: iTerm2 profile to use
            split_pane: None for new tab, "vertical" for vertical split, "horizontal" for horizontal split

        Returns:
            Exit code (0 = success)
        """
        pane_name = f"🐧 {connection_name}"

        if split_pane == "vertical":
            return self.create_split_pane(ssh_command, name=pane_name, profile=profile, vertical=True)
        elif split_pane == "horizontal":
            return self.create_split_pane(ssh_command, name=pane_name, profile=profile, vertical=False)
        else:
            return self.create_tab(ssh_command, name=pane_name, profile=profile)

    def launch_docker_connection(
        self,
        docker_command: str,
        container_name: str,
        profile: str = "Default",
        split_pane: Optional[str] = None,
    ) -> int:
        """Launch Docker connection in iTerm2 tab or split pane.

        Args:
            docker_command: Full docker exec command to execute
            container_name: Name of the container (for tab naming)
            profile: iTerm2 profile to use
            split_pane: None for new tab, "vertical" for vertical split, "horizontal" for horizontal split

        Returns:
            Exit code (0 = success)
        """
        pane_name = f"🐳 {container_name}"

        if split_pane == "vertical":
            return self.create_split_pane(docker_command, name=pane_name, profile=profile, vertical=True)
        elif split_pane == "horizontal":
            return self.create_split_pane(docker_command, name=pane_name, profile=profile, vertical=False)
        else:
            return self.create_tab(docker_command, name=pane_name, profile=profile)


# vim: ts=4 sw=4 et
