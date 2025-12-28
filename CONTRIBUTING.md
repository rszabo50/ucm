# Contributing to UCM

Thank you for your interest in contributing to UCM! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal or political attacks
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of terminal UI concepts
- Familiarity with SSH and/or Docker (helpful but not required)

### Development Setup

1. **Fork and Clone**

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR-USERNAME/ucm.git
cd ucm
```

2. **Create a Virtual Environment** (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Development Dependencies**

```bash
pip install -e ".[dev]"
```

4. **Install Pre-commit Hooks**

```bash
pre-commit install
```

5. **Verify Setup**

```bash
# Run tests
pytest tests/

# Run UCM
ucm
```

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

### 2. Make Changes

- Write code following our [Code Standards](#code-standards)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_validators.py

# Run with coverage
pytest tests/ --cov=ucm

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/ucm/

# Run all pre-commit hooks
pre-commit run --all-files
```

### 4. Commit Your Changes

We use conventional commit messages:

```bash
# Format: <type>(<scope>): <subject>

# Examples:
git commit -m "feat(ssh): add support for ProxyJump option"
git commit -m "fix(docker): handle containers without bash shell"
git commit -m "docs(readme): add troubleshooting section"
git commit -m "test(validators): add port validation tests"
git commit -m "refactor(ui): extract filter logic to separate method"
```

**Commit Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Test changes
- `chore` - Build process or tooling changes

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
# The CI will automatically run tests
```

## Code Standards

### Python Style

We use **Ruff** for linting and formatting:

```bash
# Format code
ruff format src/ tests/

# Check for issues
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### Code Style Guidelines

**General Principles:**
- Follow PEP 8
- Maximum line length: 120 characters
- Use clear, descriptive variable names
- Add docstrings to public functions
- Keep functions focused and small

**Example:**

```python
def validate_connection(conn: Dict[str, Any], index: int = 0) -> Tuple[bool, Optional[str]]:
    """Validate a single SSH connection configuration.

    Args:
        conn: Connection dictionary to validate
        index: Connection index for error messages

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(conn, dict):
        return False, f"Connection #{index + 1} is not a dictionary"

    # Validation logic...
    return True, None
```

### Type Hints

- Add type hints to all new functions
- Use `typing` module types: `Dict`, `List`, `Optional`, `Any`, etc.
- Type hints help catch bugs and improve documentation

```python
from typing import Any, Dict, List, Optional

def fetch_data(self) -> List[Dict[str, Any]]:
    """Fetch connection data."""
    return []
```

### Error Handling

- Use specific exception types
- Log errors with context
- Provide helpful error messages to users

```python
try:
    result = validate_connections(connections)
except ConfigValidationError as e:
    logging.error(f"Validation failed: {e}")
    print(f"\n❌ Configuration Error:\n{e}\n")
    raise
```

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update user-facing documentation when changing features

```python
def connect(self, data: Dict[str, Any]) -> None:
    """Execute SSH connection to remote host.

    Args:
        data: Connection dictionary containing:
            - address (str): Remote host address
            - user (str, optional): SSH username
            - port (int, optional): SSH port
            - identity (str, optional): SSH key path

    Raises:
        ConnectionError: If SSH connection fails
    """
```

## Testing

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names

```python
def test_valid_minimal_connection(self):
    """Test validation of minimal valid connection."""
    conn = {'name': 'server1', 'address': '192.168.1.100'}
    is_valid, error = SshConnectionValidator.validate_connection(conn)
    self.assertTrue(is_valid)
    self.assertIsNone(error)

def test_missing_required_field(self):
    """Test validation fails when required field is missing."""
    conn = {'name': 'server1'}  # Missing 'address'
    is_valid, error = SshConnectionValidator.validate_connection(conn)
    self.assertFalse(is_valid)
    self.assertIn('address', error)
```

### Test Organization

```
tests/
├── test_validators.py    # Validation tests
├── test_config.py        # Configuration tests
├── test_ssh_commands.py  # SSH command building tests
└── test_registry.py      # Registry pattern tests
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific file
pytest tests/test_validators.py

# Specific test
pytest tests/test_validators.py::TestSshConnectionValidator::test_valid_minimal_connection

# With coverage report
pytest tests/ --cov=ucm --cov-report=html

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x
```

## Submitting Changes

### Pull Request Process

1. **Update Documentation**
   - Update README.md if adding features
   - Update USER_GUIDE.md for user-facing changes
   - Add/update docstrings

2. **Ensure Tests Pass**
   - All existing tests pass
   - New tests added for new features
   - Coverage doesn't decrease

3. **Create Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes

4. **PR Description Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing done

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] No new warnings
```

5. **Review Process**
   - Maintainers will review your PR
   - Address any feedback
   - CI must pass before merging
   - Squash commits when merging

### Commit Message Guidelines

Good commit messages help understand the project history.

**Good examples:**
```
feat(ssh): add ProxyJump configuration support

Allows users to specify ProxyJump hosts in SSH connections.
This enables connecting through bastion/jump hosts.

Closes #42
```

```
fix(docker): handle containers without bash shell

Some minimal containers don't have bash. Now UCM tries bash
first, then falls back to sh, matching Docker's behavior.

Fixes #38
```

**Bad examples:**
```
fixed stuff
update code
changes
```

## Reporting Bugs

### Before Reporting

1. **Search existing issues** - Your bug might already be reported
2. **Try latest version** - Bug might be fixed in main branch
3. **Check documentation** - Might be expected behavior

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
1. Launch UCM with...
2. Click on...
3. See error...

**Expected behavior**
What should happen instead

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- UCM version: [e.g., 0.1.2]
- Installation method: [pip, source]

**Configuration:**
```yaml
# Relevant parts of your config (sanitize sensitive data!)
```

**Log output:**
```
# Relevant log lines (with --log-level DEBUG)
```

**Additional context**
Any other relevant information
```

### Security Issues

**DO NOT** report security vulnerabilities in public issues.

Email security concerns to: rszabo50@gmail.com

## Requesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
What should the feature do?

**Describe alternatives you've considered**
Other approaches considered

**Additional context**
Mockups, examples, etc.
```

### Feature Discussion

- Feature requests are discussed in Issues
- Maintainers will label as `enhancement`
- Community feedback is encouraged
- Implementation priority determined by maintainers

## Development Tips

### Debugging UCM

```bash
# Run with debug logging
ucm --log-level DEBUG

# Watch log file
tail -f /tmp/ucm-$(whoami).log

# Use Python debugger
# Add to code: import pdb; pdb.set_trace()
```

### Testing UI Changes

- Test with different terminal sizes
- Test with and without mouse
- Test keyboard navigation thoroughly
- Test with many connections (100+)

### Documentation Changes

Documentation-only changes don't need extensive tests:

```bash
# Just ensure docs render correctly
# Check for broken links
# Verify code examples work
```

## Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Open an Issue
- **Feature ideas**: Open an Issue with `enhancement` label
- **Security concerns**: Email rszabo50@gmail.com

## License

By contributing to UCM, you agree that your contributions will be licensed under the GNU GPLv3 license.

---

**Thank you for contributing to UCM!** 🎉

Every contribution, no matter how small, helps make UCM better for everyone.
