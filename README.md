# **U**rwid rendered **C**onnection **M**anager (**ucm**)

[![CI](https://github.com/rszabo50/ucm/actions/workflows/ci.yml/badge.svg)](https://github.com/rszabo50/ucm/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/rszabo50/ucm/branch/main/graph/badge.svg)](https://codecov.io/gh/rszabo50/ucm)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Released under GNU GPLv3.

https://www.gnu.org/licenses/gpl-3.0.en.html

This software can be used by anyone at no cost, however, if you like using this software and can support

- please donate to any of your local charities (childrens hospitals, food banks, shelters, spca,  etc).

This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation: GNU GPLv3.
You must include this entire text with your distribution.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

## About ucm

ucm is modeled after nccm (NCurses ssh Connection Manager), but built using urwid which provides a similar interface with
added mouse support. see: https://github.com/flyingrhinonz/nccm for details.

### UCM provides:

* a simple TUI for managing and connecting to ssh endpoints
* a simple TUI for attaching to Docker Containers that are present on your system

### UCM intended users

* You have dozens or more of hosts to manage via ssh.
* Your ssh requirements (identities, ports, users etc) differ from host to host, and you want to simplify things
* You want a simple interfaces to get console access to your docker containers
* You want View all your hosts/containers at once and filter easily so that you know who to connect to.
* Have a need to use command line, don't have a GUI, or simply prefer to work more efficiently?

## UCM Configuration

Configuration is stored in `~/.ucm/ssh_connections.yml` by default.

### SSH Connections Configuration

Each SSH connection **requires**:
- `name`: Unique identifier for the connection
- `address`: IP address or hostname

**Optional fields**:
- `user`: Username for SSH (default: current user)
- `port`: TCP port (default: 22, valid range: 1-65535)
- `identity`: Path to SSH identity file
- `options`: Additional SSH command-line options
- `category`: Grouping label for filtering

### Example Configuration

```yaml
# Minimal connection
- name: webserver
  address: web.example.com

# Connection with all options
- name: production-db
  address: db.example.com
  user: admin
  port: 2222
  identity: ~/.ssh/prod-key.pem
  options: -X
  category: production
```

See `examples/ssh_connections.yml` for more examples.

### Configuration Validation

UCM automatically validates your configuration on startup and will show helpful error messages if there are issues:

```
❌ Configuration Error:
SSH connection configuration has 2 error(s):
  - Connection #1 ('server1'): Missing required field(s): address
  - Connection #2: 'port' must be between 1 and 65535, got 99999
```

### Custom Configuration Directory

You can specify a custom configuration directory:

```bash
ucm --config-dir ~/my-configs
```

## UCM UI Controls

The UI controls are quite simple, The main interactions can all be done via the mouse.

* Clicking on buttons, RadioButtons etc all work as you would expect via the mouse
* Clicking on a list will mark the row selected, and double clicking will trigger the connect action.


If your not using the mouse to control things:

* page-up, page-down will move up/down a page in the list views, and the help screen
* up/down arrows will scroll up/down one row at a time in the list views, and the help screen
