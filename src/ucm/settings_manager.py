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

"""Application settings management."""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class SettingsManager:
    """Manages application settings."""

    DEFAULT_SETTINGS = {
        "terminal": {
            "integration": "none",  # Options: "none", "tmux", "iterm2"
            "tmux": {
                "mode": "window",  # Only "window" mode is supported
                "auto_name": True,  # Auto-name windows with connection info
            },
            "iterm2": {
                "profile": "Default",  # iTerm2 profile to use
            },
        }
    }

    def __init__(self, config_dir: str = None):
        """Initialize settings manager.

        Args:
            config_dir: Configuration directory path (default: ~/.ucm)
        """
        if config_dir is None:
            config_dir = os.path.expanduser("~/.ucm")

        self.config_dir = Path(config_dir)
        self.settings_file = self.config_dir / "config.yml"

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._settings: Dict[str, Any] = {}
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from file or create default settings."""
        import copy

        if not self.settings_file.exists():
            logging.info("Settings file not found, creating default settings")
            self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)
            self._save_settings()
            return

        try:
            with open(self.settings_file) as f:
                data = yaml.safe_load(f)
                if data is None:
                    self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)
                else:
                    # Merge with defaults to ensure all keys exist
                    self._settings = self._merge_with_defaults(data)
            logging.debug(f"Loaded settings from {self.settings_file}")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")
            self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)

    def _merge_with_defaults(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults to ensure all keys exist.

        Args:
            data: Loaded settings data

        Returns:
            Merged settings dictionary
        """
        import copy

        merged = copy.deepcopy(self.DEFAULT_SETTINGS)

        def deep_merge(base: dict, override: dict) -> dict:
            """Recursively merge override into base."""
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        return deep_merge(merged, data)

    def _save_settings(self) -> None:
        """Save settings to file."""
        try:
            with open(self.settings_file, "w") as f:
                yaml.safe_dump(self._settings, f, default_flow_style=False, sort_keys=False)
            logging.debug(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a setting value using dot notation.

        Args:
            key_path: Setting key path (e.g., "terminal.integration")
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        keys = key_path.split(".")
        value = self._settings

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set a setting value using dot notation.

        Args:
            key_path: Setting key path (e.g., "terminal.integration")
            value: Value to set
        """
        keys = key_path.split(".")
        target = self._settings

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # Set the value
        target[keys[-1]] = value
        self._save_settings()
        logging.debug(f"Set {key_path} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """Get all settings.

        Returns:
            Complete settings dictionary
        """
        return self._settings.copy()

    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        import copy

        self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)
        self._save_settings()
        logging.info("Reset settings to defaults")

    def get_terminal_integration(self) -> str:
        """Get current terminal integration mode.

        Returns:
            Integration mode: "none", "tmux", or "iterm2"
        """
        return self.get("terminal.integration", "none")

    def set_terminal_integration(self, mode: str) -> None:
        """Set terminal integration mode.

        Args:
            mode: Integration mode ("none", "tmux", or "iterm2")
        """
        if mode not in ["none", "tmux", "iterm2"]:
            raise ValueError(f"Invalid terminal integration mode: {mode}")
        self.set("terminal.integration", mode)

    def get_tmux_settings(self) -> Dict[str, Any]:
        """Get tmux-specific settings.

        Returns:
            Tmux settings dictionary
        """
        return self.get("terminal.tmux", {})

    def get_iterm2_settings(self) -> Dict[str, Any]:
        """Get iTerm2-specific settings.

        Returns:
            iTerm2 settings dictionary
        """
        return self.get("terminal.iterm2", {})


# Global instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager(config_dir: str = None) -> SettingsManager:
    """Get or create global settings manager instance.

    Args:
        config_dir: Configuration directory path

    Returns:
        SettingsManager instance
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager(config_dir)
    return _settings_manager


# vim: ts=4 sw=4 et
