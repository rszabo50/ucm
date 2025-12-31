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

"""Add/Edit SSH Connection dialog for UCM."""

import logging
import os
from typing import Any, Dict, Optional, Tuple

import yaml
from urwid import AttrWrap, Divider, Edit, Filler, ListBox, Pile, SimpleListWalker, Text

from ucm.Dialogs import DialogDisplay
from ucm.UserConfig import UserConfig
from ucm.validators import SshConnectionValidator


class ConnectionDialog:
    """Dialog for adding or editing SSH connections."""

    def __init__(
        self,
        loop: Any,
        palette: list,
        ssh_list_view: Any,
        mode: str = "add",
        connection_data: Optional[Dict[str, Any]] = None,
    ):
        """Initialize connection dialog.

        Args:
            loop: Main urwid loop
            palette: Color palette
            ssh_list_view: Reference to SshListView for callbacks
            mode: Dialog mode - "add" or "edit"
            connection_data: Existing connection data (required for edit mode)
        """
        self.loop = loop
        self.palette = palette
        self.ssh_list_view = ssh_list_view
        self.mode = mode
        self.original_connection = connection_data if mode == "edit" else None

        # Validate: edit mode requires connection_data
        if mode == "edit" and not connection_data:
            raise ValueError("connection_data required for edit mode")

        # Edit field widgets
        self.name_edit: Edit = None
        self.address_edit: Edit = None
        self.user_edit: Edit = None
        self.port_edit: Edit = None
        self.identity_edit: Edit = None
        self.options_edit: Edit = None
        self.category_edit: Edit = None

        # Create dialog widgets
        self.body_widgets = self._create_body_widgets()

    def _create_body_widgets(self) -> Pile:
        """Create the body widgets for the dialog.

        Returns:
            Pile widget containing all form fields
        """
        widgets = []

        # Dynamic header based on mode
        if self.mode == "add":
            widgets.append(Text(("bold", "Add New SSH Connection"), align="center"))
        else:
            widgets.append(Text(("bold", "Edit SSH Connection"), align="center"))
        widgets.append(Divider())
        widgets.append(Text("Fields marked with * are required", align="center"))
        widgets.append(Text(""))

        # Name field (REQUIRED)
        widgets.append(Text(("bold", "Name: *")))
        widgets.append(Text("  Hostname or identifier for this connection"))
        self.name_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.name_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Address field (REQUIRED)
        widgets.append(Text(("bold", "Address: *")))
        widgets.append(Text("  IP address or DNS resolvable hostname"))
        self.address_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.address_edit, "button normal", "button select"))
        widgets.append(Text(""))

        widgets.append(Divider("─"))
        widgets.append(Text(("bold", "Optional Fields")))
        widgets.append(Text(""))

        # User field
        widgets.append(Text("User:"))
        widgets.append(Text("  Username to connect with"))
        self.user_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.user_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Port field
        widgets.append(Text("Port:"))
        widgets.append(Text("  TCP port (default: 22, range: 1-65535)"))
        self.port_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.port_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Identity field
        widgets.append(Text("Identity:"))
        widgets.append(Text("  Path to SSH key file (e.g., ~/.ssh/id_rsa)"))
        self.identity_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.identity_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Options field
        widgets.append(Text("Options:"))
        widgets.append(Text("  Additional SSH command options"))
        self.options_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.options_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Category field
        widgets.append(Text("Category:"))
        widgets.append(Text("  Category identifier for filtering"))
        self.category_edit = Edit("  ", edit_text="")
        widgets.append(AttrWrap(self.category_edit, "button normal", "button select"))
        widgets.append(Text(""))

        # Pre-populate fields if in edit mode
        if self.mode == "edit" and self.original_connection:
            self.name_edit.set_edit_text(self.original_connection.get("name", ""))
            self.address_edit.set_edit_text(self.original_connection.get("address", ""))
            self.user_edit.set_edit_text(self.original_connection.get("user", ""))
            # Convert port to string for Edit widget
            port_value = self.original_connection.get("port", "")
            self.port_edit.set_edit_text(str(port_value) if port_value else "")
            self.identity_edit.set_edit_text(self.original_connection.get("identity", ""))
            self.options_edit.set_edit_text(self.original_connection.get("options", ""))
            self.category_edit.set_edit_text(self.original_connection.get("category", ""))

        return Pile(widgets)

    def _collect_form_data(self) -> Dict[str, Any]:
        """Collect data from form fields.

        Returns:
            Dictionary with connection data
        """
        connection = {
            "name": self.name_edit.get_edit_text().strip(),
            "address": self.address_edit.get_edit_text().strip(),
        }

        # Add optional fields only if they have values
        user = self.user_edit.get_edit_text().strip()
        if user:
            connection["user"] = user

        port = self.port_edit.get_edit_text().strip()
        if port:
            # Store as integer for validation
            try:
                connection["port"] = int(port)
            except ValueError:
                connection["port"] = port  # Let validator catch this

        identity = self.identity_edit.get_edit_text().strip()
        if identity:
            connection["identity"] = identity

        options = self.options_edit.get_edit_text().strip()
        if options:
            connection["options"] = options

        category = self.category_edit.get_edit_text().strip()
        if category:
            connection["category"] = category

        return connection

    def _validate_connection(self, connection: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate connection data.

        Args:
            connection: Connection dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        return SshConnectionValidator.validate_connection(connection, 0)

    def _save_or_update_connection_to_yaml(self, connection: Dict[str, Any]) -> bool:
        """Save (add mode) or update (edit mode) connection in ssh_connections.yml.

        Args:
            connection: Connection dictionary to save

        Returns:
            True if save succeeded, False otherwise
        """
        ssh_config_file = UserConfig().get("ssh_config_file")

        # Load existing connections
        existing_connections = []
        try:
            if os.path.exists(ssh_config_file):
                with open(ssh_config_file) as f:
                    existing_connections = yaml.safe_load(f) or []
        except Exception as e:
            logging.error(f"Failed to load existing connections: {e}")
            self._show_error_dialog(f"Failed to load existing connections:\n{str(e)}")
            return False

        if self.mode == "add":
            # Append new connection
            existing_connections.append(connection)
            logging.info(f"Adding new connection: {connection['name']}")
        else:
            # Edit mode: Find and replace
            # Identify by original name+address
            original_name = self.original_connection.get("name")
            original_address = self.original_connection.get("address")

            found = False
            for i, conn in enumerate(existing_connections):
                if conn.get("name") == original_name and conn.get("address") == original_address:
                    # Replace this connection
                    existing_connections[i] = connection
                    found = True
                    logging.info(f"Updated connection at index {i}: {original_name} -> {connection['name']}")
                    break

            if not found:
                logging.error(f"Original connection not found: {original_name}@{original_address}")
                self._show_error_dialog(
                    f"Could not find original connection:\n{original_name} ({original_address})\n\n"
                    "It may have been deleted or modified outside UCM."
                )
                return False

        # Write back to file
        try:
            with open(ssh_config_file, "w") as f:
                yaml.safe_dump(existing_connections, f, default_flow_style=False, sort_keys=False, indent=2, width=1000)
            logging.info(f"Successfully saved connection: {connection['name']}")
            return True
        except Exception as e:
            logging.error(f"Failed to write ssh_connections.yml: {e}")
            self._show_error_dialog(f"Failed to save connection:\n{str(e)}")
            return False

    def _reload_list(self, connection: Dict[str, Any]):
        """Reload connections list after save.

        Args:
            connection: The connection that was saved/updated
        """
        try:
            # Reload SSH config
            UserConfig().load_ssh_config()

            # Refresh the list view
            self.ssh_list_view.filter_and_set("")

            if self.mode == "add":
                # Add mode: Find and select the new connection, then connect
                for i, list_item in enumerate(self.ssh_list_view.walker):
                    item_data = list_item.item_data
                    if (
                        item_data.get("name") == connection["name"]
                        and item_data.get("address") == connection["address"]
                    ):
                        # Found it - set focus
                        self.ssh_list_view.walker.set_focus(i)
                        logging.info(f"Selected new connection: {connection['name']}")
                        # Auto-connect
                        self.ssh_list_view.connect(item_data)
                        break
            else:
                # Edit mode: Just reload, no select or connect
                logging.info(f"List reloaded after editing: {connection['name']}")

        except Exception as e:
            logging.error(f"Failed to reload list: {e}")
            self._show_error_dialog(f"Connection saved but failed to reload:\n{str(e)}")

    def _show_error_dialog(self, error_message: str):
        """Show error dialog with message.

        Args:
            error_message: Error message to display
        """
        from ucm.Registry import Registry

        body = Filler(Text(error_message, align="center"))
        d = DialogDisplay(
            "Error", 70, 12, body=body, loop=Registry().main_loop, exit_cb=lambda btn: None, palette=self.palette
        )
        d.add_buttons([("OK", 0)])
        d.show()

    def _dialog_exit_cb(self, button: Any) -> None:
        """Handle dialog exit.

        Args:
            button: Button that was pressed
        """
        if button.exitcode == 0:  # Save button
            action = "Add" if self.mode == "add" else "Edit"
            logging.info(f"{action} Connection dialog: Save clicked")

            # Collect form data
            connection = self._collect_form_data()

            # Validate
            is_valid, error_msg = self._validate_connection(connection)
            if not is_valid:
                logging.warning(f"Validation failed: {error_msg}")
                self._show_error_dialog(f"Validation Error:\n\n{error_msg}")
                # Keep dialog open by showing it again
                self.show()
                return

            # Save to YAML
            if self._save_or_update_connection_to_yaml(connection):
                # Reload list (and auto-connect if add mode)
                self._reload_list(connection)
        else:  # Cancel button
            action = "Add" if self.mode == "add" else "Edit"
            logging.info(f"{action} Connection dialog: Cancel clicked")

        # Force screen redraw to prevent display artifacts
        if self.loop is not None:
            self.loop.screen.clear()
            self.loop.draw_screen()

    def show(self) -> None:
        """Show the connection dialog."""
        # Create scrollable list box with form fields
        listbox = ListBox(SimpleListWalker([self.body_widgets]))

        # Dynamic title based on mode
        title = "+ Add SSH Connection" if self.mode == "add" else "✎ Edit SSH Connection"

        # Create dialog
        dialog = DialogDisplay(
            title,
            85,
            30,
            body=listbox,
            loop=self.loop,
            exit_cb=self._dialog_exit_cb,
            palette=self.palette,
        )

        dialog.add_buttons([("Save", 0), ("Cancel", 1)])
        dialog.show()


# Backward compatibility alias
AddConnectionDialog = ConnectionDialog


# vim: ts=4 sw=4 et
