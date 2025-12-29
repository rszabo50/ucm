# Homebrew Formula for UCM

This directory contains the Homebrew formula for UCM (Urwid Connection Manager).

## Prerequisites

1. UCM must be published to PyPI first
2. You need the SHA256 checksum of the PyPI release

## Getting SHA256 Checksums

After publishing to PyPI, get the SHA256 for the main package and all dependencies:

```bash
# Get UCM package SHA256
curl -sL https://pypi.org/pypi/ucm/json | \
  jq -r '.releases["0.2.0"][] | select(.packagetype=="sdist") | .digests.sha256'

# Get PyYAML SHA256
curl -sL https://pypi.org/pypi/PyYAML/json | \
  jq -r '.releases["6.0.3"][] | select(.packagetype=="sdist") | .digests.sha256'

# Get urwid SHA256
curl -sL https://pypi.org/pypi/urwid/json | \
  jq -r '.releases | to_entries | max_by(.key) | .value[] | select(.packagetype=="sdist") | .digests.sha256'

# Get panwid SHA256
curl -sL https://pypi.org/pypi/panwid/json | \
  jq -r '.releases | to_entries | max_by(.key) | .value[] | select(.packagetype=="sdist") | .digests.sha256'
```

Or manually:
1. Go to https://pypi.org/project/ucm/#files
2. Click on the `.tar.gz` file
3. Look for "SHA256" in the file details

## Updating the Formula

1. Edit `ucm.rb`
2. Update the version number in the `url` field
3. Replace `REPLACE_WITH_ACTUAL_SHA256_AFTER_PYPI_RELEASE` with actual SHA256
4. Update all resource SHA256 values
5. Test the formula locally (see below)

## Testing Locally

```bash
# Install from local formula
brew install --build-from-source ./homebrew/ucm.rb

# Test it works
ucm --version

# Uninstall
brew uninstall ucm
```

## Publishing Options

### Option 1: Create Your Own Tap (Recommended for testing)

```bash
# Create a tap repository
# Repository name must be: homebrew-<tap-name>
# Example: homebrew-ucm

# Users can then install with:
brew tap rszabo50/ucm
brew install ucm
```

### Option 2: Submit to Homebrew Core

Requirements for submission to homebrew-core:
- Package must be stable (not pre-release)
- Package must be notable/widely used
- Must pass all brew audit checks
- See: https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md

**Steps:**
1. Fork homebrew-core
2. Add ucm.rb to Formula/ directory
3. Test thoroughly
4. Submit PR

### Option 3: Homebrew Cask (if creating a standalone app)

If you package UCM as a standalone .app or .dmg:
- See: https://github.com/Homebrew/homebrew-cask

## Audit and Test Commands

```bash
# Audit the formula
brew audit --strict --online ./homebrew/ucm.rb

# Test installation
brew install --build-from-source ./homebrew/ucm.rb
brew test ucm

# Test uninstall
brew uninstall ucm
```

## Formula Maintenance

When releasing a new version:

1. Update version in `url` field
2. Get new SHA256 checksum
3. Update `sha256` field
4. Test locally
5. Push to tap repository (or update PR for homebrew-core)

## Resources

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Python for Formula Authors](https://docs.brew.sh/Python-for-Formula-Authors)
- [Homebrew Core Contributing](https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md)

## Notes

- The formula uses `virtualenv_install_with_resources` to create an isolated Python environment
- Dependencies are automatically resolved from the resources list
- The formula is compatible with Homebrew on macOS and Linux
