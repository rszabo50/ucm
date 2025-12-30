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

from urwid import RIGHT, AttrWrap, Columns, ListBox, Pile, SimpleListWalker, Text, raw_display

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
        super().__init__("Docker", filter_fields=["containerId", "name", "image"])

    def formatter(self, record: Dict[str, Any]) -> str:
        return f"{str(record['index']).rjust(4)} {record['containerId'].ljust(15)} {record['name'].ljust(20)} {record['image']}"

    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch list of running Docker containers.

        Returns:
            List of container dictionaries with containerId, name, and image fields
        """
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

    def keypress_callback(self, size, key, data: Optional[Dict[str, Any]] = None) -> None:
        logging.debug(f"ListViewHandler[{self.name}] {size} {key} pressed")
        if key == "c":
            self._connect_to_container(data, shell="bash")
        if key == "i":
            self.popup_info_dialog(data)
        super().keypress_callback(size, key, data)

    def _connect_to_container(self, data: Dict[str, Any], shell: str = "bash") -> None:
        """Connect to a Docker container.

        Args:
            data: Container data dictionary
            shell: Shell to use (default: 'bash')
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

            logging.debug(f"Launching Docker connection in iTerm2 tab: {container_name}")
            rc = self.iterm2_service.launch_docker_connection(
                docker_command=docker_command,
                container_name=container_name,
                profile=profile,
            )

            if rc != 0:
                logging.error(f"Failed to launch iTerm2 tab for {container_name}")
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

    def get_filter_widgets(self) -> Columns:
        return Columns(
            [
                super().get_filter_widgets(),
                Columns([AttrWrap(Text("| On highlighted row: 'c' = connect", align=RIGHT), "header", "header")]),
            ]
        )

    def get_header(self) -> str:
        return f"{'#'.rjust(4)} {'ContainerId'.ljust(15)} {'Name'.ljust(20)} Image"


# vim: ts=4 sw=4 et
