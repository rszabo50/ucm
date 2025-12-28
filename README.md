# **U**rwid rendered **C**onnection **M**anager (**ucm**)

[![CI](https://github.com/rszabo50/ucm/actions/workflows/ci.yml/badge.svg)](https://github.com/rszabo50/ucm/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/rszabo50/ucm/branch/main/graph/badge.svg)](https://codecov.io/gh/rszabo50/ucm)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A terminal-based connection manager for SSH and Docker with a powerful, mouse-friendly interface.

> **Note**: UCM is inspired by [nccm](https://github.com/flyingrhinonz/nccm) but built with [urwid](http://urwid.org/) for enhanced mouse support and a modern terminal UI.

## ✨ Features

- 🖥️ **SSH Connection Management** - Organize and connect to SSH hosts with ease
- 🐳 **Docker Container Access** - Quick console access to running containers
- 🔍 **Real-time Filtering** - Instantly search through hundreds of connections
- 🖱️ **Mouse Support** - Full mouse and keyboard navigation
- ⚙️ **Configuration Validation** - Automatic config checking with helpful error messages
- 📝 **Flexible Config** - Simple YAML configuration with sensible defaults
- 🎨 **Clean TUI** - Beautiful terminal interface powered by urwid

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/rszabo50/ucm.git
cd ucm
pip install -e .

# Run UCM
ucm
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

## 🎮 Usage

### Keyboard Shortcuts

#### Navigation
- `↑`/`↓` or `j`/`k` - Move up/down in lists
- `Page Up`/`Page Down` - Page through lists
- `Tab` - Cycle between UI elements
- `Enter` - Connect to selected host/container

#### Actions
- `c` - Connect to selected Docker container (Docker view)
- `i` - Inspect Docker container (Docker view)
- `q` - Quit UCM
- `?` - Show help

#### Filtering
- Type in the filter box to search connections in real-time
- Filter works on name, address, user, and category fields

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

**Swarm View** - Docker Swarm (if configured)
- Manage swarm services and containers

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
