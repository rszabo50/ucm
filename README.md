# 🚀 UCM - Urwid Connection Manager

[![PyPI](https://img.shields.io/pypi/v/ucm)](https://pypi.org/project/ucm/)
[![CI](https://github.com/rszabo50/ucm/actions/workflows/ci.yml/badge.svg)](https://github.com/rszabo50/ucm/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/rszabo50/ucm/branch/main/graph/badge.svg)](https://codecov.io/gh/rszabo50/ucm)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**A powerful terminal UI for managing SSH and Docker connections** - Built for system administrators and developers who live in the terminal.

### ⚡ Quick Example

**Before UCM:** 30 seconds to find and connect
```bash
vim ~/.ssh/config  # Search for the right server
ssh prod-web-server-03-us-east-1.example.com  # Type exact name
```

**With UCM:** 3 seconds
```bash
ucm
# Press '/' → Type 'prod web' → Press Enter → Connected! 🎉
```

> **Inspired by** [nccm](https://github.com/flyingrhinonz/nccm), **built with** [urwid](http://urwid.org/) for a modern terminal experience

## 🎯 Perfect For

**System Administrators** managing infrastructure:
- Corporate networks with 50+ servers
- Multi-datacenter deployments
- Jump host / bastion workflows
- Connection audit trails

**DevOps Engineers** in cloud environments:
- AWS, GCP, Azure instances (100+)
- Kubernetes node access
- Microservices debugging
- Quick incident response

**Developers** working across environments:
- Production / staging / dev servers
- Database server management
- Docker container debugging
- Remote development environments

## Why UCM?

### vs SSH Config Aliases
| Feature | ~/.ssh/config | UCM |
|---------|---------------|-----|
| Visual interface | ❌ | ✅ |
| Fuzzy search | ❌ | ✅ |
| Favorites | ❌ | ✅ ⭐ |
| History tracking | ❌ | ✅ |
| One-key reconnect | ❌ | ✅ `L` key |
| Docker support | ❌ | ✅ |
| Mouse support | ❌ | ✅ |
| Connection stats | ❌ | ✅ |

### Time Savings
- **Average connection time**: 30s → 3s (90% faster)
- **Daily connections**: 50 × 27s saved = **22 minutes/day**
- **Monthly savings**: ~8 hours (1 work day!)

## ✨ Features

- ⭐ **One-key Favorites** - Mark servers with `f`, filter with `F` (shows ★)
- ⚡ **Quick Reconnect** - Press `L` to connect to your last server
- 🔍 **Vim-style Search** - Press `/` to filter, prevents accidental text entry
- 📊 **Connection History** - Auto-tracked with timestamps, sort by recent with `r`
- 🖥️ **SSH Management** - Organize hundreds of hosts with ease
- 🐳 **Docker Integration** - SSH and containers in one place
- 🪟 **Terminal Integration** - Keep UCM open with tmux/iTerm2, no more Ctrl+b sequences
- ⌨️ **Keyboard-first** - Full vim navigation (j/k, /, Esc)
- 🖱️ **Mouse Support** - Click and double-click workflows
- ⚙️ **Config Validation** - Automatic checking with helpful errors
- 📝 **YAML Config** - Simple, readable connection definitions
- 🎨 **Clean TUI** - Beautiful urwid interface

## 🚀 Quick Start

### Installation

**Option 1: Install from PyPI (Recommended)**

```bash
pip install ucm
```

**Option 2: Install from Homebrew (macOS/Linux)**

```bash
# Coming soon
brew install ucm
```

**Option 3: Install from Source**

```bash
git clone https://github.com/rszabo50/ucm.git
cd ucm
pip install -e .
```

**Run UCM:**

```bash
ucm
```

### Upgrading

**PyPI:**
```bash
pip install --upgrade ucm
```

**Source:**
```bash
cd ucm
git pull
pip install -e .
```

### First Run

On first launch, UCM will create a default configuration at `~/.ucm/ssh_connections.yml`:

```bash
ucm
```

Edit the configuration file to add your SSH connections:

```bash
# Edit with your favorite editor
vi ~/.ucm/ssh_connections.yml
```

### Quick Example

```yaml
# ~/.ucm/ssh_connections.yml
- name: webserver
  address: web.example.com

- name: database
  address: db.example.com
  user: admin
  port: 2222
  identity: ~/.ssh/db-key.pem
```

Launch UCM and start connecting!

## 📖 Documentation

- **[User Guide](USER_GUIDE.md)** - Comprehensive usage documentation
- **[Development Guide](DEVELOPMENT.md)** - Contributing and development setup
- **[Contributing](CONTRIBUTING.md)** - How to contribute to UCM

## 🎯 Use Cases

UCM is perfect if you:

- ✅ Manage dozens (or hundreds!) of SSH hosts
- ✅ Have different SSH requirements per host (identities, ports, users)
- ✅ Need quick console access to Docker containers
- ✅ Want to filter and view all connections at once
- ✅ Prefer efficient command-line workflows
- ✅ Work in environments without a GUI
- ✅ Use tmux or iTerm2 and want better window management
- ✅ Make frequent successive connections to different servers

## ⚙️ Configuration

### SSH Connections

Configuration is stored in `~/.ucm/ssh_connections.yml` by default.

**Required fields:**
- `name`: Unique identifier
- `address`: IP or hostname

**Optional fields:**
- `user`: SSH username (default: current user)
- `port`: TCP port (default: 22, range: 1-65535)
- `identity`: Path to SSH key file
- `options`: Additional SSH options
- `category`: Grouping label

### Example Configuration

```yaml
# Minimal connection
- name: webserver
  address: web.example.com

# Full configuration
- name: production-db
  address: db.example.com
  user: admin
  port: 2222
  identity: ~/.ssh/prod-key.pem
  options: -X
  category: production

# Using SSH config defaults
- name: jumphost
  address: jump.example.com
  # UCM respects ~/.ssh/config for additional settings
```

See [`examples/ssh_connections.yml`](examples/ssh_connections.yml) for more examples.

### Connection History and Favorites

UCM automatically tracks your SSH connection usage and allows you to mark favorites.

**Features:**
- ⭐ **Favorites** - Press `f` to toggle favorite status (marked with ★)
- 🔍 **Favorites Filter** - Press `F` to show only favorite connections
- 📅 **Recently Used Sorting** - Press `r` to sort connections by last used
- ⚡ **Quick Connect** - Press `L` to instantly connect to your last used connection
- 📊 **Usage Tracking** - Automatically records connection timestamps and use counts
- 💾 **Persistence** - History and favorites saved to `~/.ucm/history.yml` and `~/.ucm/favorites.yml`
- 📈 **Statistics** - Track most-used connections and usage patterns

**Benefits:**
- Quickly identify frequently-used servers
- Mark critical servers as favorites for easy identification
- Sort and filter connections by usage patterns
- Instant access to your last used connection
- Track connection patterns across your infrastructure

### Configuration Validation

UCM automatically validates your configuration and provides helpful error messages:

```
❌ Configuration Error:
SSH connection configuration has 2 error(s):
  - Connection #1 ('server1'): Missing required field(s): address
  - Connection #2: 'port' must be between 1 and 65535, got 99999
```

### Custom Configuration Directory

```bash
# Use custom config location
ucm --config-dir ~/my-configs

# Different log level
ucm --log-level DEBUG

# Custom log file
ucm --log-file /var/log/ucm.log
```

## ⌨️ Keyboard Shortcuts Quick Reference

```
┌─ Navigation ──────────────────┬─ Power Features ──────────────┐
│ ↑/k        Move up            │ f          Toggle favorite ★  │
│ ↓/j        Move down          │ F          Show favorites     │
│ PgUp/PgDn  Page up/down       │ r          Sort by recent     │
│ Tab        Next UI element    │ L          Last connection    │
│ Enter/c    Connect            │ /          Activate filter    │
│ q          Quit               │ Esc        Deactivate filter  │
│ ?          Help               │ ,          Settings           │
│                               │ i          Info/Inspect       │
└───────────────────────────────┴───────────────────────────────┘
```

### Filter Search
- **Press `/`** to activate vim-style filter (shows `[/]` indicator)
- **Type** to search across name, address, user, category
- **Esc** or **Tab** to deactivate and return to list
- Prevents accidental text entry when using command keys

### Mouse Controls

- **Click** - Select a connection
- **Double-click** - Connect immediately
- **Click buttons** - Activate buttons (Help, Quit, etc.)
- **Click radio buttons** - Switch views (SSH, Docker, Swarm)
- **Scroll wheel** - Scroll through lists

### Views

**SSH View** - Manage SSH connections
- Lists all configured SSH hosts
- Filter by any field
- Double-click or Enter to connect

**Docker View** - Container management
- Shows running Docker containers
- Press `c` to connect to a container
- Press `i` to inspect container details

**Tmux View** - Navigate tmux windows (only visible inside tmux)
- Shows all tmux windows with names
- Switch windows without `Ctrl+b` sequences
- Close windows with `x` key
- Refresh list with `r` key

**Swarm View** - Docker Swarm (if configured)
- Manage swarm services and containers

## 💪 Power User Tips

### Quick Aliases
```bash
# Add to .bashrc or .zshrc
alias ucm-last='ucm && L'               # Launch and connect to last
alias ucm-prod='ucm --config-dir ~/.ucm-prod'   # Separate prod config
alias ssh-fav='ucm'                     # Quick favorite access (press F)
```

### Category-Based Organization
```yaml
# Organize by environment, role, or datacenter
- name: prod-web-01
  category: production

- name: staging-api-01
  category: staging
```
Filter by typing the category name!

### Jump Host / Bastion Workflow
```yaml
# UCM respects SSH ProxyJump
- name: internal-server
  address: 10.0.1.50
  user: admin
  options: -J bastion.example.com
```

### Structured Logging for SIEM
```bash
# JSON logs for log aggregation/SIEM
ucm --log-format json --log-file /var/log/ucm.log
```

## 🔧 Command-Line Options

```bash
ucm --help
```

**Available options:**

```
--version              Show version and exit
--config-dir DIR       Custom configuration directory (default: ~/.ucm)
--log-level LEVEL      Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
--log-file FILE        Custom log file path (default: /tmp/ucm-{user}.log)
--log-format FORMAT    Log output format: text, json (default: text)
--log-max-bytes BYTES  Maximum log file size before rotation (default: 10MB)
--log-backup-count N   Number of rotated log files to keep (default: 5)
```

**Examples:**

```bash
# Show version
ucm --version

# Debug mode with verbose logging
ucm --log-level DEBUG

# Use alternative config
ucm --config-dir ~/.config/ucm-work

# Save logs to specific file
ucm --log-file ~/logs/ucm.log

# JSON logging for log aggregation tools
ucm --log-format json

# Custom log rotation settings (1MB files, keep 10 backups)
ucm --log-max-bytes 1048576 --log-backup-count 10

# Full logging example: JSON format with debug level
ucm --log-level DEBUG --log-format json --log-file /var/log/ucm.log
```

## 🐳 Docker Integration

UCM automatically detects running Docker containers if Docker is installed.

### Requirements

- Docker installed and accessible
- User has permission to run `docker ps`

### Docker Commands

- `docker ps` - List containers (used by UCM)
- `docker exec -it <container> bash` - Connect to container (UCM executes this)
- `docker inspect <container>` - View container details

## 🪟 Terminal Integration

**Keep UCM running and eliminate manual window switching!** UCM integrates with tmux and iTerm2 to launch connections in new windows/tabs while keeping the UCM interface open for your next connection.

### Supported Terminals

**tmux (Linux/macOS)**
- Launch SSH/Docker connections in new tmux windows
- Navigate tmux windows with UCM's Tmux View (no more `Ctrl+b` sequences!)
- Auto-configured `Ctrl+b u` keybinding to return to UCM
- Automatic screen refresh when switching back

**iTerm2 (macOS)**
- Launch connections in new iTerm2 tabs
- UCM stays open in the original tab
- Use `Cmd+1`, `Cmd+2`, etc. to switch between tabs
- Configurable iTerm2 profiles for connections

### Getting Started

**1. Enable Terminal Integration**
```bash
ucm
# Press ',' to open Settings
# Select "Tmux" or "iTerm2" integration
# Save settings
```

**2. Using tmux Integration**
```bash
# Start or attach to tmux session
tmux

# Launch UCM
ucm

# Connect to a server - opens in new tmux window
# Press Ctrl+b u from anywhere to return to UCM
# Or use the Tmux View tab to see all windows and navigate
```

**3. Using iTerm2 Integration (macOS)**
```bash
# Launch UCM in iTerm2
ucm

# Enable iTerm2 in Settings (press ',')
# Connect to a server - opens in new tab
# Use Cmd+1 to return to UCM tab
# Cmd+2, Cmd+3, etc. for your connection tabs
```

### Benefits

- **No more exit/restart cycles** - UCM stays open for rapid successive connections
- **Visual window management** - Tmux View shows all your connections at once
- **No memorization** - Navigate tmux without remembering `Ctrl+b` sequences
- **Faster workflows** - Jump between servers without returning to command line
- **Better multitasking** - Work in multiple servers simultaneously

### Settings

Press `,` (comma) in UCM to configure terminal integration:

**Tmux Settings:**
- Auto-name windows with connection info (🐧 for SSH, 🐳 for Docker)
- Only window mode supported (each connection in separate window)

**iTerm2 Settings:**
- Specify iTerm2 profile for connections
- Only new tab mode supported (each connection in separate tab)

## 🛠️ Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development setup, testing, and contribution guidelines.

### Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/rszabo50/ucm.git
cd ucm

# Install development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Format code
ruff format src/ tests/
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute:**
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📄 License

Released under GNU GPLv3.

https://www.gnu.org/licenses/gpl-3.0.en.html

This software can be used by anyone at no cost. However, if you find it useful and can support:
- **Please donate to your local charities** (children's hospitals, food banks, shelters, SPCA, etc.)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation: GNU GPLv3.

This program is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

## 🙏 Acknowledgments

- Inspired by [nccm](https://github.com/flyingrhinonz/nccm) - NCurses ssh Connection Manager
- Built with [urwid](http://urwid.org/) - Console user interface library
- Uses [panwid](https://github.com/tonycpsu/panwid) - Additional urwid widgets

## 📞 Support

- **Issues**: https://github.com/rszabo50/ucm/issues
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: See [USER_GUIDE.md](USER_GUIDE.md) for detailed usage

---

**Made with ❤️ for sysadmins and developers who live in the terminal**
