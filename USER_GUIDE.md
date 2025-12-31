# UCM User Guide

Complete guide to using UCM (Urwid Connection Manager) for SSH and Docker container management.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [SSH Connection Management](#ssh-connection-management)
- [Docker Container Management](#docker-container-management)
- [Keyboard Shortcuts Reference](#keyboard-shortcuts-reference)
- [Common Workflows](#common-workflows)
- [Tips and Tricks](#tips-and-tricks)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/rszabo50/ucm.git
cd ucm

# Install UCM
pip install -e .
```

### First Launch

When you first run UCM, it will create a default configuration directory:

```bash
ucm
```

This creates:
- `~/.ucm/` - Configuration directory
- `~/.ucm/ssh_connections.yml` - SSH connections file
- `/tmp/ucm-{user}.log` - Log file

### Initial Configuration

Edit your SSH connections file:

```bash
vi ~/.ucm/ssh_connections.yml
```

Add your first connection:

```yaml
- name: my-server
  address: example.com
```

Save and relaunch UCM to see your connection!

## Interface Overview

```
┌────────────────────────────────────────────────────────────┐
│ UCM: 0.1.2              View: ◉ SSH  ○ Docker  ○ Swarm    │ ← Header
├────────────────────────────────────────────────────────────┤
│   # ContainerId  Name          Image                       │ ← Column Headers
│   0 abc123def    web-app       nginx:latest                │
│   1 xyz789ghi    database      postgres:14                 │ ← Connection List
│   2 jkl456mno    cache         redis:7                     │
│                                                             │
├────────────────────────────────────────────────────────────┤
│ Filter Text: [________________]                            │ ← Filter Bar
├────────────────────────────────────────────────────────────┤
│ [ Help ] [ Quit ]                          HH:MM:SS        │ ← Footer
└────────────────────────────────────────────────────────────┘
```

### UI Components

**Header** - Shows program name, version, and GitHub URL
**Tab Bar** - View selector tabs (SSH, Docker, Tmux, Swarm)
**Connection List** - Scrollable list of connections/containers
**Filter Bar** - Real-time search filter with status indicators
**Keyboard Mnemonics** - Context-sensitive keyboard shortcuts
**Footer** - Action buttons (Help, Settings, Quit)

### View Modes

- **SSH View** - Manage SSH connections from your config file
- **Docker View** - List and connect to running Docker containers
- **Swarm View** - Docker Swarm services (if configured)

## SSH Connection Management

### Adding SSH Connections

**Method 1: Using UCM Interface (Recommended)**

Press `+` in the SSH view to open the Add Connection dialog. This provides a guided form with validation and automatically saves to your configuration file.

**Method 2: Manual Configuration**

Edit `~/.ucm/ssh_connections.yml`:

```yaml
# Basic connection
- name: webserver
  address: 192.168.1.100

# Connection with user
- name: database
  address: db.example.com
  user: admin

# Full configuration
- name: production
  address: prod.example.com
  user: deploy
  port: 2222
  identity: ~/.ssh/prod-key.pem
  options: -X
  category: production
```

### Field Reference

**Required:**
- `name` - Unique identifier for the connection
- `address` - Hostname or IP address

**Optional:**
- `user` - SSH username (default: current user)
- `port` - SSH port (default: 22)
- `identity` - Path to SSH private key
- `options` - Additional SSH command-line options
- `category` - Group label for filtering

### Editing SSH Connections

**Method 1: Using UCM Interface (Recommended)**

1. Select a connection in the SSH view
2. Press `E` to open the Edit Connection dialog
3. Modify any fields (all fields are editable)
4. Press **Save** to update the configuration file

**Method 2: Manual Edit**

Manually edit `~/.ucm/ssh_connections.yml` and reload UCM.

**Note:** When editing via the UI, you can change the connection name or address. UCM tracks the original connection to ensure the correct entry is updated.

### Connecting to a Host

**Method 1: Mouse**
1. Click on the connection to select it
2. Double-click to connect

**Method 2: Keyboard**
1. Use ↑/↓ or j/k to navigate
2. Press Enter to connect

**Method 3: Filter + Connect**
1. Type in filter box to find host
2. Press Enter when filtered to one result

### SSH Connection Options

UCM respects your `~/.ssh/config` file. You can set default options there:

```bash
# ~/.ssh/config
Host 192.168.*
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    IdentityFile ~/.ssh/my-key.pem

Host *.example.com
    User admin
    Port 2222
```

Then in UCM, you only need:

```yaml
- name: server1
  address: 192.168.1.100
  # Other options come from ~/.ssh/config!
```

### Categories and Organization

Use categories to group connections:

```yaml
- name: web1
  address: web1.prod.com
  category: production

- name: web2
  address: web2.prod.com
  category: production

- name: dev-server
  address: dev.example.com
  category: development
```

Filter by category in the filter box: type "production" to see only production servers.

## Docker Container Management

### Requirements

- Docker installed and running
- User has permission to run Docker commands

### Switching to Docker View

**Mouse:** Click the "Docker" radio button in the header
**Keyboard:** Use Tab to cycle to view selector, then arrow keys

### Container List

The Docker view shows:
- Container ID (short)
- Container Name
- Image Name
- Status (when showing all containers)

**Default View:** Running containers only
**Show All View:** Press `a` to toggle between running and all containers (including stopped)

When showing all containers:
- Running containers are marked with ●
- Stopped containers are marked with ○
- `[ALL]` indicator appears in the filter bar

### Connecting to a Container

UCM attempts to connect with `bash`, falling back to `sh` if bash isn't available.

**Method 1: Double-click** on a container

**Method 2: Select and press `c`**
1. Navigate to container with ↑/↓
2. Press `c` to connect

**Method 3: Enter key**
1. Navigate to container
2. Press Enter

### Viewing Container Logs

Press `l` while a container is selected to open the log viewer:

**Log Viewer Features:**
- Starts with last 100 lines
- Live streaming with auto-scroll
- **Pause/Resume** button: Pause log streaming to review, then resume
- **Line Count Control:** Change number of lines to display (updates stream)
- **Apply** button: Restart stream with new line count
- Scrollable display

**Example Workflow:**
1. Select a container
2. Press `l` to view logs
3. Review the initial 100 lines
4. Press **Pause** to stop scrolling and review carefully
5. Change line count to 500 and press **Apply** for more context
6. Press **Resume** to continue live streaming
7. Press **Close** when done

### Container Lifecycle Management

**Stop Container** (`S` key)
- Stops a running container
- 10 second timeout before force kill
- Shows success/failure message
- Auto-refreshes container list

**Start Container** (`s` key)
- Starts a stopped container
- Only works when showing all containers
- Shows success/failure message
- Auto-refreshes container list

**Restart Container** (`R` key)
- Restarts a container (stop + start)
- 10 second timeout before force kill
- Shows success/failure message
- Auto-refreshes container list

**Remove Container** (`D` key)
- Shows confirmation dialog before removing
- Container must be stopped first
- Cannot be undone
- Shows success/failure message
- Auto-refreshes container list

**Example Workflow:**
1. Press `a` to show all containers
2. Select a stopped container (marked with ○)
3. Press `D` to remove it
4. Confirm removal in dialog
5. Container is removed and list refreshes

### Inspecting Containers

Press `i` while a container is selected to view detailed information:

```
Container Inspection: web-app
──────────────────────────────────
{
  "Id": "abc123def...",
  "Name": "/web-app",
  "Image": "nginx:latest",
  "State": {
    "Running": true,
    ...
  }
}
```

### Docker View Shortcuts

| Key | Action | Notes |
|-----|--------|-------|
| `c` or `Enter` | Connect to container | Opens bash/sh shell |
| `i` | Inspect container | Show detailed info |
| `l` | View logs | Live log viewer with pause/resume |
| `S` | Stop container | Stops running container |
| `s` | Start container | Starts stopped container |
| `R` | Restart container | Stop + start |
| `D` | Remove container | Requires confirmation |
| `a` | Toggle show all | Running only ↔ All containers |
| `/` | Activate filter | Filter by ID, name, image, status |

## Keyboard Shortcuts Reference

**Context-Sensitive Shortcuts:** UCM displays available shortcuts in the footer based on the current view and whether an item is selected. This helps you discover relevant commands without memorizing all shortcuts.

### Global Shortcuts (All Views)

| Key | Action |
|-----|--------|
| `q` | Quit UCM |
| `?` | Show help dialog |
| `s` | Show settings dialog |
| `Tab` | Cycle between UI elements |
| `Esc` | Close dialogs / Deactivate filter |

### Navigation

| Key | Action |
|-----|--------|
| `↑` or `k` | Move up one row |
| `↓` or `j` | Move down one row |
| `Page Up` | Scroll up one page |
| `Page Down` | Scroll down one page |
| `Home` | Jump to first item |
| `End` | Jump to last item |

### Filtering

| Key | Action |
|-----|--------|
| `/` | Activate filter mode |
| Type text | Filter connections in real-time |
| `Backspace` | Remove filter characters |
| `Ctrl+U` | Clear entire filter |
| `Esc` or `Tab` | Deactivate filter mode |

### Connection Actions

| Key | Action | View | Notes |
|-----|--------|------|-------|
| `Enter` or `c` | Connect to selected item | All | Only shown when item selected |
| `i` | Inspect/Info | All | Only shown when item selected |
| `\|` | Connect in vertical split | SSH/Docker | Only shown with iTerm2 enabled |
| `-` | Connect in horizontal split | SSH/Docker | Only shown with iTerm2 enabled |

### SSH-Specific Shortcuts

| Key | Action | Notes |
|-----|--------|-------|
| `+` | Add new connection | Opens dialog to create new SSH connection |
| `E` | Edit connection | Edit selected connection (only when selected) |
| `f` | Toggle favorite status | Mark/unmark with ★ |
| `F` | Show favorites only | Filter to favorites |
| `r` | Sort by recent | Toggle recent-first sort |
| `L` | Connect to last used | Quick reconnect |

### Docker/Swarm Shortcuts

| Key | Action | View |
|-----|--------|------|
| `c` | Connect with bash | Docker/Swarm |
| `i` | Inspect container | Docker/Swarm |
| `l` | View logs | Docker |
| `S` | Stop container / Connect with sh | Docker / Swarm |
| `s` | Start container | Docker |
| `R` | Restart container | Docker |
| `D` | Remove container | Docker |
| `a` | Toggle show all containers | Docker |
| `b` | Connect with bash | Swarm |

### Tmux Shortcuts

| Key | Action | View |
|-----|--------|------|
| `c` or `Enter` | Switch to window | Tmux |
| `x` | Close/kill window | Tmux |
| `r` | Refresh window list | Tmux |

## Common Workflows

### Quick Connect to Favorite Server

1. Launch UCM: `ucm`
2. Type server name in filter: "prod"
3. Press Enter when it's the only result

### Adding a New SSH Connection

1. Launch UCM: `ucm`
2. Press `+` to open the Add Connection dialog
3. Fill in the required fields:
   - **Name** (required): A unique identifier (e.g., "webserver")
   - **Address** (required): IP or hostname (e.g., "192.168.1.100")
4. Fill in optional fields as needed:
   - **User**: SSH username (default: current user)
   - **Port**: SSH port (default: 22)
   - **Identity**: Path to SSH key (e.g., `~/.ssh/id_rsa`)
   - **Options**: Additional SSH options (e.g., `-X`)
   - **Category**: Group label for filtering
5. Press **Save** to create the connection
6. UCM automatically connects to the new server

### Editing an Existing Connection

1. Launch UCM: `ucm`
2. Select the connection you want to edit (using arrow keys or filter)
3. Press `E` to open the Edit Connection dialog
4. Modify any fields (all fields are editable, including name and address)
5. Press **Save** to update the connection
6. UCM reloads the list with your changes

**Note:** When editing, you can rename connections or change any field. UCM tracks the connection by its original name and address.

### Managing Multiple Environments

Organize by category:

```yaml
# Production servers
- name: prod-web
  address: web.prod.com
  category: production

- name: prod-db
  address: db.prod.com
  category: production

# Development servers
- name: dev-web
  address: web.dev.com
  category: development
```

Filter by environment:
- Type "production" to see only prod servers
- Type "development" for dev servers

### Docker Container Workflow

1. Switch to Docker view
2. Find your container (filter if needed)
3. Press `i` to inspect (check if it's the right one)
4. Press `c` or Enter to connect
5. Work in the container
6. Type `exit` to return to UCM

### Using Custom Config Location

Separate work and personal configs:

```bash
# Work connections
ucm --config-dir ~/.ucm-work

# Personal connections
ucm --config-dir ~/.ucm-personal
```

### Debugging Connection Issues

Enable debug logging:

```bash
ucm --log-level DEBUG
```

Then check the log file:

```bash
tail -f /tmp/ucm-$(whoami).log
```

## Tips and Tricks

### Faster Navigation with Vim Keys

Use `j` and `k` instead of arrow keys for faster up/down navigation (no need to reach for arrow keys).

### Filter Power-User Tips

- **Partial matching**: Type "web" to find "webserver1", "webserver2", etc.
- **Multiple matches**: Filter narrows down the list; use ↑/↓ to select
- **Clear filter**: Click in filter box and press Ctrl+U to clear

### SSH Config Integration

Set common options in `~/.ssh/config` instead of repeating in UCM:

```bash
# ~/.ssh/config
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking no
```

Now all UCM connections inherit these settings!

### Mouse vs Keyboard

**Use mouse when:**
- Browsing/exploring connections
- Working with multiple views
- Prefer visual interaction

**Use keyboard when:**
- You know exactly what you want
- Speed is important
- Working over SSH/slow connection

### Quick Docker Container Access

Instead of:
```bash
docker ps  # find container
docker exec -it abc123 bash
```

Just use UCM:
1. Launch UCM
2. Switch to Docker view
3. Double-click container

### Organizing Many Connections

For 100+ hosts, use categories and clear naming:

```yaml
- name: prod-web-01
  address: 10.0.1.10
  category: production-web

- name: prod-web-02
  address: 10.0.1.11
  category: production-web

- name: prod-db-01
  address: 10.0.2.10
  category: production-database
```

Filter by: "prod-web", "prod-db", "production", etc.

## Troubleshooting

### Configuration Errors

**Problem:** UCM shows configuration error on startup

**Solution:** Check the error message - it tells you exactly what's wrong:

```
❌ Configuration Error:
SSH connection configuration has 1 error(s):
  - Connection #3 ('server3'): Missing required field(s): address
```

Fix the config file at the indicated connection.

### SSH Connection Fails

**Problem:** Selected host but connection fails

**Common causes:**
1. **Wrong address** - Check spelling/IP
2. **Firewall** - Port 22 blocked?
3. **SSH key** - Wrong identity file or permissions
4. **User** - Wrong username specified

**Debug steps:**
```bash
# Test SSH manually
ssh user@hostname

# Check SSH key permissions
chmod 600 ~/.ssh/your-key.pem

# Enable UCM debug logging
ucm --log-level DEBUG
```

### Docker Containers Not Showing

**Problem:** Docker view is empty but containers are running

**Common causes:**
1. **Docker not running** - `docker ps` fails
2. **Permission denied** - User not in docker group
3. **Docker path** - Docker command not in PATH

**Solutions:**
```bash
# Verify Docker works
docker ps

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Check docker command location
which docker
```

### UCM Won't Start

**Problem:** UCM command not found or import errors

**Solutions:**
```bash
# Reinstall in editable mode
pip install -e .

# Check Python version (need 3.8+)
python --version

# Install missing dependencies
pip install -e ".[dev]"
```

### Filter Not Working

**Problem:** Typing in filter doesn't filter list

**Cause:** Focus is not on filter box

**Solution:**
- Click in the filter box with mouse
- Press Tab until filter box is highlighted
- Filter field names must match (name, address, user, category)

### Slow Performance with Many Connections

**Problem:** UCM sluggish with 500+ connections

**Solutions:**
1. **Use filters** - Type to narrow list before scrolling
2. **Split configs** - Use `--config-dir` for separate sets
3. **Categories** - Organize and filter by category

### Container Connection Drops Immediately

**Problem:** Connected to container but dropped right back to UCM

**Cause:** Container doesn't have bash or sh

**Solution:**
```bash
# Check container manually
docker exec -it container-name bash

# If no bash, try sh
docker exec -it container-name sh

# Some containers are minimal (e.g., scratch-based)
# You may need to use docker exec with specific command
```

### Permission Denied Errors

**Problem:** Can't write to config directory

**Solution:**
```bash
# Fix permissions
chmod 755 ~/.ucm
chmod 644 ~/.ucm/ssh_connections.yml

# Or use custom location
ucm --config-dir ~/my-configs
```

### Log File Issues

**Problem:** Can't write to `/tmp/ucm-user.log`

**Solution:**
```bash
# Use custom log location
ucm --log-file ~/ucm.log

# Or use system temp
ucm --log-file /var/tmp/ucm.log
```

## Advanced Usage

### Environment-Specific Configs

```bash
# Create alias for different environments
alias ucm-prod='ucm --config-dir ~/.ucm-production'
alias ucm-dev='ucm --config-dir ~/.ucm-development'
alias ucm-personal='ucm --config-dir ~/.ucm-personal'
```

### Integration with tmux/screen

UCM works great in tmux/screen sessions:

```bash
# Launch UCM in tmux pane
tmux
ucm

# Connect to host (from UCM)
# Work on host
# Exit to return to UCM
# Select next host...
```

### Automated Connection Lists

Generate configs from infrastructure as code:

```python
# generate_ucm_config.py
import yaml

hosts = [
    {"name": f"web-{i:02d}", "address": f"10.0.1.{i}", "category": "webservers"}
    for i in range(1, 11)
]

with open(os.path.expanduser("~/.ucm/ssh_connections.yml"), "w") as f:
    yaml.dump(hosts, f)
```

---

**Need more help?** Check [GitHub Issues](https://github.com/rszabo50/ucm/issues) or open a discussion!
