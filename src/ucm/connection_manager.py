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

"""Connection history and favorites management."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConnectionManager:
    """Manages connection history and favorites."""

    def __init__(self, config_dir: str = None):
        """Initialize connection manager.

        Args:
            config_dir: Configuration directory path (default: ~/.ucm)
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.ucm")

        self.config_dir = Path(config_dir)
        self.history_file = self.config_dir / "history.yml"
        self.favorites_file = self.config_dir / "favorites.yml"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._history: List[Dict[str, Any]] = []
        self._favorites: List[str] = []  # List of connection identifiers (name:address)

        self._load_history()
        self._load_favorites()

    def _connection_id(self, connection: Dict[str, Any]) -> str:
        """Generate unique identifier for a connection.

        Args:
            connection: Connection dictionary

        Returns:
            Unique identifier string
        """
        return f"{connection.get('name', '')}:{connection.get('address', '')}"

    def _load_history(self) -> None:
        """Load connection history from file."""
        if not self.history_file.exists():
            self._history = []
            return

        try:
            with open(self.history_file) as f:
                data = yaml.safe_load(f)
                self._history = data if data else []
            logging.debug(f"Loaded {len(self._history)} history entries")
        except Exception as e:
            logging.error(f"Failed to load history: {e}")
            self._history = []

    def _save_history(self) -> None:
        """Save connection history to file."""
        try:
            with open(self.history_file, "w") as f:
                yaml.safe_dump(self._history, f, default_flow_style=False)
            logging.debug(f"Saved {len(self._history)} history entries")
        except Exception as e:
            logging.error(f"Failed to save history: {e}")

    def _load_favorites(self) -> None:
        """Load favorites from file."""
        if not self.favorites_file.exists():
            self._favorites = []
            return

        try:
            with open(self.favorites_file) as f:
                data = yaml.safe_load(f)
                self._favorites = data if data else []
            logging.debug(f"Loaded {len(self._favorites)} favorites")
        except Exception as e:
            logging.error(f"Failed to load favorites: {e}")
            self._favorites = []

    def _save_favorites(self) -> None:
        """Save favorites to file."""
        try:
            with open(self.favorites_file, "w") as f:
                yaml.safe_dump(self._favorites, f, default_flow_style=False)
            logging.debug(f"Saved {len(self._favorites)} favorites")
        except Exception as e:
            logging.error(f"Failed to save favorites: {e}")

    def record_connection(self, connection: Dict[str, Any]) -> None:
        """Record a connection use in history.

        Args:
            connection: Connection dictionary
        """
        conn_id = self._connection_id(connection)
        timestamp = datetime.now().isoformat()

        # Find existing entry
        existing_index = None
        for i, entry in enumerate(self._history):
            if self._connection_id(entry) == conn_id:
                existing_index = i
                break

        if existing_index is not None:
            # Update existing entry
            self._history[existing_index]["last_used"] = timestamp
            self._history[existing_index]["use_count"] = self._history[existing_index].get("use_count", 0) + 1
        else:
            # Add new entry
            history_entry = {
                "name": connection.get("name", ""),
                "address": connection.get("address", ""),
                "last_used": timestamp,
                "use_count": 1,
            }
            # Add optional fields if present
            if "user" in connection:
                history_entry["user"] = connection["user"]
            if "category" in connection:
                history_entry["category"] = connection["category"]

            self._history.insert(0, history_entry)

        # Keep only last 100 entries
        self._history = self._history[:100]

        self._save_history()
        logging.info(f"Recorded connection to {conn_id}")

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent connection history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent connections
        """
        return self._history[:limit]

    def is_favorite(self, connection: Dict[str, Any]) -> bool:
        """Check if connection is marked as favorite.

        Args:
            connection: Connection dictionary

        Returns:
            True if connection is a favorite
        """
        conn_id = self._connection_id(connection)
        return conn_id in self._favorites

    def toggle_favorite(self, connection: Dict[str, Any]) -> bool:
        """Toggle favorite status of a connection.

        Args:
            connection: Connection dictionary

        Returns:
            New favorite status (True if now favorite)
        """
        conn_id = self._connection_id(connection)

        if conn_id in self._favorites:
            self._favorites.remove(conn_id)
            self._save_favorites()
            logging.info(f"Removed {conn_id} from favorites")
            return False
        else:
            self._favorites.append(conn_id)
            self._save_favorites()
            logging.info(f"Added {conn_id} to favorites")
            return True

    def get_favorites(self) -> List[str]:
        """Get list of favorite connection identifiers.

        Returns:
            List of favorite connection IDs
        """
        return self._favorites.copy()

    def clear_history(self) -> None:
        """Clear all connection history."""
        self._history = []
        self._save_history()
        logging.info("Cleared connection history")

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics.

        Returns:
            Dictionary with statistics
        """
        total_connections = len(self._history)
        total_uses = sum(entry.get("use_count", 0) for entry in self._history)

        most_used = None
        if self._history:
            most_used = max(self._history, key=lambda x: x.get("use_count", 0))

        return {
            "total_connections": total_connections,
            "total_uses": total_uses,
            "favorites_count": len(self._favorites),
            "most_used": most_used,
        }


# Global instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager(config_dir: str = None) -> ConnectionManager:
    """Get or create global connection manager instance.

    Args:
        config_dir: Configuration directory path

    Returns:
        ConnectionManager instance
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager(config_dir)
    return _connection_manager


# vim: ts=4 sw=4 et
