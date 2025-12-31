#!/usr/bin/env python3

#
#  Copyright (C) 2022 Robert Szabo.
#
#  This software can be used by anyone at no cost, however,
#  if you like using my software and can support - please
#  donate money to a children's hospital of your choice.
#  This program is free software: you can redistribute it
#  and/or modify it under the terms of the GNU General Public
#  License as published by the Free Software Foundation:
#  GNU GPLv3. You must include this entire text with your
#  distribution.
#  This program is distributed in the hope that it will be
#  useful, but WITHOUT ANY WARRANTY; without even the implied
#  warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#  PURPOSE.
#  See the GNU General Public License for more details.
#

# Created by rszabo50 at 2022-02-01

import logging
import time
from typing import Any, Dict, List, Optional

from urwid import (
    RIGHT,
    AttrWrap,
    Button,
    Columns,
    Divider,
    Edit,
    Filler,
    ListBox,
    Pile,
    SimpleListWalker,
    Text,
    raw_display,
)

from ucm.constants import MAIN_PALETTE
from ucm.Dialogs import DialogDisplay
from ucm.Registry import Registry
from ucm.services import DockerService, DockerServiceProtocol, TmuxService
from ucm.services.iterm2_service import ITerm2Service
from ucm.settings_manager import get_settings_manager
from ucm.UserConfig import UserConfig
from ucm.Widgets import ListView


class DockerListView(ListView):
    def __init__(self, docker_service: Optional[DockerServiceProtocol] = None) -> None:
        docker_cmd = UserConfig().docker
        self.docker_service = (
            docker_service if docker_service is not None else DockerService(docker_cmd if docker_cmd else "docker")
        )
        self.tmux_service = TmuxService()
        self.iterm2_service = ITerm2Service()
        self.settings_manager = get_settings_manager()
        self.show_all_containers = False  # Toggle state (resets each session)
        super().__init__("Docker", filter_fields=["containerId", "name", "image", "status"])

    def formatter(self, record: Dict[str, Any]) -> str:
        # Show status indicator when showing all containers
        if self.show_all_containers and "status" in record:
            status_indicator = "●" if "Up" in record["status"] else "○"
            return f"{status_indicator} {str(record['index']).rjust(4)} {record['containerId'].ljust(15)} {record['name'].ljust(20)} {record['image']}"
        else:
            return f"  {str(record['index']).rjust(4)} {record['containerId'].ljust(15)} {record['name'].ljust(20)} {record['image']}"

    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch Docker containers based on show_all toggle.

        Returns:
            List of container dictionaries with containerId, name, image, and status fields (if showing all)
        """
        if self.show_all_containers:
            return self.docker_service.list_all_containers()
        else:
            return self.docker_service.list_containers()

    def popup_info_dialog(self, data: Dict[str, Any]) -> None:
        """Show container inspection dialog.

        Args:
            data: Container data dictionary
        """
        cols, rows = raw_display.Screen().get_cols_rows()
        inspect_output = self.docker_service.inspect(data)
        lines = [Text(line.rstrip()) for line in inspect_output.splitlines()]

        d = DialogDisplay(
            f"Container Inspection: {data['name']}",
            cols - 20,
            rows - 6,
            body=Pile([ListBox(SimpleListWalker(lines))]),
            loop=Registry().main_loop,
            exit_cb=self.close_cb,
            palette=MAIN_PALETTE,
        )
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def close_cb(button: Any) -> None:
        pass

    def double_click_callback(self) -> None:
        logging.debug(f"{self.name}] {self.selected.item_data['name']} double_click_callback")
        self._connect_to_container(self.selected.item_data)

    def keypress_callback(self, size, key, data: Optional[Dict[str, Any]] = None):
        logging.debug(f"ListViewHandler[{self.name}] {size} {key} pressed")
        if key == "c":
            self._connect_to_container(data, shell="bash")
            return None
        elif key == "|":
            # iTerm2 vertical split pane
            self._connect_to_container(data, shell="bash", split_pane="vertical")
            return None
        elif key == "-":
            # iTerm2 horizontal split pane
            self._connect_to_container(data, shell="bash", split_pane="horizontal")
            return None
        elif key == "i":
            self.popup_info_dialog(data)
            return None
        elif key == "a":
            # Toggle show all containers
            self.show_all_containers = not self.show_all_containers
            mode = "all" if self.show_all_containers else "running only"
            logging.info(f"Show containers: {mode}")
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")
            return None
        elif key == "S":
            # Stop container
            if data:
                self._stop_container(data)
            return None
        elif key == "s":
            # Start container
            if data:
                self._start_container(data)
            return None
        elif key == "R":
            # Restart container
            if data:
                self._restart_container(data)
            return None
        elif key == "D":
            # Remove container (with confirmation)
            if data:
                self._confirm_remove_container(data)
            return None
        elif key == "l":
            # Show logs
            if data:
                self._show_logs_dialog(data)
            return None
        # Return result from parent to allow unhandled keys to bubble up
        return super().keypress_callback(size, key, data)

    def _connect_to_container(
        self, data: Dict[str, Any], shell: str = "bash", split_pane: Optional[str] = None
    ) -> None:
        """Connect to a Docker container.

        Args:
            data: Container data dictionary
            shell: Shell to use (default: 'bash')
            split_pane: For iTerm2: None for new tab, "vertical" or "horizontal" for split pane
        """
        # Check if terminal integration is enabled
        terminal_integration = self.settings_manager.get_terminal_integration()

        if terminal_integration == "tmux" and self.tmux_service.is_inside_tmux():
            # Use tmux integration - keep UCM running
            tmux_settings = self.settings_manager.get_tmux_settings()
            mode = tmux_settings.get("mode", "window")
            auto_name = tmux_settings.get("auto_name", True)

            # Build docker exec command
            container_id = data.get("containerId", data.get("name", "unknown"))
            docker_cmd = self.docker_service.docker_cmd
            docker_command = f"{docker_cmd} exec -it {container_id} {shell}"
            container_name = data.get("name", container_id)

            logging.debug(f"Launching Docker connection in tmux {mode}: {container_name}")
            rc = self.tmux_service.launch_docker_connection(
                docker_command=docker_command,
                container_name=container_name,
                mode=mode,
                auto_name=auto_name,
            )

            if rc != 0:
                logging.error(f"Failed to launch tmux {mode} for {container_name}")
        elif terminal_integration == "iterm2" and self.iterm2_service.is_iterm2_available():
            # Use iTerm2 integration - keep UCM running
            iterm2_settings = self.settings_manager.get_iterm2_settings()
            profile = iterm2_settings.get("profile", "Default")

            # Build docker exec command
            container_id = data.get("containerId", data.get("name", "unknown"))
            docker_cmd = self.docker_service.docker_cmd
            docker_command = f"{docker_cmd} exec -it {container_id} {shell}"
            container_name = data.get("name", container_id)

            mode_desc = "split pane" if split_pane else "tab"
            logging.debug(f"Launching Docker connection in iTerm2 {mode_desc}: {container_name}")
            rc = self.iterm2_service.launch_docker_connection(
                docker_command=docker_command,
                container_name=container_name,
                profile=profile,
                split_pane=split_pane,
            )

            if rc != 0:
                logging.error(f"Failed to launch iTerm2 {mode_desc} for {container_name}")
        else:
            # Traditional mode - stop UCM, connect, then restart
            main_loop = Registry().get("main_loop")
            if main_loop:
                try:
                    main_loop.screen.stop()
                    print(chr(27) + "[2J")
                    rc = self.docker_service.connect(data, shell)
                    if rc != 0:
                        print(f"Container connection failed with return code: {rc}")
                        time.sleep(5)
                except Exception as e:
                    logging.error(f"Docker connection error: {e}")
                    print(f"Error: {e}")
                    time.sleep(3)
                finally:
                    main_loop.screen.start(alternate_buffer=True)
                    main_loop.screen.clear()
                    main_loop.draw_screen()

    def _show_message_dialog(self, title: str, message: str, is_error: bool = False) -> None:
        """Show a message dialog.

        Args:
            title: Dialog title
            message: Message text
            is_error: If True, highlight as error
        """
        # Use "error" or "bold" style based on is_error
        style = "error" if is_error else "bold"
        body = Filler(Text((style, message), align="center"))

        d = DialogDisplay(
            title, 70, 12, body=body, loop=Registry().main_loop, exit_cb=lambda btn: None, palette=MAIN_PALETTE
        )
        d.add_buttons([("OK", 0)])
        d.show()

    def _stop_container(self, data: Dict[str, Any]) -> None:
        """Stop a container.

        Args:
            data: Container data
        """
        logging.info(f"Stopping container: {data.get('name')}")
        rc, msg = self.docker_service.stop(data)
        self._show_message_dialog("Stop Container", msg, is_error=(rc != 0))
        if rc == 0:
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")

    def _start_container(self, data: Dict[str, Any]) -> None:
        """Start a container.

        Args:
            data: Container data
        """
        logging.info(f"Starting container: {data.get('name')}")
        rc, msg = self.docker_service.start(data)
        self._show_message_dialog("Start Container", msg, is_error=(rc != 0))
        if rc == 0:
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")

    def _restart_container(self, data: Dict[str, Any]) -> None:
        """Restart a container.

        Args:
            data: Container data
        """
        logging.info(f"Restarting container: {data.get('name')}")
        rc, msg = self.docker_service.restart(data)
        self._show_message_dialog("Restart Container", msg, is_error=(rc != 0))
        if rc == 0:
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")

    def _confirm_remove_container(self, data: Dict[str, Any]) -> None:
        """Show confirmation dialog before removing container.

        Args:
            data: Container data
        """
        container_name = data.get("name", "unknown")
        message = (
            f"Are you sure you want to remove container '{container_name}'?\n\n"
            "This action cannot be undone.\n\n"
            "Note: Container must be stopped before removal."
        )
        body = Filler(Text(message, align="center"))

        def confirm_callback(button):
            if button.exitcode == 0:  # Remove button
                self._remove_container(data)

        d = DialogDisplay(
            "Confirm Remove Container",
            70,
            14,
            body=body,
            loop=Registry().main_loop,
            exit_cb=confirm_callback,
            palette=MAIN_PALETTE,
        )
        d.add_buttons([("Remove", 0), ("Cancel", 1)])
        d.show()

    def _remove_container(self, data: Dict[str, Any]) -> None:
        """Remove a container (called after confirmation).

        Args:
            data: Container data
        """
        logging.info(f"Removing container: {data.get('name')}")
        rc, msg = self.docker_service.remove(data)
        self._show_message_dialog("Remove Container", msg, is_error=(rc != 0))
        if rc == 0:
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")

    def _show_logs_dialog(self, data: Dict[str, Any]) -> None:
        """Show container logs in a dialog with pause/unpause and line count control.

        Args:
            data: Container data
        """
        container_name = data.get("name", "unknown")
        cols, rows = raw_display.Screen().get_cols_rows()

        # State variables
        log_state = {
            "paused": False,
            "log_lines": 100,
            "log_process": None,
            "alarm_handle": None,
            "log_walker": SimpleListWalker([]),
        }

        # Line count edit field with numeric-only validation
        class NumericEdit(Edit):
            def keypress(self, size, key):
                if key in (
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "backspace",
                    "delete",
                    "left",
                    "right",
                    "home",
                    "end",
                ):
                    return super().keypress(size, key)
                return key  # Ignore non-numeric keys

        line_count_edit = NumericEdit(edit_text="100")

        # Pause button placeholder - will be created with callback
        pause_button = None

        # Log display
        log_listbox = ListBox(log_state["log_walker"])

        def update_line_count(button):
            """Update line count and restart stream."""
            try:
                new_count = int(line_count_edit.get_edit_text().strip())
                if new_count < 1:
                    new_count = 1
                log_state["log_lines"] = new_count
                logging.info(f"Updated log line count to {new_count}")
                start_log_stream()
            except ValueError:
                logging.error(f"Invalid line count: {line_count_edit.get_edit_text()}")

        def toggle_pause(button):
            """Toggle pause/unpause."""
            log_state["paused"] = not log_state["paused"]
            button.set_label("Resume" if log_state["paused"] else "Pause")
            logging.info(f"Logs {'paused' if log_state['paused'] else 'resumed'}")

            if log_state["paused"]:
                # Cancel the pending alarm when pausing
                if log_state["alarm_handle"]:
                    try:
                        Registry().main_loop.remove_alarm(log_state["alarm_handle"])
                        log_state["alarm_handle"] = None
                        logging.info("Alarm canceled - logs paused")
                    except Exception as e:
                        logging.error(f"Failed to cancel alarm: {e}")
            else:
                # Resume polling
                logging.info("Resuming log polling")
                poll_logs()

        def start_log_stream():
            """Start streaming logs."""
            # Kill existing process
            if log_state["log_process"]:
                try:
                    log_state["log_process"].terminate()
                    log_state["log_process"].wait(timeout=1)
                except Exception:
                    pass

            # Cancel existing alarm
            if log_state["alarm_handle"]:
                try:
                    Registry().main_loop.remove_alarm(log_state["alarm_handle"])
                except Exception:
                    pass

            # Clear log display
            log_state["log_walker"][:] = []

            # Start new process
            try:
                log_state["log_process"] = self.docker_service.logs(data, lines=log_state["log_lines"], follow=True)
                logging.info(f"Started log stream for {container_name} with {log_state['log_lines']} lines")
                poll_logs()
            except Exception as e:
                logging.error(f"Failed to start log stream: {e}")
                log_state["log_walker"].append(Text(f"Error: Failed to start log stream: {e}"))

        def poll_logs(loop=None, user_data=None):
            """Poll logs and update display."""
            if log_state["paused"]:
                # Don't schedule next poll when paused
                return

            if not log_state["log_process"]:
                return

            try:
                # Read available lines (non-blocking)
                import select

                # Check if data is available
                if log_state["log_process"].poll() is None:  # Process still running
                    ready, _, _ = select.select([log_state["log_process"].stdout], [], [], 0)
                    if ready:
                        line = log_state["log_process"].stdout.readline()
                        if line:
                            log_state["log_walker"].append(Text(line.rstrip()))
                            # Auto-scroll to bottom
                            try:
                                log_listbox.set_focus(len(log_state["log_walker"]) - 1)
                            except Exception:
                                pass
            except Exception as e:
                logging.debug(f"Poll logs error (non-critical): {e}")

            # Schedule next poll only if not paused
            if not log_state["paused"]:
                log_state["alarm_handle"] = Registry().main_loop.set_alarm_in(0.5, poll_logs)

        def exit_callback(button):
            """Cleanup when dialog closes."""
            # Cancel alarm
            if log_state["alarm_handle"]:
                try:
                    Registry().main_loop.remove_alarm(log_state["alarm_handle"])
                except Exception:
                    pass

            # Terminate log process
            if log_state["log_process"]:
                try:
                    log_state["log_process"].terminate()
                    log_state["log_process"].wait(timeout=1)
                except Exception:
                    pass

        # Create buttons with callbacks
        pause_button = Button("Pause", on_press=toggle_pause)
        apply_button = Button("Apply", on_press=update_line_count)

        # Build dialog body - use flow widgets for controls
        body = Pile(
            [
                (
                    "flow",
                    Columns(
                        [
                            (20, Text("Lines to show:")),
                            (10, AttrWrap(line_count_edit, "button normal", "button select")),
                            (2, Text("")),
                            (15, AttrWrap(apply_button, "button normal", "button select")),
                            (2, Text("")),
                            (15, AttrWrap(pause_button, "button normal", "button select")),
                        ]
                    ),
                ),
                ("flow", Divider()),
                ("weight", 1, log_listbox),
            ]
        )

        d = DialogDisplay(
            f"Container Logs: {container_name}",
            cols - 10,
            rows - 4,
            body=body,
            loop=Registry().main_loop,
            exit_cb=exit_callback,
            palette=MAIN_PALETTE,
        )
        d.add_buttons([("Close", 0)])

        # Start streaming
        start_log_stream()

        d.show()

    def get_filter_widgets(self) -> Columns:
        """Get filter widgets with show-all indicator."""
        if self.show_all_containers:
            return Columns(
                [
                    super().get_filter_widgets(),
                    (10, AttrWrap(Text("[ALL]", align=RIGHT), "header", "header")),
                ]
            )
        else:
            return super().get_filter_widgets()

    def get_header(self) -> str:
        if self.show_all_containers:
            return f"  {'#'.rjust(4)} {'ContainerId'.ljust(15)} {'Name'.ljust(20)} Image"
        else:
            return f"  {'#'.rjust(4)} {'ContainerId'.ljust(15)} {'Name'.ljust(20)} Image"


# vim: ts=4 sw=4 et
