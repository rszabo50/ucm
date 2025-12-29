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

"""Settings dialog for UCM."""

import logging
from typing import Any, List

from urwid import (
    AttrWrap,
    CheckBox,
    Divider,
    Edit,
    ListBox,
    Pile,
    RadioButton,
    SimpleListWalker,
    Text,
)

from ucm.Dialogs import DialogDisplay
from ucm.settings_manager import get_settings_manager


class SettingsDialog:
    """Settings dialog for configuring UCM options."""

    def __init__(self, loop: Any, palette: list):
        """Initialize settings dialog.

        Args:
            loop: Main urwid loop
            palette: Color palette
        """
        self.loop = loop
        self.palette = palette
        self.settings_manager = get_settings_manager()

        # Radio button groups
        self.integration_group: List[RadioButton] = []

        # Checkboxes
        self.tmux_auto_name_cb: CheckBox = None

        # Edit fields
        self.iterm2_profile_edit: Edit = None

        # Create dialog widgets
        self.body_widgets = self._create_body_widgets()

    def _create_body_widgets(self) -> Pile:
        """Create the body widgets for the settings dialog.

        Returns:
            Pile widget containing all settings
        """
        widgets = []

        # Header
        widgets.append(Text(("bold", "Terminal Integration Settings"), align="center"))
        widgets.append(Divider())
        widgets.append(Text(""))

        # Terminal Integration Mode
        widgets.append(Text(("bold", "Terminal Integration:")))
        widgets.append(Text("  Choose how UCM should integrate with your terminal:"))
        widgets.append(Text(""))

        # Get current integration mode
        current_mode = self.settings_manager.get_terminal_integration()

        # Radio buttons for integration mode
        none_rb = RadioButton(
            self.integration_group, "  None - Exit UCM after connection", state=(current_mode == "none")
        )
        tmux_rb = RadioButton(
            self.integration_group, "  Tmux - Keep UCM open, use tmux windows/panes", state=(current_mode == "tmux")
        )
        iterm2_rb = RadioButton(
            self.integration_group, "  iTerm2 - Keep UCM open, use iTerm2 tabs", state=(current_mode == "iterm2")
        )

        widgets.append(AttrWrap(none_rb, "button normal", "button select"))
        widgets.append(AttrWrap(tmux_rb, "button normal", "button select"))
        widgets.append(AttrWrap(iterm2_rb, "button normal", "button select"))
        widgets.append(Text(""))

        # Tmux Settings
        widgets.append(Divider("─"))
        widgets.append(Text(("bold", "Tmux Settings:")))
        widgets.append(Text("  (Only used when Tmux integration is enabled)"))
        widgets.append(Text(""))

        # Get current tmux settings
        tmux_settings = self.settings_manager.get_tmux_settings()
        auto_name = tmux_settings.get("auto_name", True)

        # Tmux mode is always "window" (pane mode not supported)
        widgets.append(Text("  Connection Mode: New Window (each connection in separate window)"))
        widgets.append(Text(""))

        # Tmux auto-name checkbox
        self.tmux_auto_name_cb = CheckBox("  Auto-name windows with connection info", state=auto_name)
        widgets.append(AttrWrap(self.tmux_auto_name_cb, "button normal", "button select"))
        widgets.append(Text(""))

        # iTerm2 Settings
        widgets.append(Divider("─"))
        widgets.append(Text(("bold", "iTerm2 Settings (macOS only):")))
        widgets.append(Text("  (Only used when iTerm2 integration is enabled)"))
        widgets.append(Text(""))

        # Get current iTerm2 settings
        iterm2_settings = self.settings_manager.get_iterm2_settings()
        profile = iterm2_settings.get("profile", "Default")

        # Connections always open in new tabs (only supported mode)
        widgets.append(Text("  Connection Mode: New Tab (each connection in separate tab)"))
        widgets.append(Text(""))

        # iTerm2 profile edit
        widgets.append(Text("  iTerm2 Profile:"))
        self.iterm2_profile_edit = Edit("    ", edit_text=profile)
        widgets.append(AttrWrap(self.iterm2_profile_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Help text
        widgets.append(Divider("─"))
        widgets.append(Text(""))
        widgets.append(Text("  Note: Terminal integration features are optional and can be", align="center"))
        widgets.append(Text("  configured here. Changes take effect immediately.", align="center"))
        widgets.append(Text(""))

        return Pile(widgets)

    def _save_settings(self) -> None:
        """Save current dialog settings to settings manager."""
        # Determine which integration mode is selected
        integration_mode = "none"
        for rb in self.integration_group:
            if rb.get_state():
                label = rb.get_label()
                if "None" in label:
                    integration_mode = "none"
                elif "Tmux" in label:
                    integration_mode = "tmux"
                elif "iTerm2" in label:
                    integration_mode = "iterm2"
                break

        self.settings_manager.set_terminal_integration(integration_mode)

        # Save tmux settings (mode is always "window")
        self.settings_manager.set("terminal.tmux.mode", "window")
        self.settings_manager.set("terminal.tmux.auto_name", self.tmux_auto_name_cb.get_state())

        # Save iTerm2 settings
        self.settings_manager.set("terminal.iterm2.profile", self.iterm2_profile_edit.get_edit_text())

        logging.info(f"Settings saved: terminal integration = {integration_mode}")

    def show(self) -> None:
        """Show the settings dialog."""
        # Create scrollable list box with settings
        listbox = ListBox(SimpleListWalker([self.body_widgets]))

        # Create dialog
        dialog = DialogDisplay(
            "⚙️  Settings",
            100,  # width
            30,  # height
            body=listbox,
            loop=self.loop,
            exit_cb=self._dialog_exit_cb,
            palette=self.palette,
        )

        dialog.add_buttons([("Save", 0), ("Cancel", 1)])
        dialog.show()

    def _dialog_exit_cb(self, button: Any) -> None:
        """Handle dialog exit.

        Args:
            button: Button that was pressed
        """
        if button.exitcode == 0:  # Save button
            self._save_settings()
            logging.info("Settings dialog: Save clicked")
        else:  # Cancel button
            logging.info("Settings dialog: Cancel clicked")

        # Force screen redraw to prevent display artifacts
        if self.loop is not None:
            self.loop.screen.clear()


# vim: ts=4 sw=4 et
