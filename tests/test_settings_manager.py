#!/usr/bin/env python3

"""Tests for settings manager."""

from pathlib import Path

import pytest
import yaml
from ucm import settings_manager as settings_manager_module
from ucm.settings_manager import SettingsManager, get_settings_manager


class TestSettingsManager:
    """Test settings manager functionality."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset the global singleton before each test."""
        settings_manager_module._settings_manager = None
        yield
        settings_manager_module._settings_manager = None

    @pytest.fixture(scope="function")
    def temp_config_dir(self, tmp_path):
        """Create temporary config directory."""
        return str(tmp_path)

    @pytest.fixture(scope="function")
    def settings_manager(self, temp_config_dir):
        """Create settings manager with temporary directory."""
        # Delete config file if it exists to ensure clean state
        config_file = Path(temp_config_dir) / "config.yml"
        if config_file.exists():
            config_file.unlink()
        sm = SettingsManager(temp_config_dir)
        # Reset to defaults to ensure clean state
        sm.reset_to_defaults()
        return sm

    def test_initialization(self, temp_config_dir):
        """Test settings manager initialization creates default settings."""
        sm = SettingsManager(temp_config_dir)
        settings_file = Path(temp_config_dir) / "config.yml"

        assert settings_file.exists()
        assert sm.get_terminal_integration() == "none"

    def test_default_settings_structure(self, settings_manager):
        """Test default settings have correct structure."""
        settings = settings_manager.get_all()

        assert "terminal" in settings
        assert "integration" in settings["terminal"]
        assert "tmux" in settings["terminal"]
        assert "iterm2" in settings["terminal"]

        # Check tmux settings
        assert "mode" in settings["terminal"]["tmux"]
        assert "auto_name" in settings["terminal"]["tmux"]

        # Check iTerm2 settings
        assert "new_tab" in settings["terminal"]["iterm2"]
        assert "profile" in settings["terminal"]["iterm2"]

    def test_get_with_dot_notation(self, settings_manager):
        """Test getting values with dot notation."""
        assert settings_manager.get("terminal.integration") == "none"
        assert settings_manager.get("terminal.tmux.mode") == "window"
        assert settings_manager.get("terminal.tmux.auto_name") is True
        assert settings_manager.get("terminal.iterm2.new_tab") is True
        assert settings_manager.get("terminal.iterm2.profile") == "Default"

    def test_get_with_default(self, settings_manager):
        """Test getting values with default fallback."""
        assert settings_manager.get("nonexistent.key", "default") == "default"
        assert settings_manager.get("terminal.nonexistent", 42) == 42

    def test_set_with_dot_notation(self, settings_manager):
        """Test setting values with dot notation."""
        settings_manager.set("terminal.integration", "tmux")
        assert settings_manager.get("terminal.integration") == "tmux"

        settings_manager.set("terminal.tmux.mode", "pane")
        assert settings_manager.get("terminal.tmux.mode") == "pane"

    def test_set_creates_nested_keys(self, settings_manager):
        """Test setting creates nested keys if they don't exist."""
        settings_manager.set("new.nested.key", "value")
        assert settings_manager.get("new.nested.key") == "value"

    def test_settings_persistence(self, temp_config_dir):
        """Test settings are persisted to file."""
        sm1 = SettingsManager(temp_config_dir)
        sm1.set("terminal.integration", "tmux")
        sm1.set("terminal.tmux.mode", "pane")

        # Create new instance - should load from file
        sm2 = SettingsManager(temp_config_dir)
        assert sm2.get("terminal.integration") == "tmux"
        assert sm2.get("terminal.tmux.mode") == "pane"

    def test_terminal_integration_getter(self, settings_manager):
        """Test terminal integration getter."""
        assert settings_manager.get_terminal_integration() == "none"

        settings_manager.set("terminal.integration", "tmux")
        assert settings_manager.get_terminal_integration() == "tmux"

    def test_terminal_integration_setter(self, settings_manager):
        """Test terminal integration setter."""
        settings_manager.set_terminal_integration("tmux")
        assert settings_manager.get("terminal.integration") == "tmux"

        settings_manager.set_terminal_integration("iterm2")
        assert settings_manager.get("terminal.integration") == "iterm2"

    def test_terminal_integration_setter_validation(self, settings_manager):
        """Test terminal integration setter validates input."""
        with pytest.raises(ValueError):
            settings_manager.set_terminal_integration("invalid")

    def test_get_tmux_settings(self, settings_manager):
        """Test getting tmux settings."""
        tmux_settings = settings_manager.get_tmux_settings()

        assert isinstance(tmux_settings, dict)
        assert "mode" in tmux_settings
        assert "auto_name" in tmux_settings
        assert tmux_settings["mode"] == "window"
        assert tmux_settings["auto_name"] is True

    def test_get_iterm2_settings(self, settings_manager):
        """Test getting iTerm2 settings."""
        iterm2_settings = settings_manager.get_iterm2_settings()

        assert isinstance(iterm2_settings, dict)
        assert "new_tab" in iterm2_settings
        assert "profile" in iterm2_settings
        assert iterm2_settings["new_tab"] is True
        assert iterm2_settings["profile"] == "Default"

    def test_reset_to_defaults(self, settings_manager):
        """Test resetting to default settings."""
        # Modify settings
        settings_manager.set("terminal.integration", "tmux")
        settings_manager.set("terminal.tmux.mode", "pane")

        # Reset
        settings_manager.reset_to_defaults()

        # Verify defaults are restored
        assert settings_manager.get("terminal.integration") == "none"
        assert settings_manager.get("terminal.tmux.mode") == "window"

    def test_merge_with_defaults(self, temp_config_dir):
        """Test loading settings merges with defaults for missing keys."""
        settings_file = Path(temp_config_dir) / "config.yml"

        # Write partial settings
        partial_settings = {"terminal": {"integration": "tmux"}}
        with open(settings_file, "w") as f:
            yaml.safe_dump(partial_settings, f)

        # Load settings
        sm = SettingsManager(temp_config_dir)

        # Verify custom value is preserved
        assert sm.get("terminal.integration") == "tmux"

        # Verify missing keys are filled with defaults
        assert sm.get("terminal.tmux.mode") == "window"
        assert sm.get("terminal.iterm2.new_tab") is True

    def test_config_directory_creation(self, temp_config_dir):
        """Test config directory is created if it doesn't exist."""
        nested_dir = Path(temp_config_dir) / "nested" / "config"
        SettingsManager(str(nested_dir))

        assert nested_dir.exists()
        assert (nested_dir / "config.yml").exists()

    def test_get_settings_manager_singleton(self, temp_config_dir):
        """Test get_settings_manager returns singleton instance."""
        sm1 = get_settings_manager(temp_config_dir)
        sm2 = get_settings_manager(temp_config_dir)

        assert sm1 is sm2

    def test_yaml_format_preserved(self, settings_manager, temp_config_dir):
        """Test settings file is saved in readable YAML format."""
        settings_file = Path(temp_config_dir) / "config.yml"

        with open(settings_file) as f:
            content = f.read()

        # Check file is valid YAML
        yaml.safe_load(content)

        # Check formatting (no flow style, readable)
        assert "terminal:" in content
        assert "integration:" in content
        assert "tmux:" in content


# vim: ts=4 sw=4 et
