# Installation Guide

This guide provides detailed installation instructions for UCM (Urwid Connection Manager) across different platforms and use cases.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [PyPI (Recommended)](#pypi-recommended)
  - [Homebrew (macOS/Linux)](#homebrew-macoslinux)
  - [From Source](#from-source)
  - [Docker](#docker)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Unix-like systems
- **Terminal**: Any modern terminal emulator with UTF-8 support
- **Optional**: Docker (for container management features)

## Installation Methods

### PyPI (Recommended)

The easiest way to install UCM is from PyPI using pip:

```bash
# Install UCM
pip install ucm

# Verify installation
ucm --version

# Run UCM
ucm
```

**Upgrade to latest version:**
```bash
pip install --upgrade ucm
```

**Install specific version:**
```bash
pip install ucm==0.2.0
```

### Homebrew (macOS/Linux)

> **Note**: Homebrew formula coming soon!

Once available, you'll be able to install with:

```bash
# Install
brew install ucm

# Upgrade
brew upgrade ucm

# Uninstall
brew uninstall ucm
```

### From Source

Install the latest development version from GitHub:

**Clone and install:**
```bash
# Clone repository
git clone https://github.com/rszabo50/ucm.git
cd ucm

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

**Install with development dependencies:**
```bash
pip install -e ".[dev]"
```

This includes:
- pytest (testing)
- pytest-cov (coverage)
- mypy (type checking)
- ruff (linting/formatting)
- pre-commit (git hooks)

**Set up pre-commit hooks (for contributors):**
```bash
pre-commit install
```

### Docker

> **Note**: Docker image coming soon!

Once available, you can run UCM in a container:

```bash
# Run UCM in Docker
docker run -it --rm -v ~/.ucm:/root/.ucm -v ~/.ssh:/root/.ssh:ro rszabo50/ucm

# Create an alias for convenience
alias ucm='docker run -it --rm -v ~/.ucm:/root/.ucm -v ~/.ssh:/root/.ssh:ro rszabo50/ucm'
```

## Platform-Specific Instructions

### Ubuntu / Debian

```bash
# Update package list
sudo apt update

# Install Python 3 and pip if not already installed
sudo apt install python3 python3-pip

# Install UCM
pip3 install ucm

# Add pip install location to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Fedora / RHEL / CentOS

```bash
# Install Python 3 and pip
sudo dnf install python3 python3-pip

# Install UCM
pip3 install ucm

# Add to PATH if needed
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### macOS

```bash
# Python 3 usually comes with macOS
# If not, install using Homebrew:
brew install python3

# Install UCM
pip3 install ucm
```

### Arch Linux

```bash
# Install Python and pip
sudo pacman -S python python-pip

# Install UCM
pip install ucm
```

## Virtual Environments

It's recommended to use virtual environments to avoid conflicts with system packages:

**Using venv:**
```bash
# Create virtual environment
python3 -m venv ~/.venvs/ucm

# Activate
source ~/.venvs/ucm/bin/activate

# Install UCM
pip install ucm

# Run UCM (while venv is activated)
ucm

# Deactivate when done
deactivate
```

**Using pipx (isolated installation):**
```bash
# Install pipx if not already installed
pip install pipx
pipx ensurepath

# Install UCM
pipx install ucm

# UCM is now available globally
ucm
```

## Configuration

On first run, UCM creates a default configuration directory:

```bash
~/.ucm/
├── ssh_connections.yml  # SSH connection definitions
├── history.yml          # Connection history
└── favorites.yml        # Favorite connections
```

**Edit your SSH connections:**
```bash
vi ~/.ucm/ssh_connections.yml
```

**Example configuration:**
```yaml
- name: webserver
  address: web.example.com
  user: admin
  port: 22
  identity: ~/.ssh/web-key.pem
```

See [USER_GUIDE.md](USER_GUIDE.md) for detailed configuration options.

## Troubleshooting

### Command not found

If `ucm` command is not found after installation:

```bash
# Add pip user install directory to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Import errors

If you see import errors related to urwid or panwid:

```bash
# Reinstall with --force-reinstall
pip install --force-reinstall ucm
```

### Permission errors

If you get permission errors during installation:

```bash
# Install for current user only (recommended)
pip install --user ucm

# Or use sudo (not recommended)
sudo pip install ucm
```

### Python version errors

UCM requires Python 3.8 or higher:

```bash
# Check your Python version
python3 --version

# If too old, install a newer version
# Ubuntu/Debian
sudo apt install python3.11

# macOS
brew install python@3.11
```

### Docker connection issues

If UCM can't connect to Docker:

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect

# Verify Docker access
docker ps
```

## Uninstallation

### PyPI installation

```bash
# Uninstall UCM
pip uninstall ucm

# Remove configuration (optional)
rm -rf ~/.ucm
```

### Source installation

```bash
# Navigate to source directory
cd ucm

# Uninstall
pip uninstall ucm

# Remove source directory (optional)
cd ..
rm -rf ucm
```

### Homebrew installation

```bash
# Uninstall
brew uninstall ucm

# Remove configuration (optional)
rm -rf ~/.ucm
```

## Getting Help

- **Documentation**: [USER_GUIDE.md](USER_GUIDE.md)
- **Issues**: https://github.com/rszabo50/ucm/issues
- **Discussions**: https://github.com/rszabo50/ucm/discussions

## Next Steps

After installation, see:
- [USER_GUIDE.md](USER_GUIDE.md) - Comprehensive usage guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing to UCM
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup

---

**Need help?** Open an issue at https://github.com/rszabo50/ucm/issues
