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
import os
import subprocess
import time
import traceback
from typing import Any, Dict, List, Optional

from urwid import RIGHT, AttrWrap, Columns, ListBox, Pile, SimpleListWalker, Text, raw_display

from ucm.constants import MAIN_PALETTE
from ucm.Dialogs import DialogDisplay
from ucm.Registry import Registry
from ucm.UserConfig import UserConfig
from ucm.Widgets import ListView


def docker_connect(data: Dict[str, Any], shell: str = "bash") -> None:
    """Connect to a Docker container with an interactive shell.

    Args:
        data: Container data dictionary with 'name' key
        shell: Shell to use (default: 'bash', fallback: 'sh')
    """
    if not data or "name" not in data:
        logging.error(f"Invalid container data: {data}")
        return

    docker_cmd = UserConfig().docker
    if not docker_cmd:
        logging.error("Docker command not found")
        return

    main_loop = Registry().get("main_loop")
    if main_loop:
        try:
            main_loop.screen.stop()
            print(chr(27) + "[2J")
            cmd = f"{docker_cmd} exec -it {data['name']} {shell}"
            print(f"Executing: {cmd}")
            logging.info(f"Docker exec: {cmd}")
            rc = os.system(cmd)
            if rc == 32256:  # Shell not found, try 'sh'
                cmd = f"{docker_cmd} exec -it {data['name']} sh"
                logging.info(f"Retrying with sh: {cmd}")
                rc = os.system(cmd)
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


def docker_inspect(data: Dict[str, Any]) -> List[Text]:
    """Inspect a Docker container and return formatted output.

    Args:
        data: Container data dictionary with 'name' key

    Returns:
        List of Text widgets containing inspection output
    """
    docker_cmd = UserConfig().docker
    if not docker_cmd:
        return [Text("Error: Docker command not found")]

    if not data or "name" not in data:
        return [Text(f"Error: Invalid container data: {data}")]

    try:
        proc = subprocess.Popen([docker_cmd, "inspect", data["name"]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = proc.communicate()
        return [Text(x.rstrip()) for x in output.splitlines()]
    except Exception as e:
        logging.error(f"Docker inspect error: {e}")
        return [Text(f"Error inspecting container: {e}")]


class DockerListView(ListView):
    def __init__(self) -> None:
        super().__init__("Docker", filter_fields=["containerId", "name", "image"])

    def formatter(self, record: Dict[str, Any]) -> str:
        return f"{str(record['index']).rjust(4)} {record['containerId'].ljust(15)} {record['name'].ljust(20)} {record['image']}"

    def fetch_data(self) -> List[Dict[str, Any]]:
        """Fetch list of running Docker containers.

        Returns:
            List of container dictionaries with containerId, name, and image fields
        """
        data = []
        docker_cmd = UserConfig().docker
        if not docker_cmd:
            logging.error("Docker command not available")
            return data

        try:
            proc = subprocess.Popen(
                [docker_cmd, "ps", "--format", "table {{.ID}}\t{{.Names}}\t{{.Image}}"],
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
            logging.error(f"Docker command not found: {docker_cmd}")
        except Exception as e:
            logging.error(f"Error fetching Docker containers: {e}\n{traceback.format_exc()}")

        return data

    @staticmethod
    def popup_info_dialog(data: Dict[str, Any]) -> None:
        cols, rows = raw_display.Screen().get_cols_rows()
        d = DialogDisplay(
            f"Container Inspection: {data['name']}",
            cols - 20,
            rows - 6,
            body=Pile([ListBox(SimpleListWalker(docker_inspect(data)))]),
            loop=Registry().main_loop,
            exit_cb=DockerListView.close_cb,
            palette=MAIN_PALETTE,
        )
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def close_cb(button: Any) -> None:
        pass

    def double_click_callback(self) -> None:
        logging.debug(f"{self.name}] {self.selected.item_data['name']} double_click_callback")
        docker_connect(self.selected.item_data)

    def keypress_callback(self, size, key, data: Optional[Dict[str, Any]] = None) -> None:
        logging.debug(f"ListViewHandler[{self.name}] {size} {key} pressed")
        if key == "c":
            docker_connect(data, shell="bash")
        if key == "i":
            DockerListView.popup_info_dialog(data)
        super().keypress_callback(size, key, data)

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
