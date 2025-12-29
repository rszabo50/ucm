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

# Created for tmux window navigation

import logging
from typing import Any, Dict, List, Optional

from urwid import RIGHT, AttrWrap, Columns, Text

from ucm.services import TmuxService
from ucm.Widgets import ListView


class TmuxListView(ListView):
    """ListView for managing tmux windows."""

    def __init__(self) -> None:
        self.tmux_service = TmuxService()
        self.ucm_window_index = None

        # Set up Ctrl+b u keybinding to return to UCM
        if TmuxService.is_inside_tmux():
            self.ucm_window_index = TmuxService.get_current_window_index()
            if self.ucm_window_index is not None:
                TmuxService.setup_ucm_return_key(self.ucm_window_index, key="u")
                logging.info(f"UCM running in tmux window {self.ucm_window_index}. Press Ctrl+b u to return to UCM.")

        super().__init__("Tmux", filter_fields=["name", "index"])

    def formatter(self, record: Dict[str, Any]) -> str:
        """Format tmux window record for display.

        Args:
            record: Window dictionary

        Returns:
            Formatted string for display
        """
        active_marker = "▶" if record.get("active", False) else " "
        index = str(record.get("index", "?")).rjust(3)
        name = record.get("name", "unknown")
        panes = record.get("panes", 1)
        panes_str = f"({panes} panes)" if panes > 1 else "(1 pane)"

        # Truncate long window names
        if len(name) > 60:
            name = f"{name[:57]}..."

        return f"{active_marker} {index}   {name.ljust(60)}   {panes_str}"

    @staticmethod
    def fetch_data() -> Optional[List[Dict[str, Any]]]:
        """Fetch list of tmux windows.

        Returns:
            List of window dictionaries
        """
        tmux_service = TmuxService()
        windows = tmux_service.list_windows()

        # Add index for the list view
        for idx, window in enumerate(windows):
            window["list_index"] = idx

        return windows if windows else None

    def double_click_callback(self) -> None:
        """Handle double-click on a window."""
        logging.debug(f"{self.name}] {self.selected.item_data.get('name', 'unknown')} double_click_callback")
        self.switch_to_window(self.selected.item_data)

    def keypress_callback(self, size, key, data: Optional[Dict[str, Any]] = None) -> None:
        """Handle keypresses for tmux window actions.

        Args:
            size: Widget size
            key: Key pressed
            data: Window data dictionary
        """
        logging.debug(f"ListViewHandler[{self.name}] {size} {key} pressed")

        if key == "c" or key == "enter":
            # Switch to window
            self.switch_to_window(data)
        elif key == "x":
            # Close/kill window
            self.close_window(data)
        elif key == "r":
            # Refresh window list
            self.filter_and_set("")

        super().keypress_callback(size, key, data)

    def switch_to_window(self, data: Dict[str, Any]) -> None:
        """Switch to the selected tmux window.

        Args:
            data: Window data dictionary
        """
        if not data:
            logging.error("No window data provided")
            return

        window_index = data.get("index")
        if window_index is None:
            logging.error("Window index not found in data")
            return

        logging.debug(f"Switching to tmux window {window_index}: {data.get('name', 'unknown')}")
        rc = self.tmux_service.switch_window(window_index)

        if rc != 0:
            logging.error(f"Failed to switch to window {window_index}")
        else:
            # Refresh the list to update the active marker
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")

    def close_window(self, data: Dict[str, Any]) -> None:
        """Close/kill the selected tmux window.

        Args:
            data: Window data dictionary
        """
        if not data:
            logging.error("No window data provided")
            return

        window_index = data.get("index")
        window_name = data.get("name", "unknown")

        if window_index is None:
            logging.error("Window index not found in data")
            return

        # Don't allow killing the current window (would kill UCM)
        if data.get("active", False):
            logging.warning(f"Cannot kill active window {window_index} ({window_name})")
            return

        logging.debug(f"Closing tmux window {window_index}: {window_name}")
        rc = self.tmux_service.kill_window(window_index)

        if rc != 0:
            logging.error(f"Failed to close window {window_index}")
        else:
            # Refresh the list after closing
            self.filter_and_set(self.filter_edit.edit_text if hasattr(self, "filter_edit") else "")

    def get_filter_widgets(self) -> Columns:
        """Get filter widgets with tmux-specific help text.

        Returns:
            Columns widget with filter and help text
        """
        # Build help text with UCM window info
        help_text = "| 'c/Enter'=switch 'x'=close 'r'=refresh"
        if self.ucm_window_index is not None:
            help_text += " | Ctrl+b u=return to UCM"

        return Columns(
            [
                super().get_filter_widgets(),
                Columns(
                    [
                        AttrWrap(
                            Text(help_text, align=RIGHT),
                            "header",
                            "header",
                        )
                    ]
                ),
            ]
        )


# vim: ts=4 sw=4 et
