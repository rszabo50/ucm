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

import argparse
import getpass
import json
import logging
import logging.handlers
import sys
import warnings
from pathlib import Path
from typing import Any

from urwid import (
    CENTER,
    RIGHT,
    AttrWrap,
    Columns,
    ExitMainLoop,
    Filler,
    Frame,
    LineBox,
    MainLoop,
    Padding,
    RadioButton,
    Text,
    WidgetWrap,
    raw_display,
    set_encoding,
)

from ucm.constants import MAIN_PALETTE, PROGRAM_NAME, PROGRAM_VERSION, SCM_URL
from ucm.Dialogs import DialogDisplay
from ucm.DockerListView import DockerListView
from ucm.Registry import Registry
from ucm.SshListView import SshListView
from ucm.SwarmListView import SwarmListView
from ucm.TabGroup import TabGroupButton, TabGroupManager, TabGroupRadioButton
from ucm.UserConfig import UserConfig
from ucm.Widgets import Clock, Footer, Header, HelpBody, View

# Suppress panwid deprecation warnings with urwid 3.x
# See: https://github.com/tonycpsu/panwid/issues
warnings.filterwarnings("ignore", category=DeprecationWarning, module="panwid")


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class Actions:
    @staticmethod
    def show_or_exit(key):
        if key in ["q", "Q"]:
            Actions.popup_exit_dialog()
        if key in ["?"]:
            Actions.popup_help_dialog()

    @staticmethod
    def action_button_cb(_button: Any = None):
        if _button.get_label() == "Quit":
            Actions.popup_exit_dialog()
        if _button.get_label() == "Help":
            Actions.popup_help_dialog()

    @staticmethod
    def popup_exit_dialog(_button: Any = None):
        logger.error("Popping up exit dialog")
        body = Filler(Text("Are you sure you want to exit?"))
        d = DialogDisplay(
            "Confirm", 50, 10, body=body, loop=Registry().main_loop, exit_cb=Actions.exit_cb, palette=MAIN_PALETTE
        )
        d.add_buttons([("OK", 0), ("Cancel", 1)])
        d.show()

    @staticmethod
    def exit_cb(button: Any):
        if button.exitcode == 0:
            Actions.clear()
            raise ExitMainLoop()

    @staticmethod
    def clear():
        if Registry().get("main_loop") is not None:
            Registry().main_loop.widget = Filler(Text(""))
            Registry().main_loop.draw_screen()

    @staticmethod
    def popup_help_dialog(_button: Any = None):
        cols, rows = raw_display.Screen().get_cols_rows()
        d = DialogDisplay(
            "Help",
            cols - 20,
            rows - 6,
            body=HelpBody(),
            loop=Registry().main_loop,
            exit_cb=Actions.help_exit_cb,
            palette=MAIN_PALETTE,
        )
        d.add_buttons([("Cancel", 1)])
        d.show()

    @staticmethod
    def help_exit_cb(button: Any):
        pass


class Application:
    def __init__(self):
        self.header = None
        self.footer = None
        self.loop = None
        self.body = None
        self.view_holder = None
        self.views = {}
        self.filter_edit = None
        self.filter_columns = None
        self.clock = None
        self.rb_group = []
        self.frame = None
        self.tab_group_manager = TabGroupManager()

    def build(self):
        logger.debug("Building application ...")

        set_encoding("UTF-8")

        self.views["SSH"] = View(SshListView())
        if UserConfig().docker is not None:
            self.views["Docker"] = View(DockerListView())
        self.views["Swarm"] = View(SwarmListView())
        self.view_holder = WidgetWrap(self.views["SSH"])

        self.body = Padding(LineBox(self.view_holder), align=CENTER, left=1, right=2)

        view_column_array = [
            (7, AttrWrap(Text("View: "), "header", "header")),
            (
                11,
                AttrWrap(
                    TabGroupRadioButton(self.rb_group, "🐧-SSH", on_state_change=self.view_changed), "header", "header"
                ),
            ),
        ]

        if UserConfig().docker is not None:
            view_column_array.extend(
                [
                    (
                        14,
                        AttrWrap(
                            TabGroupRadioButton(self.rb_group, "🐳-Docker", on_state_change=self.view_changed),
                            "header",
                            "header",
                        ),
                    )
                ]
            )

        if UserConfig().docker is not None and UserConfig().swarm_host is not None and UserConfig().swarm_host:
            view_column_array.extend(
                [
                    (
                        14,
                        AttrWrap(
                            TabGroupRadioButton(self.rb_group, "🐳-Swarm", on_state_change=self.view_changed),
                            "header",
                            "header",
                        ),
                    )
                ]
            )

        action_button_list = [
            (8, AttrWrap(TabGroupButton("Help", on_press=Actions.action_button_cb), "button normal", "button select")),
            (8, AttrWrap(TabGroupButton("Quit", on_press=Actions.action_button_cb), "button normal", "button select")),
        ]

        view_columns = Columns(view_column_array, 1)

        action_content = Columns(action_button_list, 1)

        self.header = Header(
            name=f"{PROGRAM_NAME}:",
            release=PROGRAM_VERSION,
            left_content=view_columns,
            right_content=Text(f"{SCM_URL}", align=RIGHT),
        )

        self.clock = Clock()
        self.footer = Footer(left_content=action_content, right_content=self.clock)

        self.frame = Frame(self.body, self.header, self.footer)

        self.tab_group_manager.add("view_select", self.frame, "header", view_columns)
        self.tab_group_manager.add(
            "list", self.frame, "body", self.views["SSH"].list_view, pile=self.views["SSH"].pile, pile_pos=1
        )
        self.tab_group_manager.add("filters_select", self.frame, "body", self.views["SSH"].list_view.filter_columns)
        self.tab_group_manager.add("action_buttons", self.frame, "footer", action_content)

        Registry().main_loop = MainLoop(self.frame, palette=MAIN_PALETTE, unhandled_input=Actions.show_or_exit)
        return self

    def start(self):
        logger.debug("Starting clock ...")
        self.clock.start()
        logger.debug("Starting application loop  ...")
        Registry().main_loop.run()

    def view_changed(self, radio_button: RadioButton, state: bool):
        if state:
            view_key = radio_button.get_label().encode("ascii", "ignore").decode().strip().replace("-", "")
            logger.info(f"switching to view {view_key}")
            self.view_holder._w = self.views[view_key]
            self.view_holder._w.list_view.filters_clear()

            self.tab_group_manager.add(
                "list", self.frame, "body", self.views[view_key].list_view, pile=self.views[view_key].pile, pile_pos=1
            )
            self.tab_group_manager.add(
                "filters_select", self.frame, "body", self.views[view_key].list_view.filter_columns
            )
            Registry().main_loop.screen.clear()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="ucm",
        description=f"{PROGRAM_NAME} - Terminal UI for managing SSH and Docker connections",
        epilog=f"Version {PROGRAM_VERSION} - {SCM_URL}",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {PROGRAM_VERSION}")

    parser.add_argument(
        "--config-dir", type=str, default=None, metavar="DIR", help="Configuration directory (default: ~/.ucm)"
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-file", type=str, default=None, metavar="FILE", help="Log file path (default: /tmp/ucm-{user}.log)"
    )

    parser.add_argument(
        "--log-format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Log output format (default: text)",
    )

    parser.add_argument(
        "--log-max-bytes",
        type=int,
        default=10485760,  # 10MB
        metavar="BYTES",
        help="Maximum log file size before rotation (default: 10MB)",
    )

    parser.add_argument(
        "--log-backup-count",
        type=int,
        default=5,
        metavar="COUNT",
        help="Number of rotated log files to keep (default: 5)",
    )

    return parser.parse_args()


def setup_logging(
    log_level: str,
    log_file: str = None,
    log_format: str = "text",
    max_bytes: int = 10485760,
    backup_count: int = 5,
) -> logging.Logger:
    """Configure logging with rotation and optional JSON formatting.

    Args:
        log_level: Logging level string (DEBUG, INFO, etc.)
        log_file: Optional log file path
        log_format: Log format ('text' or 'json')
        max_bytes: Maximum log file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Returns:
        Configured logger instance
    """
    if log_file is None:
        log_file = f"/tmp/ucm-{getpass.getuser()}.log"

    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create rotating file handler
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )

    # Set formatter based on format choice
    if log_format == "json":
        formatter = JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S")
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s,%(msecs)d %(name)s {%(pathname)s:%(lineno)d} %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(handler)

    # Get UCM logger
    logger = logging.getLogger("ucm")
    logger.info(f"############# {PROGRAM_NAME} v{PROGRAM_VERSION} starting")
    logger.info(f"Log level: {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Log format: {log_format}")
    logger.info(f"Log rotation: {max_bytes} bytes, {backup_count} backups")

    return logger


def main() -> int:
    """Main entry point for UCM application.

    Returns:
        Exit code (0 for success)
    """
    try:
        args = parse_args()

        # Setup logging
        global logger
        logger = setup_logging(
            log_level=args.log_level,
            log_file=args.log_file,
            log_format=args.log_format,
            max_bytes=args.log_max_bytes,
            backup_count=args.log_backup_count,
        )

        # Override config directory if specified
        if args.config_dir:
            config_dir = Path(args.config_dir).expanduser().absolute()
            logger.info(f"Using custom config directory: {config_dir}")
            UserConfig().set("config_folder", str(config_dir))
            UserConfig().set("ssh_config_file", str(config_dir / "ssh_connections.yml"))

        # Start application
        Application().build().start()

        return 0

    except KeyboardInterrupt:
        if "logger" in globals():
            logger.info("Application interrupted by user")
        return 130
    except Exception as e:
        if "logger" in globals():
            logger.exception(f"Fatal error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

# vim: ts=4 sw=4 et
