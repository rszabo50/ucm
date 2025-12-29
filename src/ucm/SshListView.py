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
import time
from typing import Any, Dict, List, Optional

from urwid import RIGHT, AttrWrap, Columns, ListBox, Pile, SimpleListWalker, Text

from ucm.connection_manager import get_connection_manager
from ucm.constants import MAIN_PALETTE
from ucm.Dialogs import DialogDisplay
from ucm.Registry import Registry
from ucm.UserConfig import UserConfig
from ucm.Widgets import ListView


class SshListView(ListView):
    def __init__(self) -> None:
        self.conn_manager = get_connection_manager()
        super().__init__("SSH", filter_fields=["category", "name", "user", "address"])

    def formatter(self, record: Dict[str, Any]) -> str:
        if "category" not in record:
            record["category"] = "---"

        # Check if this is a favorite
        is_fav = self.conn_manager.is_favorite(record)
        fav_marker = "★" if is_fav else " "

        display_host = record["name"] if len(record["name"]) <= 58 else f"...{record['name'][-55:]}"
        display_category = record["category"] if len(record["category"]) <= 20 else f"...{record['category'][-20:]}"
        connection = record["address"] if "user" not in record else f"{record['user']}@{record['address']}"

        return f"{fav_marker} {str(record['index']).rjust(4)}   {display_category.ljust(20)}   {display_host.ljust(58)}   {connection}"

    @staticmethod
    def fetch_data() -> Optional[List[Dict[str, Any]]]:
        return UserConfig().get("ssh_connections")

    def double_click_callback(self) -> None:
        logging.debug(f"{self.name}] {self.selected.item_data['name']} double_click_callback")
        self.connect(self.selected.item_data)

    def keypress_callback(self, size, key, data: Optional[Dict[str, Any]] = None) -> None:
        logging.debug(f"ListViewHandler[{self.name}] {size} {key} pressed")
        if key == "c":
            self.connect(data)
        elif key == "i":
            SshListView.popup_info_dialog(data)
        elif key == "f":
            # Toggle favorite status
            if data:
                is_fav = self.conn_manager.toggle_favorite(data)
                status = "added to" if is_fav else "removed from"
                logging.info(f"{data.get('name', 'Connection')} {status} favorites")
                # Refresh the list to update the star indicator
                self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")
        super().keypress_callback(size, key, data)

    @staticmethod
    def popup_info_dialog(data: Dict[str, Any]) -> None:
        d = DialogDisplay(
            f"{data['name']}",
            90,
            len(data.keys()) + 9,
            body=Pile([ListBox(SimpleListWalker([Text(f"{k.ljust(25)} : {v}") for k, v in data.items()]))]),
            loop=Registry().main_loop,
            exit_cb=SshListView.close_cb,
            palette=MAIN_PALETTE,
        )
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def close_cb(button: Any) -> None:
        pass

    def get_filter_widgets(self) -> Columns:
        return Columns(
            [
                super().get_filter_widgets(),
                Columns(
                    [
                        AttrWrap(
                            Text("| 'c' = connect, 'i' = info, 'f' = toggle favorite ★", align=RIGHT),
                            "header",
                            "header",
                        )
                    ]
                ),
            ]
        )

    @staticmethod
    def build_ssh_command(data: Dict[str, Any]) -> str:
        """Build SSH command from connection data.

        Args:
            data: Connection dictionary with keys: address, user, port, identity, options

        Returns:
            Formatted SSH command string
        """
        user_at_host = data["address"] if "user" not in data else f"{data['user']}@{data['address']}"
        ident = f"-i {data['identity']}" if "identity" in data else ""
        port = f"-p {data['port']}" if "port" in data else ""
        opts = f"{data['options']}" if "options" in data else ""
        return f"ssh {ident} {port} {opts} {user_at_host}"

    def connect(self, data: Dict[str, Any]) -> None:
        """Execute SSH connection to remote host.

        Args:
            data: Connection dictionary containing connection parameters
        """
        if not data:
            logging.error("No connection data provided")
            return

        if "address" not in data:
            logging.error(f"Missing 'address' field in connection data: {data}")
            return

        # Record this connection in history
        self.conn_manager.record_connection(data)

        main_loop = Registry().get("main_loop")
        if main_loop:
            try:
                main_loop.screen.stop()
                print(chr(27) + "[2J")
                cmd = self.build_ssh_command(data)
                print(f"Executing: {cmd}")
                logging.info(f"SSH command: {cmd}")
                rc = os.system(cmd)
                if rc != 0:
                    print(f"Connection failed with return code: {rc}")
                    time.sleep(2)
            except Exception as e:
                logging.error(f"SSH connection error: {e}")
                print(f"Error: {e}")
                time.sleep(3)
            finally:
                main_loop.screen.start(alternate_buffer=True)
                main_loop.screen.clear()

    def get_header(self) -> str:
        return f"  {'#'.rjust(4)}   {'Category'.ljust(20)}   {'Hostname'.ljust(58)}   Connection"


# vim: ts=4 sw=4 et
