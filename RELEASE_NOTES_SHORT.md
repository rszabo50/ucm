# UCM 1.0.0 - Production-Ready Terminal Connection Manager

**First production release!** 🎉

UCM 1.0.0 brings powerful connection management features, a polished UX, and professional architecture to your terminal.

## 🌟 Highlights

### Connection Management
- ⭐ **Favorites** - Mark connections with `f`, filter with `F` (shows ★)
- 📊 **History Tracking** - Automatic connection history with timestamps
- 🔄 **Recent Sorting** - Press `r` to sort by recently used
- ⚡ **Quick Connect** - Press `L` to reconnect to last connection

### Enhanced UX
- 🎯 **Vim-Style Filter** - Press `/` to activate, `Esc` to deactivate
- 🎨 **Visual Feedback** - Clear `[/]` indicator when filter is active
- ⚡ **Performance** - Eliminated input lag during typing
- 🖱️ **Smart Focus** - Filter auto-deactivates on Tab/click

### Architecture & Quality
- 🏗️ **Service Layer** - Clean separation of business logic
- 📝 **Structured Logging** - JSON/text formats with rotation
- ✅ **66 Tests** - Comprehensive test coverage
- 🔄 **CI/CD** - Automated testing and releases

## 📦 Installation

```bash
# PyPI
pip install ucm

# From source
git clone https://github.com/rszabo50/ucm.git
cd ucm
pip install .

# Upgrade
pip install --upgrade ucm
```

## 🚀 Quick Start

```bash
ucm                              # First run creates config
vi ~/.ucm/ssh_connections.yml   # Add your connections
ucm                              # Launch UCM

# Try new features:
# f  - Toggle favorite
# F  - Filter to favorites only
# r  - Sort by recently used
# L  - Connect to last server
# /  - Activate filter (vim-style)
```

## 📋 What's New

### Features
- Connection history and favorites (#13, #14)
- Vim-style filter activation (#17)
- Structured logging with JSON support (#16)
- Service layer architecture (#15)
- CI/CD pipeline (#11)
- PyPI packaging ready
- Comprehensive documentation (INSTALL.md)
- Homebrew formula template

### Fixes
- Fixed accidental filter activation when using command keys
- Eliminated input lag in filter
- Auto-deactivate filter on focus change
- Proper line endings in all documentation

## 🔧 Configuration

**Logging:**
```bash
ucm --log-level DEBUG --log-format json
```

**SSH Connections:**
```yaml
# ~/.ucm/ssh_connections.yml
- name: webserver
  address: web.example.com
  user: admin
  port: 22
  identity: ~/.ssh/key.pem
  category: production
```

**History & Favorites:**
- `~/.ucm/history.yml` - Last 100 connections
- `~/.ucm/favorites.yml` - Your favorites

## 📚 Documentation

- [USER_GUIDE.md](https://github.com/rszabo50/ucm/blob/main/USER_GUIDE.md) - Complete usage guide
- [INSTALL.md](https://github.com/rszabo50/ucm/blob/main/INSTALL.md) - Platform-specific installation
- [CONTRIBUTING.md](https://github.com/rszabo50/ucm/blob/main/CONTRIBUTING.md) - How to contribute
- [PYPI_RELEASE_CHECKLIST.md](https://github.com/rszabo50/ucm/blob/main/PYPI_RELEASE_CHECKLIST.md) - Publishing workflow

## 🙏 Acknowledgments

- Inspired by [nccm](https://github.com/flyingrhinonz/nccm)
- Built with [urwid](http://urwid.org/)
- Uses [panwid](https://github.com/tonycpsu/panwid)

## 💬 Support

- **Issues**: https://github.com/rszabo50/ucm/issues
- **Discussions**: https://github.com/rszabo50/ucm/discussions

---

**Full Changelog**: https://github.com/rszabo50/ucm/compare/v0.1.2...v1.0.0

*Made with ❤️ for sysadmins and developers who live in the terminal*
