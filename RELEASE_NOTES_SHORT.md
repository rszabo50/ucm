# UCM 1.1.0 - Docker, tmux and iTerm2 Integration, Settings Screen, and urwid 5 Support

UCM 1.1.0 adds container, tmux and iTerm2 integration, a settings screen, and support for the latest urwid and Python. **UCM is no longer published to PyPI** - install with pipx or uv from GitHub.

## 🌟 Highlights

- 🐳 **Docker container management** with container list refresh
- 🪟 **Tmux windows view** with vim-style navigation
- 🍎 **iTerm2 integration** with split-pane support for SSH and Docker connections
- ⚙️ **Settings screen** and SSH connection Add/Edit dialogs
- 🎨 **Redesigned UI layout** with context-sensitive keyboard mnemonics and `F5` layout refresh
- 🧩 **urwid 3.x and 5.x**, Python 3.10 through 3.15 (urwid 5 requires Python 3.11+); **Python 3.8 and 3.9 are no longer supported**

## ⚠️ PyPI

The `ucm` package on PyPI is stuck at 0.1.2 (2022) because the original PyPI account could not be recovered. It is out of date and no longer useful; do not install it.

## 📦 Installation

```bash
# pipx (UCM is no longer published to PyPI; the old PyPI 0.1.2 package is obsolete)
pipx install git+https://github.com/rszabo50/ucm.git

# From source
git clone https://github.com/rszabo50/ucm.git
cd ucm
pip install .

# Upgrade
pipx install --force git+https://github.com/rszabo50/ucm.git
```

## 🚀 Quick Start

```bash
ucm                              # First run creates config
vi ~/.ucm/ssh_connections.yml   # Add your connections
ucm                              # Launch UCM

# Keys:
# f  - Toggle favorite
# F  - Filter to favorites only
# r  - Sort by recently used
# L  - Connect to last server
# /  - Activate filter (vim-style)
```

## 📋 What's New

### Features
- Docker container management features
- Tmux windows view (#20) and iTerm2 terminal integration with split panes
- Settings/configuration screen (#19)
- SSH connection Add and Edit
- UI redesign with context-sensitive keyboard mnemonics; `F5` refreshes the layout

### Fixes
- Terminal resize handling and screen corruption
- Footer duplication when showing dialogs
- Logging output appearing on screen during imports
- Deprecated `urwid.raw_display` import replaced with `urwid.display.raw`

### Packaging
- Dependencies: `urwid>=3.0.0,<6.0.0`; `panwid` removed
- PyPI publishing removed; install via pipx/uv from GitHub

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

## 🙏 Acknowledgments

- Inspired by [nccm](https://github.com/flyingrhinonz/nccm)
- Built with [urwid](http://urwid.org/)

## 💬 Support

- **Issues**: https://github.com/rszabo50/ucm/issues
- **Discussions**: https://github.com/rszabo50/ucm/discussions

---

**Full Changelog**: https://github.com/rszabo50/ucm/compare/v1.0.0...v1.1.0

*Made with ❤️ for sysadmins and developers who live in the terminal*
