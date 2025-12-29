#!/usr/bin/env python3

"""Tests for iTerm2 service."""

from unittest.mock import MagicMock, patch

import pytest
from ucm.services.iterm2_service import ITerm2Service


class TestITerm2Service:
    """Test iTerm2 service functionality."""

    @pytest.fixture
    def iterm2_service(self):
        """Create iTerm2 service instance."""
        return ITerm2Service()

    def test_is_iterm2_available_on_macos_with_iterm2(self, iterm2_service):
        """Test iTerm2 availability detection on macOS with iTerm2 installed."""
        with patch("platform.system", return_value="Darwin"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="true\n", returncode=0)
                assert iterm2_service.is_iterm2_available() is True

    def test_is_iterm2_available_on_macos_without_iterm2(self, iterm2_service):
        """Test iTerm2 availability detection on macOS without iTerm2."""
        with patch("platform.system", return_value="Darwin"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(stdout="false\n", returncode=0)
                assert iterm2_service.is_iterm2_available() is False

    def test_is_iterm2_available_on_linux(self, iterm2_service):
        """Test iTerm2 availability detection on non-macOS."""
        with patch("platform.system", return_value="Linux"):
            assert iterm2_service.is_iterm2_available() is False

    def test_is_iterm2_available_on_exception(self, iterm2_service):
        """Test iTerm2 availability detection handles exceptions."""
        with patch("platform.system", return_value="Darwin"):
            with patch("subprocess.run", side_effect=Exception("Test error")):
                assert iterm2_service.is_iterm2_available() is False

    def test_is_inside_iterm2_when_inside(self, iterm2_service):
        """Test detection when inside iTerm2."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert iterm2_service.is_inside_iterm2() is True

    def test_is_inside_iterm2_when_not_inside(self, iterm2_service):
        """Test detection when not inside iTerm2."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert iterm2_service.is_inside_iterm2() is False

    def test_is_inside_iterm2_on_exception(self, iterm2_service):
        """Test detection handles exceptions."""
        with patch("subprocess.run", side_effect=Exception("Test error")):
            assert iterm2_service.is_inside_iterm2() is False

    def test_create_tab_success(self, iterm2_service):
        """Test creating iTerm2 tab successfully."""
        with patch.object(iterm2_service, "is_iterm2_available", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                rc = iterm2_service.create_tab("ssh user@host", name="test-tab", profile="Default")
                assert rc == 0
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "osascript"
                assert "-e" in args

    def test_create_tab_without_name(self, iterm2_service):
        """Test creating iTerm2 tab without name."""
        with patch.object(iterm2_service, "is_iterm2_available", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)
                rc = iterm2_service.create_tab("ssh user@host", profile="Default")
                assert rc == 0

    def test_create_tab_iterm2_not_available(self, iterm2_service):
        """Test creating tab fails when iTerm2 not available."""
        with patch.object(iterm2_service, "is_iterm2_available", return_value=False):
            rc = iterm2_service.create_tab("ssh user@host")
            assert rc == 1

    def test_create_tab_on_exception(self, iterm2_service):
        """Test creating tab handles exceptions."""
        with patch.object(iterm2_service, "is_iterm2_available", return_value=True):
            with patch("subprocess.run", side_effect=Exception("Test error")):
                rc = iterm2_service.create_tab("ssh user@host")
                assert rc == 1

    def test_launch_ssh_connection(self, iterm2_service):
        """Test launching SSH connection in new tab."""
        with patch.object(iterm2_service, "create_tab", return_value=0) as mock_create:
            rc = iterm2_service.launch_ssh_connection(
                ssh_command="ssh user@host",
                connection_name="test-host",
                profile="Default",
            )
            assert rc == 0
            mock_create.assert_called_once()
            assert "ssh user@host" in mock_create.call_args[0]
            assert "🐧 test-host" == mock_create.call_args[1]["name"]

    def test_launch_docker_connection(self, iterm2_service):
        """Test launching Docker connection in new tab."""
        with patch.object(iterm2_service, "create_tab", return_value=0) as mock_create:
            rc = iterm2_service.launch_docker_connection(
                docker_command="docker exec -it container bash",
                container_name="test-container",
                profile="Default",
            )
            assert rc == 0
            mock_create.assert_called_once()
            assert "docker exec -it container bash" in mock_create.call_args[0]
            assert "🐳 test-container" == mock_create.call_args[1]["name"]


# vim: ts=4 sw=4 et
