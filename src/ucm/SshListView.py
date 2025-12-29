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

from urwid import RIGHT, AttrWrap, Columns, ListBox, Pile, SimpleListWalker, Text

from ucm.connection_manager import get_connection_manager
from ucm.constants import MAIN_PALETTE
from ucm.Dialogs import DialogDisplay
from ucm.Registry import Registry
from ucm.services import SSHService, SSHServiceProtocol, TmuxService
from ucm.services.iterm2_service import ITerm2Service
from ucm.settings_manager import get_settings_manager
from ucm.UserConfig import UserConfig
from ucm.Widgets import ListView


class SshListView(ListView):
    def __init__(self, ssh_service: Optional[SSHServiceProtocol] = None) -> None:
        self.conn_manager = get_connection_manager()
        self.ssh_service = ssh_service if ssh_service is not None else SSHService()
        self.tmux_service = TmuxService()
        self.iterm2_service = ITerm2Service()
        self.settings_manager = get_settings_manager()
        self.favorites_only = False  # Toggle to show only favorites
        self.sort_by_recent = False  # Toggle to sort by recently used
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

    def filter_data(self, filter_string: str) -> List[Dict[str, Any]]:
        """Filter and sort data based on current settings.

        Args:
            filter_string: Text filter to apply

        Returns:
            Filtered and sorted list of connections
        """
        # Get base data
        data = super().filter_data(filter_string)
        if not data:
            return []

        # Filter by favorites if enabled
        if self.favorites_only:
            data = [conn for conn in data if self.conn_manager.is_favorite(conn)]

        # Sort by recently used if enabled
        if self.sort_by_recent:
            # Get history to find use counts and last used times
            history = self.conn_manager.get_history(limit=1000)
            history_map = {
                self.conn_manager._connection_id(h): {
                    "last_used": h.get("last_used", ""),
                    "use_count": h.get("use_count", 0),
                }
                for h in history
            }

            # Sort connections by last_used (most recent first)
            def sort_key(conn):
                conn_id = self.conn_manager._connection_id(conn)
                if conn_id in history_map:
                    return (1, history_map[conn_id]["last_used"])  # 1 = has history
                return (0, "")  # 0 = no history, will be at the end

            data = sorted(data, key=sort_key, reverse=True)

        return data

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
        elif key == "F":
            # Toggle favorites-only filter
            self.favorites_only = not self.favorites_only
            mode = "ON" if self.favorites_only else "OFF"
            logging.info(f"Favorites-only filter: {mode}")
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")
        elif key == "r":
            # Toggle recently used sorting
            self.sort_by_recent = not self.sort_by_recent
            mode = "ON" if self.sort_by_recent else "OFF"
            logging.info(f"Recently used sorting: {mode}")
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")
        elif key == "L":
            # Quick connect to last used connection
            self._connect_to_last_used()
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
        # Build status indicators
        fav_indicator = " [FAV]" if self.favorites_only else ""
        recent_indicator = " [RECENT]" if self.sort_by_recent else ""
        status = f"{fav_indicator}{recent_indicator}"

        return Columns(
            [
                super().get_filter_widgets(),
                Columns(
                    [
                        AttrWrap(
                            Text(
                                f"| 'c'=connect 'i'=info 'f'=fav★ 'F'=filter favs 'r'=recent 'L'=last{status}",
                                align=RIGHT,
                            ),
                            "header",
                            "header",
                        )
                    ]
                ),
            ]
        )

    def connect(self, data: Dict[str, Any]) -> None:
        """Execute SSH connection to remote host.

        Args:
            data: Connection dictionary containing connection parameters
        """
        if not self.ssh_service.validate_connection(data):
            logging.error("Invalid connection data")
            return

        # Record this connection in history
        self.conn_manager.record_connection(data)

        # Check if terminal integration is enabled
        terminal_integration = self.settings_manager.get_terminal_integration()

        if terminal_integration == "tmux" and self.tmux_service.is_inside_tmux():
            # Use tmux integration - keep UCM running
            tmux_settings = self.settings_manager.get_tmux_settings()
            mode = tmux_settings.get("mode", "window")
            auto_name = tmux_settings.get("auto_name", True)

            ssh_command = self.ssh_service.build_ssh_command(data)
            connection_name = data.get("name", data.get("address", "unknown"))

            logging.debug(f"Launching SSH connection in tmux {mode}: {connection_name}")
            rc = self.tmux_service.launch_ssh_connection(
                ssh_command=ssh_command,
                connection_name=connection_name,
                mode=mode,
                auto_name=auto_name,
            )

            if rc != 0:
                logging.error(f"Failed to launch tmux {mode} for {connection_name}")
        elif terminal_integration == "iterm2" and self.iterm2_service.is_iterm2_available():
            # Use iTerm2 integration - keep UCM running
            iterm2_settings = self.settings_manager.get_iterm2_settings()
            new_tab = iterm2_settings.get("new_tab", True)
            profile = iterm2_settings.get("profile", "Default")

            ssh_command = self.ssh_service.build_ssh_command(data)
            connection_name = data.get("name", data.get("address", "unknown"))

            logging.debug(f"Launching SSH connection in iTerm2 tab: {connection_name}")
            rc = self.iterm2_service.launch_ssh_connection(
                ssh_command=ssh_command,
                connection_name=connection_name,
                new_tab=new_tab,
                profile=profile,
            )

            if rc != 0:
                logging.error(f"Failed to launch iTerm2 tab for {connection_name}")
        else:
            # Traditional mode - stop UCM, connect, then restart
            main_loop = Registry().get("main_loop")
            if main_loop:
                try:
                    main_loop.screen.stop()
                    print(chr(27) + "[2J")
                    rc = self.ssh_service.connect(data)
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

    def _connect_to_last_used(self) -> None:
        """Connect to the most recently used connection from history."""
        history = self.conn_manager.get_history(limit=1)
        if not history:
            logging.info("No connection history available")
            return

        last_conn = history[0]
        # Find matching connection in current config
        all_connections = self.fetch_data()
        if not all_connections:
            logging.error("No connections configured")
            return

        # Try to find the connection by name and address
        for conn in all_connections:
            if conn.get("name") == last_conn.get("name") and conn.get("address") == last_conn.get("address"):
                logging.info(f"Quick connecting to last used: {conn.get('name')}")
                self.connect(conn)
                return

        logging.warning(f"Last used connection '{last_conn.get('name')}' not found in current config")

    def get_header(self) -> str:
        return f"  {'#'.rjust(4)}   {'Category'.ljust(20)}   {'Hostname'.ljust(58)}   Connection"


# vim: ts=4 sw=4 et
