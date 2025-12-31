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

# Disable all logging until we configure it properly
# This prevents default lastResort handler from outputting to stderr during imports
logging.disable(logging.CRITICAL)

from urwid import (  # noqa: E402
    CENTER,
    AttrWrap,
    Columns,
    ExitMainLoop,
    Filler,
    Frame,
    LineBox,
    MainLoop,
    Padding,
    Pile,
    RadioButton,
    Text,
    WidgetWrap,
    raw_display,
    set_encoding,
)

from ucm.constants import MAIN_PALETTE, PROGRAM_NAME, PROGRAM_VERSION, SCM_URL  # noqa: E402
from ucm.Dialogs import DialogDisplay  # noqa: E402
from ucm.DockerListView import DockerListView  # noqa: E402
from ucm.Registry import Registry  # noqa: E402
from ucm.services import TmuxService  # noqa: E402
from ucm.SettingsDialog import SettingsDialog  # noqa: E402
from ucm.SshListView import SshListView  # noqa: E402
from ucm.SwarmListView import SwarmListView  # noqa: E402
from ucm.TabGroup import TabGroupButton, TabGroupManager, TabGroupRadioButton  # noqa: E402
from ucm.TmuxListView import TmuxListView  # noqa: E402
from ucm.UserConfig import UserConfig  # noqa: E402
from ucm.Widgets import Footer, Header, HelpBody, KeyboardMnemonics, TabBar, View  # noqa: E402

# Suppress panwid deprecation warnings with urwid 3.x
# See: https://github.com/tonycpsu/panwid/issues
warnings.filterwarnings("ignore", category=DeprecationWarning, module="panwid")

# Suppress urwid layout warnings from our DynamicHeightBox flow/box widget wrapper
# These are expected due to our custom dynamic sizing implementation
warnings.filterwarnings("ignore", message=".*Unusual widget.*sizing.*")
warnings.filterwarnings("ignore", message=".*BOX widgets not marked.*")
warnings.filterwarnings("ignore", module="urwid.widget.pile")
warnings.filterwarnings("ignore", module="urwid.widget.widget")


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
            return
        if key in ["?"]:
            Actions.popup_help_dialog()
            return
        if key in ["s", "S"]:
            Actions.popup_settings_dialog()
            return

    @staticmethod
    def action_button_cb(_button: Any = None):
        label = _button.get_label()
        if "Quit" in label:
            Actions.popup_exit_dialog()
        if "Help" in label:
            Actions.popup_help_dialog()
        if "Settings" in label:
            Actions.popup_settings_dialog()

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

    @staticmethod
    def popup_settings_dialog(_button: Any = None):
        """Show settings dialog."""
        logger.info("Opening settings dialog")
        settings_dialog = SettingsDialog(loop=Registry().main_loop, palette=MAIN_PALETTE)
        settings_dialog.show()


class Application:
    def __init__(self):
        self.header = None
        self.tab_bar = None
        self.footer = None
        self.keyboard_mnemonics = None
        self.loop = None
        self.body = None
        self.view_holder = None
        self.views = {}
        self.filter_edit = None
        self.filter_columns = None
        self.rb_group = []
        self.frame = None
        self.tab_group_manager = TabGroupManager()

    def build(self):
        logger.debug("Building application ...")

        set_encoding("UTF-8")

        # Create views
        self.views["SSH"] = View(SshListView())
        if UserConfig().docker is not None:
            self.views["Docker"] = View(DockerListView())
        if TmuxService.is_inside_tmux():
            self.views["Tmux"] = View(TmuxListView())
        if UserConfig().docker is not None and UserConfig().swarm_host:
            self.views["Swarm"] = View(SwarmListView())
        self.view_holder = WidgetWrap(self.views["SSH"])

        self.body = Padding(LineBox(self.view_holder), align=CENTER, left=1, right=2)

        # Create simplified header
        self.header = Header(
            name=f"{PROGRAM_NAME}:",
            release=PROGRAM_VERSION,
            url=SCM_URL,
        )

        # Build view tabs for TabBar
        view_tabs = [
            (
                11,
                AttrWrap(
                    TabGroupRadioButton(self.rb_group, "🐧-SSH", on_state_change=self.view_changed), "header", "header"
                ),
            ),
        ]

        if UserConfig().docker is not None:
            view_tabs.append(
                (
                    14,
                    AttrWrap(
                        TabGroupRadioButton(self.rb_group, "🐳-Docker", on_state_change=self.view_changed),
                        "header",
                        "header",
                    ),
                )
            )

        if TmuxService.is_inside_tmux():
            view_tabs.append(
                (
                    13,
                    AttrWrap(
                        TabGroupRadioButton(self.rb_group, "📟-Tmux", on_state_change=self.view_changed),
                        "header",
                        "header",
                    ),
                )
            )

        if UserConfig().docker is not None and UserConfig().swarm_host:
            view_tabs.append(
                (
                    14,
                    AttrWrap(
                        TabGroupRadioButton(self.rb_group, "🐳-Swarm", on_state_change=self.view_changed),
                        "header",
                        "header",
                    ),
                )
            )

        self.tab_bar = TabBar(tabs=view_tabs)

        # Create action buttons with keyboard shortcuts
        action_button_list = [
            (
                12,
                AttrWrap(
                    TabGroupButton("Help (?)", on_press=Actions.action_button_cb), "button normal", "button select"
                ),
            ),
            (
                16,
                AttrWrap(
                    TabGroupButton("Settings (s)", on_press=Actions.action_button_cb), "button normal", "button select"
                ),
            ),
            (
                12,
                AttrWrap(
                    TabGroupButton("Quit (q)", on_press=Actions.action_button_cb), "button normal", "button select"
                ),
            ),
        ]
        action_content = Columns(action_button_list, 1)

        # Create keyboard mnemonics - will be updated dynamically
        self.keyboard_mnemonics = KeyboardMnemonics(mnemonics="/ Filter")

        # Create footer with mnemonics above buttons
        footer_content = Pile([("pack", self.keyboard_mnemonics), ("pack", action_content)])
        self.footer = Footer(content=footer_content)

        # Create frame with header pile (header + tab_bar)
        header_pile = Pile([("pack", self.header), ("pack", self.tab_bar)])
        self.frame = Frame(self.body, header_pile, self.footer)

        # Register tab groups
        self.tab_group_manager.add("view_select", self.frame, "header", self.tab_bar)
        self.tab_group_manager.add(
            "list", self.frame, "body", self.views["SSH"].list_view, pile=self.views["SSH"].pile, pile_pos=1
        )
        self.tab_group_manager.add("filters_select", self.frame, "body", self.views["SSH"].list_view.filter_columns)
        self.tab_group_manager.add("action_buttons", self.frame, "footer", action_content)

        Registry().main_loop = MainLoop(self.frame, palette=MAIN_PALETTE, unhandled_input=Actions.show_or_exit)
        return self

    def update_mnemonics(self, view_name: str = "SSH", has_selection: bool = True):
        """Update keyboard mnemonics based on current context.

        Args:
            view_name: Current view name (SSH, Docker, Tmux, Swarm)
            has_selection: Whether a list item is currently selected
        """
        # Always show filter
        mnemonics = ["/=Filter"]

        if has_selection:
            # Universal shortcuts when item is selected
            mnemonics.extend(["c=Connect", "i=Info"])

            # iTerm2 split shortcuts if enabled
            from ucm.services.iterm2_service import ITerm2Service
            from ucm.settings_manager import get_settings_manager

            settings = get_settings_manager()
            terminal_integration = settings.get("terminal.integration", "none")
            if terminal_integration == "iterm2" and ITerm2Service.is_iterm2_available():
                mnemonics.extend(["|=VSplit", "-=HSplit"])

            # SSH-specific shortcuts
            if view_name == "SSH":
                mnemonics.extend(["+=Add", "E=Edit", "f=Fav", "F=ShowFavs", "r=Recent", "L=Last"])
            # Docker-specific shortcuts
            elif view_name == "Docker":
                mnemonics.extend(["l=Logs", "S=Stop", "s=Start", "R=Restart", "D=Remove", "a=ToggleAll"])
        else:
            # No selection - still show Add for SSH view
            if view_name == "SSH":
                mnemonics.append("+=Add")
            # Docker toggle always available
            elif view_name == "Docker":
                mnemonics.append("a=ToggleAll")

        self.keyboard_mnemonics.set_mnemonics("  ".join(mnemonics))

    def start(self):
        logger.debug("Starting application loop ...")
        # Store application instance in registry for mnemonics updates
        Registry().app = self
        # Set initial mnemonics for SSH view - check if there's actually a selection
        has_selection = False
        if "SSH" in self.views:
            ssh_list_view = self.views["SSH"].list_view
            if hasattr(ssh_list_view, "walker") and len(ssh_list_view.walker) > 0:
                try:
                    focus_widget, focus_pos = ssh_list_view.walker.get_focus()
                    has_selection = focus_widget is not None
                except (IndexError, TypeError):
                    has_selection = False
        self.update_mnemonics("SSH", has_selection)
        Registry().main_loop.run()

    def view_changed(self, radio_button: RadioButton, state: bool):
        if state:
            view_key = radio_button.get_label().encode("ascii", "ignore").decode().strip().replace("-", "")
            logger.info(f"switching to view {view_key}")
            self.view_holder._w = self.views[view_key]
            # Deactivate filter and clear filter text when switching views
            if hasattr(self.view_holder._w.list_view, "deactivate_filter"):
                self.view_holder._w.list_view.deactivate_filter()
            self.view_holder._w.list_view.filters_clear()

            self.tab_group_manager.add(
                "list", self.frame, "body", self.views[view_key].list_view, pile=self.views[view_key].pile, pile_pos=1
            )
            self.tab_group_manager.add(
                "filters_select", self.frame, "body", self.views[view_key].list_view.filter_columns
            )
            # Update mnemonics for the new view - check if there's actually a selection
            has_selection = False
            list_view = self.views[view_key].list_view
            if hasattr(list_view, "walker") and len(list_view.walker) > 0:
                try:
                    focus_widget, focus_pos = list_view.walker.get_focus()
                    has_selection = focus_widget is not None
                except (IndexError, TypeError):
                    has_selection = False
            self.update_mnemonics(view_key, has_selection)
            # Force complete screen redraw when switching views
            Registry().main_loop.screen.clear()
            Registry().main_loop.draw_screen()


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

    # Remove any existing handlers (prevents output to stdout/stderr)
    root_logger.handlers.clear()

    # Add only our file handler
    root_logger.addHandler(handler)

    # Re-enable logging now that handlers are configured
    logging.disable(logging.NOTSET)

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
        # Error is logged to file, not printed to stderr
        return 1


if __name__ == "__main__":
    sys.exit(main())

# vim: ts=4 sw=4 et
