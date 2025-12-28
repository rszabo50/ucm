# Known Issues

## Panwid Deprecation Warnings with urwid 3.x

**Status**: External dependency issue
**Severity**: Low (cosmetic only)

### Description
When using urwid 3.x, you may see deprecation warnings from panwid:
```
DeprecationWarning: listbox is moved to urwid.widget.listbox
```

### Cause
The `panwid` library (last updated 2021) uses deprecated import paths that changed in urwid 3.0. Panwid's current maintainer hasn't released an update compatible with urwid 3.x.

### Impact
- **User experience**: No impact - everything works normally
- **Development**: Warnings appear during testing but don't affect functionality

### Workaround
The application automatically suppresses these warnings in `src/ucm/__main__.py`:
```python
warnings.filterwarnings("ignore", category=DeprecationWarning, module="panwid")
```

### Long-term Solutions
1. **Wait for panwid update**: Monitor https://github.com/tonycpsu/panwid for urwid 3.x support
2. **Pin urwid version**: Currently pinned to `urwid>=2.1.0,<4.0.0` for compatibility
3. **Alternative library**: Consider migrating to pure urwid widgets if panwid becomes unmaintained

### Related Links
- panwid GitHub: https://github.com/tonycpsu/panwid
- urwid 3.0 migration guide: https://urwid.org/manual/migration3.html
