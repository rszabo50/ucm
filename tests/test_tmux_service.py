#!/usr/bin/env python3

"""Tests for tmux service."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest
from ucm.services.tmux_service import TmuxService


class TestTmuxService:
    """Test tmux service functionality."""

    @pytest.fixture
    def tmux_service(self):
        """Create tmux service instance."""
        return TmuxService()

    def test_is_tmux_available_when_installed(self, tmux_service):
        """Test tmux availability detection when tmux is installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert tmux_service.is_tmux_available() is True
            mock_run.assert_called_once()

    def test_is_tmux_available_when_not_installed(self, tmux_service):
        """Test tmux availability detection when tmux is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert tmux_service.is_tmux_available() is False

    def test_is_tmux_available_on_exception(self, tmux_service):
        """Test tmux availability detection handles exceptions."""
        with patch("subprocess.run", side_effect=Exception("Test error")):
            assert tmux_service.is_tmux_available() is False

    def test_is_inside_tmux_when_tmux_env_set(self, tmux_service):
        """Test detection when inside tmux session."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            assert tmux_service.is_inside_tmux() is True

    def test_is_inside_tmux_when_tmux_env_not_set(self, tmux_service):
        """Test detection when not inside tmux session."""
        with patch.dict("os.environ", {}, clear=True):
            assert tmux_service.is_inside_tmux() is False

    def test_get_current_session_when_inside_tmux(self, tmux_service):
        """Test getting current session name when inside tmux."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="my-session\n", returncode=0)
                session = tmux_service.get_current_session()
                assert session == "my-session"

    def test_get_current_session_when_not_inside_tmux(self, tmux_service):
        """Test getting current session name when not inside tmux."""
        with patch.dict("os.environ", {}, clear=True):
            session = tmux_service.get_current_session()
            assert session is None

    def test_get_current_session_on_exception(self, tmux_service):
        """Test getting current session handles exceptions."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "tmux")):
                session = tmux_service.get_current_session()
                assert session is None

    def test_create_window_inside_tmux(self, tmux_service):
        """Test creating tmux window when inside tmux."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                rc = tmux_service.create_window("ssh user@host", name="test-window")
                assert rc == 0
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "tmux"
                assert args[1] == "new-window"
                assert "-n" in args
                assert "test-window" in args

    def test_create_window_without_name(self, tmux_service):
        """Test creating tmux window without name."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                rc = tmux_service.create_window("ssh user@host")
                assert rc == 0
                args = mock_run.call_args[0][0]
                assert "-n" not in args

    def test_create_window_not_inside_tmux(self, tmux_service):
        """Test creating window fails when not inside tmux."""
        with patch.dict("os.environ", {}, clear=True):
            rc = tmux_service.create_window("ssh user@host")
            assert rc == 1

    def test_create_window_on_exception(self, tmux_service):
        """Test creating window handles exceptions."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run", side_effect=Exception("Test error")):
                rc = tmux_service.create_window("ssh user@host")
                assert rc == 1

    def test_create_pane_inside_tmux(self, tmux_service):
        """Test creating tmux pane when inside tmux."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                rc = tmux_service.create_pane("ssh user@host")
                assert rc == 0
                args = mock_run.call_args[0][0]
                assert args[0] == "tmux"
                assert args[1] == "split-window"

    def test_create_pane_not_inside_tmux(self, tmux_service):
        """Test creating pane fails when not inside tmux."""
        with patch.dict("os.environ", {}, clear=True):
            rc = tmux_service.create_pane("ssh user@host")
            assert rc == 1

    def test_launch_ssh_connection_window_mode(self, tmux_service):
        """Test launching SSH connection in window mode."""
        with patch.object(tmux_service, "create_window", return_value=0) as mock_create:
            rc = tmux_service.launch_ssh_connection(
                ssh_command="ssh user@host",
                connection_name="webserver",
                mode="window",
                auto_name=True,
            )
            assert rc == 0
            mock_create.assert_called_once_with("ssh user@host", name="🐧 webserver")

    def test_launch_ssh_connection_pane_mode(self, tmux_service):
        """Test launching SSH connection in pane mode."""
        with patch.object(tmux_service, "create_pane", return_value=0) as mock_create:
            rc = tmux_service.launch_ssh_connection(
                ssh_command="ssh user@host",
                connection_name="webserver",
                mode="pane",
                auto_name=True,
            )
            assert rc == 0
            mock_create.assert_called_once_with("ssh user@host")

    def test_launch_ssh_connection_without_auto_name(self, tmux_service):
        """Test launching SSH connection without auto-naming."""
        with patch.object(tmux_service, "create_window", return_value=0) as mock_create:
            rc = tmux_service.launch_ssh_connection(
                ssh_command="ssh user@host",
                connection_name="webserver",
                mode="window",
                auto_name=False,
            )
            assert rc == 0
            mock_create.assert_called_once_with("ssh user@host", name=None)

    def test_launch_docker_connection_window_mode(self, tmux_service):
        """Test launching Docker connection in window mode."""
        with patch.object(tmux_service, "create_window", return_value=0) as mock_create:
            rc = tmux_service.launch_docker_connection(
                docker_command="docker exec -it container bash",
                container_name="my-container",
                mode="window",
                auto_name=True,
            )
            assert rc == 0
            mock_create.assert_called_once_with("docker exec -it container bash", name="🐳 my-container")

    def test_launch_docker_connection_pane_mode(self, tmux_service):
        """Test launching Docker connection in pane mode."""
        with patch.object(tmux_service, "create_pane", return_value=0) as mock_create:
            rc = tmux_service.launch_docker_connection(
                docker_command="docker exec -it container bash",
                container_name="my-container",
                mode="pane",
                auto_name=True,
            )
            assert rc == 0
            mock_create.assert_called_once_with("docker exec -it container bash")

    def test_get_current_window_index_inside_tmux(self, tmux_service):
        """Test getting current window index when inside tmux."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="3\n", returncode=0)
                window_index = tmux_service.get_current_window_index()
                assert window_index == 3

    def test_get_current_window_index_not_inside_tmux(self, tmux_service):
        """Test getting current window index when not inside tmux."""
        with patch.dict("os.environ", {}, clear=True):
            window_index = tmux_service.get_current_window_index()
            assert window_index is None

    def test_get_current_window_index_on_exception(self, tmux_service):
        """Test getting current window index handles exceptions."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run", side_effect=Exception("Test error")):
                window_index = tmux_service.get_current_window_index()
                assert window_index is None

    def test_setup_ucm_return_key_inside_tmux(self, tmux_service):
        """Test setting up UCM return key when inside tmux."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run") as mock_run:
                with patch("os.getpid", return_value=12345):
                    mock_run.return_value = MagicMock(returncode=0)
                    rc = tmux_service.setup_ucm_return_key(2, key="u")
                    assert rc == 0
                    mock_run.assert_called_once()
                    args = mock_run.call_args[0][0]
                    assert args[0] == "tmux"
                    assert args[1] == "bind-key"
                    assert args[2] == "u"
                    assert args[3] == "run-shell"
                    assert "select-window -t 2" in args[4]
                    assert "kill -WINCH 12345" in args[4]

    def test_setup_ucm_return_key_not_inside_tmux(self, tmux_service):
        """Test setting up UCM return key fails when not inside tmux."""
        with patch.dict("os.environ", {}, clear=True):
            rc = tmux_service.setup_ucm_return_key(2)
            assert rc == 1

    def test_setup_ucm_return_key_on_exception(self, tmux_service):
        """Test setting up UCM return key handles exceptions."""
        with patch.dict("os.environ", {"TMUX": "/tmp/tmux-1000/default,12345,0"}):
            with patch("subprocess.run", side_effect=Exception("Test error")):
                rc = tmux_service.setup_ucm_return_key(2)
                assert rc == 1


# vim: ts=4 sw=4 et
