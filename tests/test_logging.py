#!/usr/bin/env python3

"""Tests for logging functionality."""

import json
import logging
import tempfile
import unittest
from pathlib import Path

from ucm.__main__ import JSONFormatter, setup_logging


class TestLogging(unittest.TestCase):
    """Test logging configuration and formatters."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = Path(self.temp_dir) / "test.log"

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        # Remove all handlers to prevent interference with other tests
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)

        shutil.rmtree(self.temp_dir)

    def test_setup_logging_text_format(self):
        """Test logging setup with text format."""
        logger = setup_logging(
            log_level="INFO",
            log_file=str(self.log_file),
            log_format="text",
        )

        logger.info("Test message")

        # Check log file exists
        self.assertTrue(self.log_file.exists())

        # Check log contains message
        content = self.log_file.read_text()
        self.assertIn("Test message", content)
        self.assertIn("INFO", content)

    def test_setup_logging_json_format(self):
        """Test logging setup with JSON format."""
        logger = setup_logging(
            log_level="INFO",
            log_file=str(self.log_file),
            log_format="json",
        )

        logger.info("Test JSON message")

        # Check log file exists
        self.assertTrue(self.log_file.exists())

        # Check log contains valid JSON
        content = self.log_file.read_text()
        lines = [line for line in content.strip().split("\n") if line]

        # Each line should be valid JSON
        for line in lines:
            log_entry = json.loads(line)
            self.assertIn("message", log_entry)
            self.assertIn("level", log_entry)
            self.assertIn("timestamp", log_entry)

        # Find our test message
        found = False
        for line in lines:
            log_entry = json.loads(line)
            if log_entry.get("message") == "Test JSON message":
                found = True
                self.assertEqual(log_entry["level"], "INFO")
                break

        self.assertTrue(found, "Test message not found in logs")

    def test_setup_logging_debug_level(self):
        """Test logging with DEBUG level."""
        logger = setup_logging(
            log_level="DEBUG",
            log_file=str(self.log_file),
            log_format="text",
        )

        logger.debug("Debug message")
        logger.info("Info message")

        content = self.log_file.read_text()
        self.assertIn("Debug message", content)
        self.assertIn("Info message", content)

    def test_json_formatter_with_exception(self):
        """Test JSON formatter includes exception info."""
        import sys

        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S")

        # Create a log record with exception
        try:
            raise ValueError("Test exception")
        except ValueError:
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=exc_info,
            )

        formatted = formatter.format(record)
        log_entry = json.loads(formatted)

        self.assertIn("exception", log_entry)
        self.assertIn("ValueError", log_entry["exception"])
        self.assertIn("Test exception", log_entry["exception"])

    def test_log_rotation_setup(self):
        """Test that log rotation is configured."""
        _ = setup_logging(
            log_level="INFO",
            log_file=str(self.log_file),
            log_format="text",
            max_bytes=1024,  # 1KB for testing
            backup_count=3,
        )

        # Verify logger has a RotatingFileHandler
        root_logger = logging.getLogger()
        found_rotating_handler = False
        for handler in root_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                found_rotating_handler = True
                self.assertEqual(handler.maxBytes, 1024)
                self.assertEqual(handler.backupCount, 3)
                break

        self.assertTrue(found_rotating_handler, "RotatingFileHandler not found")


if __name__ == "__main__":
    unittest.main()
