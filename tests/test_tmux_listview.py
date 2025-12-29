#!/usr/bin/env python3

"""Tests for TmuxListView."""

from unittest.mock import MagicMock, patch

import pytest
from ucm.TmuxListView import TmuxListView


class TestTmuxListView:
    """Test TmuxListView functionality."""

    @pytest.fixture
    def tmux_list_view(self):
        """Create TmuxListView instance."""
        return TmuxListView()

    def test_initialization(self, tmux_list_view):
        """Test TmuxListView initialization."""
        assert tmux_list_view.name == "Tmux"
        assert tmux_list_view.tmux_service is not None
        assert "name" in tmux_list_view.filter_fields
        assert "index" in tmux_list_view.filter_fields

    def test_formatter_active_window(self, tmux_list_view):
        """Test formatting of active window."""
        record = {"index": 0, "name": "main", "active": True, "panes": 1}
        formatted = tmux_list_view.formatter(record)

        assert "▶" in formatted  # Active marker
        assert "0" in formatted  # Index
        assert "main" in formatted  # Name
        assert "(1 pane)" in formatted  # Panes

    def test_formatter_inactive_window(self, tmux_list_view):
        """Test formatting of inactive window."""
        record = {"index": 1, "name": "editor", "active": False, "panes": 2}
        formatted = tmux_list_view.formatter(record)

        assert "▶" not in formatted  # No active marker
        assert "1" in formatted  # Index
        assert "editor" in formatted  # Name
        assert "(2 panes)" in formatted  # Multiple panes

    def test_formatter_long_name_truncation(self, tmux_list_view):
        """Test that long window names are truncated."""
        long_name = "a" * 70
        record = {"index": 2, "name": long_name, "active": False, "panes": 1}
        formatted = tmux_list_view.formatter(record)

        # Should be truncated with ellipsis
        assert "..." in formatted
        # Total formatted length should be reasonable
        assert len(formatted) < 100

    def test_fetch_data(self, tmux_list_view):
        """Test fetching tmux windows data."""
        mock_windows = [
            {"index": 0, "name": "main", "active": True, "panes": 1},
            {"index": 1, "name": "editor", "active": False, "panes": 2},
        ]

        with patch("ucm.TmuxListView.TmuxService.list_windows", return_value=mock_windows):
            data = tmux_list_view.fetch_data()

            assert data is not None
            assert len(data) == 2
            # Should add list_index to each window
            assert data[0]["list_index"] == 0
            assert data[1]["list_index"] == 1

    def test_fetch_data_no_windows(self, tmux_list_view):
        """Test fetching data when no windows exist."""
        with patch.object(tmux_list_view.tmux_service, "list_windows", return_value=[]):
            data = tmux_list_view.fetch_data()
            assert data is None

    def test_double_click_callback(self, tmux_list_view):
        """Test double-click switches to window."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}
        tmux_list_view.selected = MagicMock(item_data=mock_data)

        with patch.object(tmux_list_view, "switch_to_window") as mock_switch:
            tmux_list_view.double_click_callback()
            mock_switch.assert_called_once_with(mock_data)

    def test_keypress_callback_switch_window_c(self, tmux_list_view):
        """Test 'c' key switches to window."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}

        with patch.object(tmux_list_view, "switch_to_window") as mock_switch:
            with patch("ucm.Widgets.ListView.keypress_callback"):
                tmux_list_view.keypress_callback((80, 24), "c", mock_data)
                mock_switch.assert_called_once_with(mock_data)

    def test_keypress_callback_switch_window_enter(self, tmux_list_view):
        """Test 'enter' key switches to window."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}

        with patch.object(tmux_list_view, "switch_to_window") as mock_switch:
            with patch("ucm.Widgets.ListView.keypress_callback"):
                tmux_list_view.keypress_callback((80, 24), "enter", mock_data)
                mock_switch.assert_called_once_with(mock_data)

    def test_keypress_callback_close_window(self, tmux_list_view):
        """Test 'x' key closes window."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}

        with patch.object(tmux_list_view, "close_window") as mock_close:
            with patch("ucm.Widgets.ListView.keypress_callback"):
                tmux_list_view.keypress_callback((80, 24), "x", mock_data)
                mock_close.assert_called_once_with(mock_data)

    def test_keypress_callback_refresh(self, tmux_list_view):
        """Test 'r' key refreshes window list."""
        with patch.object(tmux_list_view, "filter_and_set") as mock_refresh:
            with patch("ucm.Widgets.ListView.keypress_callback"):
                tmux_list_view.keypress_callback((80, 24), "r", None)
                mock_refresh.assert_called_once_with("")

    def test_switch_to_window_success(self, tmux_list_view):
        """Test switching to window successfully."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}
        tmux_list_view.filter_edit = MagicMock(edit_text="")

        with patch.object(tmux_list_view.tmux_service, "switch_window", return_value=0):
            with patch.object(tmux_list_view, "filter_and_set") as mock_refresh:
                tmux_list_view.switch_to_window(mock_data)
                mock_refresh.assert_called_once_with("")

    def test_switch_to_window_no_data(self, tmux_list_view):
        """Test switching to window with no data."""
        with patch.object(tmux_list_view.tmux_service, "switch_window") as mock_switch:
            tmux_list_view.switch_to_window(None)
            mock_switch.assert_not_called()

    def test_switch_to_window_no_index(self, tmux_list_view):
        """Test switching to window without index."""
        mock_data = {"name": "editor", "active": False, "panes": 1}

        with patch.object(tmux_list_view.tmux_service, "switch_window") as mock_switch:
            tmux_list_view.switch_to_window(mock_data)
            mock_switch.assert_not_called()

    def test_switch_to_window_failure(self, tmux_list_view):
        """Test switching to window failure."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}
        tmux_list_view.filter_edit = MagicMock(edit_text="test")

        with patch.object(tmux_list_view.tmux_service, "switch_window", return_value=1):
            with patch.object(tmux_list_view, "filter_and_set") as mock_refresh:
                tmux_list_view.switch_to_window(mock_data)
                # Should not refresh on failure
                mock_refresh.assert_not_called()

    def test_close_window_success(self, tmux_list_view):
        """Test closing window successfully."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}
        tmux_list_view.filter_edit = MagicMock(edit_text="")

        with patch.object(tmux_list_view.tmux_service, "kill_window", return_value=0):
            with patch.object(tmux_list_view, "filter_and_set") as mock_refresh:
                tmux_list_view.close_window(mock_data)
                mock_refresh.assert_called_once_with("")

    def test_close_window_active_window(self, tmux_list_view):
        """Test closing active window is prevented."""
        mock_data = {"index": 0, "name": "ucm", "active": True, "panes": 1}

        with patch.object(tmux_list_view.tmux_service, "kill_window") as mock_kill:
            tmux_list_view.close_window(mock_data)
            # Should not attempt to kill active window
            mock_kill.assert_not_called()

    def test_close_window_no_data(self, tmux_list_view):
        """Test closing window with no data."""
        with patch.object(tmux_list_view.tmux_service, "kill_window") as mock_kill:
            tmux_list_view.close_window(None)
            mock_kill.assert_not_called()

    def test_close_window_no_index(self, tmux_list_view):
        """Test closing window without index."""
        mock_data = {"name": "editor", "active": False, "panes": 1}

        with patch.object(tmux_list_view.tmux_service, "kill_window") as mock_kill:
            tmux_list_view.close_window(mock_data)
            mock_kill.assert_not_called()

    def test_close_window_failure(self, tmux_list_view):
        """Test closing window failure."""
        mock_data = {"index": 1, "name": "editor", "active": False, "panes": 1}
        tmux_list_view.filter_edit = MagicMock(edit_text="test")

        with patch.object(tmux_list_view.tmux_service, "kill_window", return_value=1):
            with patch.object(tmux_list_view, "filter_and_set") as mock_refresh:
                tmux_list_view.close_window(mock_data)
                # Should not refresh on failure
                mock_refresh.assert_not_called()

    def test_get_filter_widgets(self, tmux_list_view):
        """Test filter widgets contain help text."""
        with patch("ucm.Widgets.ListView.get_filter_widgets", return_value=MagicMock()):
            widgets = tmux_list_view.get_filter_widgets()
            # Should return a Columns widget with help text
            assert widgets is not None


# vim: ts=4 sw=4 et
