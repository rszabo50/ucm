#!/usr/bin/env python3
"""Quick test to verify Settings dialog UI."""

import sys

sys.path.insert(0, "src")

from ucm.constants import MAIN_PALETTE
from ucm.settings_manager import get_settings_manager
from ucm.SettingsDialog import SettingsDialog
from urwid import ExitMainLoop, Filler, MainLoop, Text


def test_settings_dialog():
    """Test that settings dialog can be created and displayed."""

    # Create settings manager
    sm = get_settings_manager("/tmp/test-ucm-settings")
    print("Settings manager initialized")
    print(f"  Terminal integration: {sm.get_terminal_integration()}")
    print(f"  Tmux mode: {sm.get('terminal.tmux.mode')}")
    print(f"  iTerm2 profile: {sm.get('terminal.iterm2.profile')}")

    # Create main loop
    main_widget = Filler(Text("Press 's' to open Settings\nPress 'q' to quit"))
    loop = MainLoop(main_widget, palette=MAIN_PALETTE)

    def unhandled_input(key):
        if key in ["q", "Q"]:
            raise ExitMainLoop()
        elif key in ["s", "S"]:
            print("\n's' key pressed - opening settings dialog...")
            dialog = SettingsDialog(loop=loop, palette=MAIN_PALETTE)
            dialog.show()

    loop.unhandled_input = unhandled_input

    print("\n" + "=" * 60)
    print("SETTINGS UI TEST")
    print("=" * 60)
    print("Instructions:")
    print("  - Press 's' or 'S' to open Settings dialog")
    print("  - Press 'q' or 'Q' to quit")
    print("=" * 60)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass

    print("\nSettings after close:")
    sm = get_settings_manager("/tmp/test-ucm-settings")
    print(f"  Terminal integration: {sm.get_terminal_integration()}")
    print(f"  Tmux mode: {sm.get('terminal.tmux.mode')}")


if __name__ == "__main__":
    test_settings_dialog()
