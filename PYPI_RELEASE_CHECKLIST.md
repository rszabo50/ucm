# PyPI Release Checklist

**Date Prepared**: December 29, 2024
**Status**: Waiting for PyPI account recovery
**Goal**: Complete issue #10 - Publish UCM to PyPI

---

## Prerequisites (Already Completed ✅)

- ✅ Package configuration (`pyproject.toml`) is ready
- ✅ GitHub Actions workflow (`.github/workflows/release.yml`) is configured
- ✅ Package builds successfully (`python -m build` tested locally)
- ✅ Installation documentation written (README.md, INSTALL.md)
- ✅ Homebrew formula template created (`homebrew/ucm.rb`)

---

## Step 1: Set Up PyPI Trusted Publishing

Once you have PyPI account access:

1. **Log in to PyPI**
   - Go to: https://pypi.org/account/login/
   - Log in with your credentials

2. **Set up trusted publishing**
   - Go to: https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in the form:
     ```
     PyPI Project Name: ucm
     Owner: rszabo50
     Repository name: ucm
     Workflow name: release.yml
     Environment name: (leave blank)
     ```
   - Click "Add"

3. **Verify the setup**
   - You should see "ucm" in your pending publishers list
   - Status will change to "active" after first successful publish

**Note**: This is a one-time setup. GitHub Actions will be able to publish without API tokens.

---

## Step 2: Create and Push a Release Tag

From your local `ucm` repository:

```bash
# Make sure you're on main branch and up to date
git checkout main
git pull

# Verify tests pass
pytest tests/

# Create a version tag (suggests v0.2.0 as next version)
git tag v0.2.0

# Push the tag to GitHub
git push origin v0.2.0
```

**What happens next**:
- GitHub Actions workflow automatically triggers
- Package is built
- Package is published to PyPI
- GitHub release is created with changelog

---

## Step 3: Monitor the Release

1. **Watch GitHub Actions**
   - Go to: https://github.com/rszabo50/ucm/actions
   - Find the "Release" workflow run
   - Wait for it to complete (usually 2-3 minutes)

2. **Check for errors**
   - If the workflow fails, check the logs
   - Common issues:
     - Trusted publishing not configured → Go back to Step 1
     - Build errors → Check the build logs
     - PyPI upload errors → Check PyPI permissions

3. **Verify PyPI publication**
   - Go to: https://pypi.org/project/ucm/
   - You should see version 0.2.0 listed
   - Click on "Release history" to confirm

4. **Verify GitHub release**
   - Go to: https://github.com/rszabo50/ucm/releases
   - You should see "v0.2.0" release with:
     - Changelog
     - Installation instructions
     - Attached dist files (.tar.gz and .whl)

---

## Step 4: Test the PyPI Installation

On a clean machine or virtual environment:

```bash
# Create a test environment
python3 -m venv /tmp/test-ucm
source /tmp/test-ucm/bin/activate

# Install from PyPI
pip install ucm

# Verify installation
ucm --version
# Should show: ucm 0.2.0

# Test running UCM
ucm
# Press 'q' to quit

# Clean up
deactivate
rm -rf /tmp/test-ucm
```

If this works, the PyPI release is successful! 🎉

---

## Step 5: Update Homebrew Formula (Optional)

Once PyPI is working, you can prepare the Homebrew formula:

1. **Get the SHA256 checksum from PyPI**

```bash
# Get UCM package SHA256
curl -sL https://pypi.org/pypi/ucm/json | \
  jq -r '.releases["0.2.0"][] | select(.packagetype=="sdist") | .digests.sha256'
```

Or manually:
- Go to: https://pypi.org/project/ucm/#files
- Click on the `ucm-0.2.0.tar.gz` file
- Copy the SHA256 value

2. **Update the Homebrew formula**

Edit `homebrew/ucm.rb`:
```ruby
# Change this line:
url "https://files.pythonhosted.org/packages/source/u/ucm/ucm-0.2.0.tar.gz"
sha256 "REPLACE_WITH_ACTUAL_SHA256_AFTER_PYPI_RELEASE"

# To (with your actual SHA256):
url "https://files.pythonhosted.org/packages/source/u/ucm/ucm-0.2.0.tar.gz"
sha256 "abc123def456..."  # Your actual SHA256
```

3. **Get dependency SHA256s**

```bash
# PyYAML
curl -sL https://pypi.org/pypi/PyYAML/json | \
  jq -r '.releases["6.0.3"][] | select(.packagetype=="sdist") | .digests.sha256'

# urwid (get latest version)
curl -sL https://pypi.org/pypi/urwid/json | \
  jq -r '.releases | to_entries | max_by(.key) | .value[] | select(.packagetype=="sdist") | .digests.sha256'

# panwid
curl -sL https://pypi.org/pypi/panwid/json | \
  jq -r '.releases["0.3.5"][] | select(.packagetype=="sdist") | .digests.sha256'
```

4. **Test locally**

```bash
# Install from local formula
brew install --build-from-source ./homebrew/ucm.rb

# Test
ucm --version

# Uninstall
brew uninstall ucm
```

5. **Publish the formula** (choose one option)

**Option A: Create your own tap** (easier, recommended)
```bash
# Create a new GitHub repo named: homebrew-ucm
# Add ucm.rb to the repo
# Users install with:
#   brew tap rszabo50/ucm
#   brew install ucm
```

**Option B: Submit to homebrew-core** (for wider distribution)
- See: https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md
- Requires the package to be stable and notable

---

## Step 6: Update Documentation

After successful PyPI release:

1. **Update README.md** (if needed)
   - Verify installation instructions are current
   - Already done, but double-check

2. **Update issue #10**
   - Go to: https://github.com/rszabo50/ucm/issues/10
   - Add a comment with the release notes
   - Close the issue

---

## Step 7: Announce the Release

Consider announcing on:
- GitHub Discussions
- Social media (if applicable)
- Python community forums
- Your blog/website

---

## Troubleshooting

### Issue: "Trusted publishing not configured"

**Solution**: Make sure you completed Step 1 correctly. The PyPI project name must be exactly "ucm" (lowercase).

### Issue: "Version already exists on PyPI"

**Solution**: You can't re-upload the same version. Increment the version:
```bash
git tag v0.2.1  # or next version
git push origin v0.2.1
```

### Issue: GitHub Actions workflow not triggering

**Solution**:
- Check that the tag starts with 'v' (e.g., v0.2.0, not 0.2.0)
- Verify `.github/workflows/release.yml` exists
- Check GitHub Actions are enabled in repository settings

### Issue: Build fails with "listing git files failed"

**Solution**: This is just a warning in the sdist build, it doesn't affect the release. You can ignore it.

### Issue: Import errors after pip install

**Solution**:
```bash
# Force reinstall
pip install --force-reinstall ucm

# Or install in isolation
pipx install ucm
```

---

## Quick Reference Commands

```bash
# Full release process (assuming PyPI is configured)
git checkout main
git pull
pytest tests/
git tag v0.2.0
git push origin v0.2.0

# Monitor release
open https://github.com/rszabo50/ucm/actions

# Verify PyPI
pip install ucm
ucm --version

# Get SHA256 for Homebrew
curl -sL https://pypi.org/pypi/ucm/json | \
  jq -r '.releases["0.2.0"][] | select(.packagetype=="sdist") | .digests.sha256'
```

---

## Version Numbering

Current latest tag: `v0.1.2`
Suggested next version: `v0.2.0` (new features added since last release)

Future versions:
- Patch release (bug fixes): v0.2.1, v0.2.2, etc.
- Minor release (new features): v0.3.0, v0.4.0, etc.
- Major release (breaking changes): v1.0.0, v2.0.0, etc.

---

## What's Already Done

- ✅ Package configuration (pyproject.toml)
- ✅ GitHub release workflow (.github/workflows/release.yml)
- ✅ All tests passing (66 tests)
- ✅ Package builds successfully
- ✅ README.md updated with installation instructions
- ✅ INSTALL.md created with detailed platform guides
- ✅ Homebrew formula template (homebrew/ucm.rb)
- ✅ All documentation committed and pushed

---

## Support

If you run into issues:

1. Check the GitHub Actions logs for error details
2. Review PyPI trusted publishing docs: https://docs.pypi.org/trusted-publishers/
3. Open an issue if you find a bug: https://github.com/rszabo50/ucm/issues
4. Check the workflow file: `.github/workflows/release.yml`

---

**Good luck with the PyPI release!** 🚀

Once complete, issue #10 can be closed and UCM will be available via `pip install ucm`.
