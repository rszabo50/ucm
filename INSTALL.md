# Installation Guide

This guide provides detailed installation instructions for UCM (Urwid Connection Manager) across different platforms and use cases.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [pipx / uv (Recommended)](#pipx--uv-recommended)
  - [Homebrew (macOS/Linux)](#homebrew-macoslinux)
  - [From Source](#from-source)
  - [Docker](#docker)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

- **Python**: 3.10 or higher (tested through 3.15; urwid 5.x requires Python 3.11+, so Python 3.10 uses urwid 3.x)
- **urwid**: 3.x or 5.x
- **Operating System**: Linux, macOS, or Unix-like systems
- **Terminal**: Any modern terminal emulator with UTF-8 support
- **Optional**: Docker (for container management features)

## Installation Methods

### pipx / uv (Recommended)

> **UCM is no longer published to PyPI.** The `ucm` package on PyPI is stuck at
> version 0.1.2 (March 2022) because the original PyPI account could not be
> recovered, so it can no longer be updated. That release depends on packages UCM
> no longer uses (`panwid`, `datatables`, `dataclasses`) and is out of date and no
> longer useful. **Do not install it** (`pip install ucm`); install from GitHub instead.

Modern Linux distributions (Ubuntu 24.04+, Debian 12+, Fedora 38+) mark the system
Python as "externally managed" ([PEP 668](https://peps.python.org/pep-0668/)), so
`pip install` into it is refused. Use `pipx` or `uv`, which create an isolated
environment per application:

```bash
# pipx
pipx install git+https://github.com/rszabo50/ucm.git

# or uv
uv tool install git+https://github.com/rszabo50/ucm.git

# Verify installation
ucm --version
```

**Install a specific release:**
```bash
pipx install git+https://github.com/rszabo50/ucm.git@v1.1.0
```

**Upgrade:**
```bash
pipx install --force git+https://github.com/rszabo50/ucm.git
# or
uv tool install --force git+https://github.com/rszabo50/ucm.git
```

**Install from a release wheel:** download the `.whl` from the
[GitHub Releases](https://github.com/rszabo50/ucm/releases) page, then run
`pipx install ./ucm-<version>-py3-none-any.whl`.

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

# Install Python 3 and pipx (works with PEP 668 "externally managed" system Python)
sudo apt install python3 pipx
pipx ensurepath

# Install UCM
pipx install git+https://github.com/rszabo50/ucm.git
```

### Fedora / RHEL / CentOS

```bash
# Install Python 3 and pipx
sudo dnf install python3 pipx
pipx ensurepath

# Install UCM
pipx install git+https://github.com/rszabo50/ucm.git
```

### macOS

```bash
brew install pipx
pipx ensurepath

# Install UCM
pipx install git+https://github.com/rszabo50/ucm.git
```

### Arch Linux

```bash
# Install Python and pipx
sudo pacman -S python python-pipx

# Install UCM
pipx install git+https://github.com/rszabo50/ucm.git
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
pip install git+https://github.com/rszabo50/ucm.git

# Run UCM (while venv is activated)
ucm

# Deactivate when done
deactivate
```

**Using pipx (isolated installation):**
```bash
# Install pipx (see https://pipx.pypa.io) if not already installed
pipx ensurepath

# Install UCM
pipx install git+https://github.com/rszabo50/ucm.git

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
# Add the pipx/user bin directory to PATH
pipx ensurepath
```

### Import errors

If you see import errors related to `urwid`:

```bash
# Reinstall UCM and its dependencies
pipx install --force git+https://github.com/rszabo50/ucm.git
```

### "externally-managed-environment" error

Newer Linux distributions (e.g. Ubuntu 24.04+/26.04) refuse `pip install` into the
system Python (PEP 668). Do not use `--break-system-packages`; install with `pipx`
or `uv tool` as described above, or use a virtual environment.

### Python version errors

UCM requires Python 3.10 or higher and is tested through Python 3.15:

```bash
# Check your Python version
python3 --version

# If too old, install a newer version
# Ubuntu/Debian
sudo apt install python3.14

# macOS
brew install python@3.15
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

### pipx / uv installation

```bash
# Uninstall UCM
pipx uninstall ucm
# or
uv tool uninstall ucm

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
