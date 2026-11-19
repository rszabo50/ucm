# How to Create v1.1.0 Release

## Quick Release (Using Script)

```bash
# Make sure you're on main and up to date
git checkout main
git pull

# Run the release script
./create-release.sh v1.1.0
```

The script will:
1. Create the tag if needed
2. Push the tag to GitHub
3. Create the GitHub release with proper title and notes
4. Show you next steps

---

## Manual Release (If you prefer)

### Step 1: Create and Push Tag

```bash
# Create tag
git tag v1.1.0

# Push tag
git push origin v1.1.0
```

### Step 2: Create GitHub Release

**Option A: Using GitHub CLI**

```bash
gh release create v1.1.0 \
  --title "UCM 1.1.0 - Docker, tmux and iTerm2 Integration, Settings Screen, and urwid 5 Support" \
  --notes-file RELEASE_NOTES_SHORT.md
```

**Option B: Using GitHub Web Interface**

1. Go to: https://github.com/rszabo50/ucm/releases/new
2. Choose tag: `v1.1.0`
3. Set title:
   ```
   UCM 1.1.0 - Docker, tmux and iTerm2 Integration, Settings Screen, and urwid 5 Support
   ```
4. Copy contents from `RELEASE_NOTES_SHORT.md` into description
5. Click "Publish release"

---

## After Release

### 1. Monitor GitHub Actions

- Go to: https://github.com/rszabo50/ucm/actions
- Watch the "Release" workflow
- It will automatically:
  - Build the package
  - Attach dist files to the release

### 2. Verify the Release

UCM is no longer published to PyPI; install from the tag instead.

```bash
pipx install --force git+https://github.com/rszabo50/ucm.git@v1.1.0

# Check version
ucm --version
# Should show: ucm 1.1.0
```

---

## Release Notes Files

Two versions are available:

- **RELEASE_v1.0.0.md** - Full comprehensive release notes (for reference)
- **RELEASE_NOTES_SHORT.md** - Concise version (used in GitHub release)

The short version is automatically used by `create-release.sh` and is perfect for the GitHub release page.

---

## Title and Description

**Release Title:**
```
UCM 1.1.0 - Docker, tmux and iTerm2 Integration, Settings Screen, and urwid 5 Support
```

**Description:**
See `RELEASE_NOTES_SHORT.md` - already formatted for GitHub release.

---

## What Happens When You Tag

When you push `v1.1.0` tag, GitHub Actions automatically:

1. **Builds** the package from source
2. **Creates** GitHub release (only if using script or manual release)
3. **Attaches** distribution files (.tar.gz and .whl)

---

## Troubleshooting

**If the release build fails:**
- Check GitHub Actions logs

**If release creation fails:**
- Make sure `gh` CLI is installed: `brew install gh`
- Authenticate: `gh auth login`
- Check tag exists: `git tag -l v1.1.0`

---

## Version Summary

**Current Version:** v1.0.0
**New Version:** v1.1.0

**Major Changes:**
- Docker container management, tmux windows view, iTerm2 split panes
- Settings screen and SSH connection add/edit
- Redesigned UI layout with F5 layout refresh
- urwid 3.x and 5.x support, Python 3.15
- UCM is no longer published to PyPI; install with pipx or uv from GitHub

**Why 1.1.0?**
- New backwards-compatible features (minor version bump)
- Changed install method

---

Ready to release! 🚀
