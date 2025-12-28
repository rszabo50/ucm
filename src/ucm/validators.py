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

"""Configuration validators for UCM."""

import logging
from typing import Any, Dict, List, Optional, Tuple


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""

    pass


class SshConnectionValidator:
    """Validator for SSH connection configuration."""

    REQUIRED_FIELDS = {"name", "address"}
    OPTIONAL_FIELDS = {"user", "port", "identity", "options", "category"}
    VALID_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

    @classmethod
    def validate_connection(cls, conn: Dict[str, Any], index: int = 0) -> Tuple[bool, Optional[str]]:
        """Validate a single SSH connection configuration.

        Args:
            conn: Connection dictionary to validate
            index: Index of connection in list (for error messages)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(conn, dict):
            return False, f"Connection #{index + 1} is not a dictionary: {type(conn).__name__}"

        # Check required fields
        missing_fields = cls.REQUIRED_FIELDS - set(conn.keys())
        if missing_fields:
            return False, (
                f"Connection #{index + 1} ('{conn.get('name', 'unnamed')}'): "
                f"Missing required field(s): {', '.join(sorted(missing_fields))}"
            )

        # Validate 'name' field
        if not conn["name"]:
            return False, f"Connection #{index + 1}: 'name' field cannot be empty"

        if not isinstance(conn["name"], str):
            return False, (f"Connection #{index + 1}: 'name' must be a string, got {type(conn['name']).__name__}")

        # Validate 'address' field
        if not conn["address"]:
            return False, (f"Connection #{index + 1} ('{conn['name']}'): 'address' field cannot be empty")

        if not isinstance(conn["address"], str):
            return False, (
                f"Connection #{index + 1} ('{conn['name']}'): "
                f"'address' must be a string, got {type(conn['address']).__name__}"
            )

        # Check for unknown fields (warning only)
        unknown_fields = set(conn.keys()) - cls.VALID_FIELDS
        if unknown_fields:
            logging.warning(
                f"Connection #{index + 1} ('{conn['name']}'): "
                f"Unknown field(s) will be ignored: {', '.join(sorted(unknown_fields))}"
            )

        # Validate port if present
        if "port" in conn:
            port = conn["port"]
            # Port can be string or int
            if isinstance(port, int):
                if not 1 <= port <= 65535:
                    return False, (
                        f"Connection #{index + 1} ('{conn['name']}'): 'port' must be between 1 and 65535, got {port}"
                    )
            elif isinstance(port, str):
                try:
                    port_int = int(port)
                    if not 1 <= port_int <= 65535:
                        return False, (
                            f"Connection #{index + 1} ('{conn['name']}'): "
                            f"'port' must be between 1 and 65535, got {port}"
                        )
                except ValueError:
                    return False, (f"Connection #{index + 1} ('{conn['name']}'): 'port' must be a number, got '{port}'")
            else:
                return False, (
                    f"Connection #{index + 1} ('{conn['name']}'): "
                    f"'port' must be a number or string, got {type(port).__name__}"
                )

        return True, None

    @classmethod
    def validate_connections(cls, connections: Any) -> List[Dict[str, Any]]:
        """Validate SSH connections configuration.

        Args:
            connections: SSH connections data (should be a list of dicts)

        Returns:
            Validated list of connection dictionaries

        Raises:
            ConfigValidationError: If validation fails
        """
        if connections is None:
            raise ConfigValidationError(
                "SSH connections configuration is empty. "
                "Please add at least one connection to ~/.ucm/ssh_connections.yml"
            )

        if not isinstance(connections, list):
            raise ConfigValidationError(
                f"SSH connections must be a list, got {type(connections).__name__}. "
                f"Check your ~/.ucm/ssh_connections.yml format."
            )

        if len(connections) == 0:
            raise ConfigValidationError(
                "SSH connections list is empty. Please add at least one connection to ~/.ucm/ssh_connections.yml"
            )

        errors = []
        for i, conn in enumerate(connections):
            is_valid, error_msg = cls.validate_connection(conn, i)
            if not is_valid:
                errors.append(error_msg)

        if errors:
            error_summary = "\n".join(f"  - {err}" for err in errors)
            raise ConfigValidationError(
                f"SSH connection configuration has {len(errors)} error(s):\n{error_summary}\n\n"
                f"Please fix your ~/.ucm/ssh_connections.yml file."
            )

        logging.info(f"Validated {len(connections)} SSH connection(s)")
        return connections


# vim: ts=4 sw=4 et
