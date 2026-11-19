#!/usr/bin/env python3

"""Tests for DockerListView refresh behavior."""

from unittest.mock import MagicMock, patch

import pytest

from ucm.DockerListView import DockerListView
from ucm.Registry import Registry


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure registry state does not leak across tests."""
    registry = Registry()
    for attr in ["main_loop", "app"]:
        if hasattr(registry, attr):
            delattr(registry, attr)
    yield
    for attr in ["main_loop", "app"]:
        if hasattr(registry, attr):
            delattr(registry, attr)


@pytest.fixture
def docker_list_view():
    """Create DockerListView with mocked docker service."""
    docker_service = MagicMock()
    docker_service.list_containers.return_value = [
        {"containerId": "id-1", "name": "one", "image": "img1"},
        {"containerId": "id-2", "name": "two", "image": "img2"},
    ]
    return DockerListView(docker_service=docker_service)


def test_refresh_preserve_state_keeps_selected_container(docker_list_view):
    """Refresh should keep focus on previously selected container when present."""
    docker_list_view.selected = docker_list_view.walker[1]

    docker_list_view.docker_service.list_containers.return_value = [
        {"containerId": "id-1", "name": "one", "image": "img1"},
        {"containerId": "id-2", "name": "two", "image": "img2-new"},
        {"containerId": "id-3", "name": "three", "image": "img3"},
    ]

    docker_list_view.refresh_preserve_state()
    focused_item, _ = docker_list_view.walker.get_focus()
    assert focused_item.item_data["containerId"] == "id-2"


def test_auto_refresh_callback_refreshes_only_when_active(docker_list_view):
    """Auto-refresh callback should refresh only when Docker view is active."""
    active_view = object()
    docker_list_view.view = active_view
    Registry().app = MagicMock(view_holder=MagicMock(_w=active_view))

    with patch.object(docker_list_view, "refresh_preserve_state") as mock_refresh:
        with patch.object(docker_list_view, "_schedule_auto_refresh"):
            docker_list_view._auto_refresh_callback()
            mock_refresh.assert_called_once()

    Registry().app = MagicMock(view_holder=MagicMock(_w=object()))

    with patch.object(docker_list_view, "refresh_preserve_state") as mock_refresh:
        with patch.object(docker_list_view, "_schedule_auto_refresh"):
            docker_list_view._auto_refresh_callback()
            mock_refresh.assert_not_called()
