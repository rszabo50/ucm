#!/usr/bin/env python3

"""Tests for connection management (history and favorites)."""

import os
import tempfile
import unittest

from ucm.connection_manager import ConnectionManager


class TestConnectionManager(unittest.TestCase):
    """Test ConnectionManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test config
        self.test_dir = tempfile.mkdtemp()
        self.manager = ConnectionManager(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil

        shutil.rmtree(self.test_dir)

    def test_record_connection(self):
        """Test recording a connection in history."""
        conn = {"name": "webserver", "address": "web.example.com"}

        self.manager.record_connection(conn)

        history = self.manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["name"], "webserver")
        self.assertEqual(history[0]["use_count"], 1)

    def test_record_connection_multiple_times(self):
        """Test recording same connection multiple times."""
        conn = {"name": "webserver", "address": "web.example.com"}

        self.manager.record_connection(conn)
        self.manager.record_connection(conn)
        self.manager.record_connection(conn)

        history = self.manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["use_count"], 3)

    def test_history_limit(self):
        """Test history is limited to 100 entries."""
        # Create 150 different connections
        for i in range(150):
            conn = {"name": f"server{i}", "address": f"192.168.1.{i % 255}"}
            self.manager.record_connection(conn)

        history = self.manager.get_history(limit=200)
        self.assertEqual(len(history), 100)

    def test_get_history_with_limit(self):
        """Test get_history respects limit parameter."""
        for i in range(20):
            conn = {"name": f"server{i}", "address": f"192.168.1.{i}"}
            self.manager.record_connection(conn)

        history = self.manager.get_history(limit=5)
        self.assertEqual(len(history), 5)

    def test_toggle_favorite(self):
        """Test toggling favorite status."""
        conn = {"name": "webserver", "address": "web.example.com"}

        # Initially not a favorite
        self.assertFalse(self.manager.is_favorite(conn))

        # Toggle on
        result = self.manager.toggle_favorite(conn)
        self.assertTrue(result)
        self.assertTrue(self.manager.is_favorite(conn))

        # Toggle off
        result = self.manager.toggle_favorite(conn)
        self.assertFalse(result)
        self.assertFalse(self.manager.is_favorite(conn))

    def test_favorites_persistence(self):
        """Test favorites are persisted to disk."""
        conn = {"name": "webserver", "address": "web.example.com"}

        self.manager.toggle_favorite(conn)

        # Create new manager instance with same config dir
        new_manager = ConnectionManager(self.test_dir)
        self.assertTrue(new_manager.is_favorite(conn))

    def test_history_persistence(self):
        """Test history is persisted to disk."""
        conn = {"name": "webserver", "address": "web.example.com"}

        self.manager.record_connection(conn)

        # Create new manager instance with same config dir
        new_manager = ConnectionManager(self.test_dir)
        history = new_manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["name"], "webserver")

    def test_connection_id_generation(self):
        """Test connection ID is correctly generated."""
        conn1 = {"name": "web", "address": "example.com"}
        conn2 = {"name": "web", "address": "other.com"}

        self.manager.toggle_favorite(conn1)
        self.assertTrue(self.manager.is_favorite(conn1))
        self.assertFalse(self.manager.is_favorite(conn2))

    def test_get_favorites(self):
        """Test getting list of favorites."""
        conn1 = {"name": "web1", "address": "web1.example.com"}
        conn2 = {"name": "web2", "address": "web2.example.com"}

        self.manager.toggle_favorite(conn1)
        self.manager.toggle_favorite(conn2)

        favorites = self.manager.get_favorites()
        self.assertEqual(len(favorites), 2)

    def test_clear_history(self):
        """Test clearing connection history."""
        for i in range(10):
            conn = {"name": f"server{i}", "address": f"192.168.1.{i}"}
            self.manager.record_connection(conn)

        self.assertEqual(len(self.manager.get_history(limit=20)), 10)

        self.manager.clear_history()
        self.assertEqual(len(self.manager.get_history()), 0)

    def test_get_stats(self):
        """Test getting connection statistics."""
        conn1 = {"name": "web", "address": "web.example.com"}
        conn2 = {"name": "db", "address": "db.example.com"}

        self.manager.record_connection(conn1)
        self.manager.record_connection(conn1)
        self.manager.record_connection(conn2)
        self.manager.toggle_favorite(conn1)

        stats = self.manager.get_stats()

        self.assertEqual(stats["total_connections"], 2)
        self.assertEqual(stats["total_uses"], 3)
        self.assertEqual(stats["favorites_count"], 1)
        self.assertIsNotNone(stats["most_used"])
        self.assertEqual(stats["most_used"]["name"], "web")

    def test_record_connection_with_optional_fields(self):
        """Test recording connection with optional fields."""
        conn = {"name": "webserver", "address": "web.example.com", "user": "admin", "category": "production"}

        self.manager.record_connection(conn)

        history = self.manager.get_history()
        self.assertEqual(history[0]["user"], "admin")
        self.assertEqual(history[0]["category"], "production")

    def test_history_most_recent_first(self):
        """Test history returns most recent connections first."""
        conn1 = {"name": "server1", "address": "192.168.1.1"}
        conn2 = {"name": "server2", "address": "192.168.1.2"}
        conn3 = {"name": "server3", "address": "192.168.1.3"}

        self.manager.record_connection(conn1)
        self.manager.record_connection(conn2)
        self.manager.record_connection(conn3)

        history = self.manager.get_history()
        self.assertEqual(history[0]["name"], "server3")
        self.assertEqual(history[1]["name"], "server2")
        self.assertEqual(history[2]["name"], "server1")

    def test_config_directory_creation(self):
        """Test config directory is created if it doesn't exist."""
        new_dir = os.path.join(self.test_dir, "newdir")
        self.assertFalse(os.path.exists(new_dir))

        _ = ConnectionManager(new_dir)
        self.assertTrue(os.path.exists(new_dir))

    def test_empty_history_file(self):
        """Test handling of empty or missing history file."""
        # History file doesn't exist yet
        self.assertEqual(len(self.manager.get_history()), 0)

    def test_empty_favorites_file(self):
        """Test handling of empty or missing favorites file."""
        conn = {"name": "webserver", "address": "web.example.com"}
        # Favorites file doesn't exist yet
        self.assertFalse(self.manager.is_favorite(conn))


if __name__ == "__main__":
    unittest.main()
