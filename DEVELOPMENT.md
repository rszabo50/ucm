# UCM Development Guide

## Known Issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for a list of known issues and workarounds, including the panwid deprecation warnings with urwid 3.x.

## Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/rszabo50/ucm.git
cd ucm

# Install in development mode with dev dependencies
make install-dev

# Set up pre-commit hooks (recommended!)
make pre-commit-install

# Or manually:
pip3 install -e ".[dev]"
pre-commit install
```

### Pre-commit Hooks

Pre-commit hooks automatically run before each commit to ensure code quality:

- ✅ Auto-format code with Ruff
- ✅ Check for lint errors
- ✅ Run type checking with mypy
- ✅ Run all tests
- ✅ Check for trailing whitespace, YAML syntax, etc.

**Setup:**
```bash
make pre-commit-install
```

**Manual run on all files:**
```bash
make pre-commit-run
```

**Update hooks to latest versions:**
```bash
make pre-commit-update
```

**Skip hooks (not recommended):**
```bash
git commit --no-verify
```

## Development Workflow

### Running the Application

```bash
# Standard run
make run

# With debug logging
make run-debug

# With custom config directory
python3 -m ucm --config-dir ~/my-ucm-config

# Show all options
make run-help
```

### Testing

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
python3 -m pytest tests/test_ssh_commands.py -v
```

### Code Quality

```bash
# Run linter
make lint

# Format code
make format

# Check formatting without changes
make format-check

# Type checking
make type-check

# Run all checks
make check-all
```

## Project Structure

```
ucm/
├── src/
│   └── ucm/
│       ├── __init__.py
│       ├── __main__.py        # Entry point with CLI args
│       ├── constants.py       # Constants and version
│       ├── Registry.py        # Global registry singleton
│       ├── UserConfig.py      # Configuration management
│       ├── SshListView.py     # SSH connections view
│       ├── DockerListView.py  # Docker containers view
│       ├── SwarmListView.py   # Docker Swarm view
│       ├── Widgets.py         # UI widgets
│       ├── Dialogs.py         # Dialog windows
│       └── TabGroup.py        # Tab management
├── tests/
│   ├── test_ssh_commands.py  # SSH command tests
│   ├── test_config.py         # Configuration tests
│   └── test_registry.py       # Registry tests
├── pyproject.toml             # Project metadata and config
├── requirements.txt           # Dependencies
├── Makefile                   # Development commands
└── README.md                  # User documentation
```

## Code Standards

### Type Hints
All new code should include type hints:

```python
def connect(self, data: Dict[str, Any]) -> None:
    """Connect to SSH host.

    Args:
        data: Connection dictionary with address, user, etc.
    """
    pass
```

### Error Handling
Use specific exceptions and log errors:

```python
try:
    result = subprocess.run(cmd, capture_output=True, check=True)
except FileNotFoundError:
    logging.error(f"Command not found: {cmd}")
    return None
except subprocess.CalledProcessError as e:
    logging.error(f"Command failed: {e}")
    return None
```

### Documentation
All public functions should have docstrings:

```python
def build_ssh_command(data: Dict[str, Any]) -> str:
    """Build SSH command from connection data.

    Args:
        data: Connection dictionary with keys: address, user, port, identity, options

    Returns:
        Formatted SSH command string
    """
```

## Testing Guidelines

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names that explain what's being tested
- Mock external dependencies (subprocess, file I/O, etc.)

Example test:

```python
def test_ssh_command_with_user(self):
    """Test SSH command with user and address."""
    data = {'address': '192.168.1.100', 'user': 'admin'}
    cmd = SshListView.build_ssh_command(data)
    self.assertEqual(cmd, 'ssh    admin@192.168.1.100')
```

## Configuration

### Ruff (Linter/Formatter)
Configuration in `pyproject.toml` under `[tool.ruff]`

### Mypy (Type Checker)
Configuration in `pyproject.toml` under `[tool.mypy]`

### Pytest (Testing)
Configuration in `pyproject.toml` under `[tool.pytest.ini_options]`

## Git Workflow

1. Create a feature branch
2. Make your changes
3. Commit your changes (pre-commit hooks run automatically!)
4. Push and create a pull request

**Pre-commit hooks will automatically:**
- Format your code
- Run linter
- Run type checks
- Run all tests

If any check fails, the commit will be aborted. Fix the issues and try again.

**Manual quality checks:**
```bash
make check-all         # Run all checks manually
make pre-commit-run    # Run pre-commit on all files
```

## Version Management

UCM uses **setuptools_scm** for automatic version management from git tags. You never need to manually edit version numbers!

### How It Works

The version is automatically derived from your git tags:

- **Tagged release**: `v0.1.2` → version is `0.1.2`
- **Development version**: After changes since last tag → `0.1.3.dev0` (automatically increments)
- **No tags**: Falls back to `0.0.0.dev0`

### Creating a New Release

**1. Commit all your changes:**
```bash
git add .
git commit -m "Your changes"
```

**2. Create a git tag:**
```bash
# For version 0.2.0
git tag -a v0.2.0 -m "Version 0.2.0 - Feature description"
```

**3. Reinstall to pick up the new version:**
```bash
pip3 install -e .
```

**4. Verify the version:**
```bash
ucm --version        # Should show: ucm 0.2.0
python3 -c "from ucm.constants import PROGRAM_VERSION; print(PROGRAM_VERSION)"
```

**5. Push the tag to GitHub:**
```bash
git push origin v0.2.0
```

### Version Naming Convention

Use semantic versioning: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v2.0.0)
- **MINOR**: New features, backwards compatible (v0.2.0)
- **PATCH**: Bug fixes (v0.1.3)

Examples:
```bash
git tag -a v0.1.3 -m "Version 0.1.3 - Bug fixes"
git tag -a v0.2.0 -m "Version 0.2.0 - New Docker features"
git tag -a v1.0.0 -m "Version 1.0.0 - First stable release"
```

### Development Versions

When you have uncommitted changes or commits after a tag, setuptools_scm automatically creates a development version:

```bash
# Latest tag: v0.1.2
# You make changes and commit
# Version becomes: 0.1.3.dev0

ucm --version  # Shows: ucm 0.1.3.dev0
```

This helps identify development builds vs. official releases.

### GitHub Integration

On GitHub, tags automatically create releases:

1. Push your tag: `git push origin v0.2.0`
2. Go to GitHub → Releases → You'll see v0.2.0
3. Edit the release to add release notes

### Checking Current Version

```bash
# From command line
ucm --version

# From Python code
python3 -c "from ucm.constants import PROGRAM_VERSION; print(PROGRAM_VERSION)"

# From git
git describe --tags  # Shows: v0.1.2 or v0.1.2-1-g1a2b3c4
```

### Troubleshooting

**Version shows 0.0.0.dev0:**
- You don't have any git tags yet
- Create one: `git tag -a v0.1.0 -m "Initial version"`
- Reinstall: `pip3 install -e .`

**Version not updating:**
- Reinstall the package: `pip3 install -e .`
- Check git tags exist: `git tag -l`

**Want to see what version will be assigned:**
```bash
python3 -m setuptools_scm
```

## Troubleshooting

### Import Errors
If you get import errors, make sure you installed in editable mode:
```bash
pip3 install -e .
```

### Type Checking Fails
If mypy complains about missing stubs:
```bash
pip3 install types-PyYAML
```

### Tests Fail
Check that you're running from the project root:
```bash
cd /path/to/ucm
python3 -m pytest tests/
```
