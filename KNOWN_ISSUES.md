# Known Issues

## urwid 3.x Migration

**Status**: Resolved in current codebase
**Severity**: Historical

### Summary
Older releases depended on `panwid` for a scrolling list wrapper. That dependency imported removed private `urwid` modules and blocked `urwid` 3.x at import time.

### Resolution
UCM now uses native `urwid.ListBox`-based wrappers in `src/ucm/Widgets.py` and no longer depends on `panwid`. The package requirement is now `urwid>=3,<4`.

### Verification
- Local test suite passes on Python 3.14.3 with `urwid 3.0.5`
- CI is configured to include Python 3.14

### Related Links
- urwid migration guide: https://urwid.org/manual/migration3.html
