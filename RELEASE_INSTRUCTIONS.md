# How to Create v1.0.0 Release

## Quick Release (Using Script)

```bash
# Make sure you're on main and up to date
git checkout main
git pull

# Run the release script
./create-release.sh v1.0.0
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
git tag v1.0.0

# Push tag
git push origin v1.0.0
```

### Step 2: Create GitHub Release

**Option A: Using GitHub CLI**

```bash
gh release create v1.0.0 \
  --title "UCM 1.0.0 - Production-Ready Terminal Connection Manager with History, Favorites, and Enhanced UX" \
  --notes-file RELEASE_NOTES_SHORT.md
```

**Option B: Using GitHub Web Interface**

1. Go to: https://github.com/rszabo50/ucm/releases/new
2. Choose tag: `v1.0.0`
3. Set title:
   ```
   UCM 1.0.0 - Production-Ready Terminal Connection Manager with History, Favorites, and Enhanced UX
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
  - Publish to PyPI (if trusted publishing is configured)
  - Attach dist files to the release

### 2. Verify PyPI Publication

```bash
# Wait a few minutes, then test
pip install ucm

# Check version
ucm --version
# Should show: ucm 1.0.0
```

### 3. Update Issue #10

- Go to: https://github.com/rszabo50/ucm/issues/10
- Add comment: "Released as v1.0.0: https://github.com/rszabo50/ucm/releases/tag/v1.0.0"
- Close the issue

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
UCM 1.0.0 - Production-Ready Terminal Connection Manager with History, Favorites, and Enhanced UX
```

**Description:**
See `RELEASE_NOTES_SHORT.md` - already formatted for GitHub release.

---

## What Happens When You Tag

When you push `v1.0.0` tag, GitHub Actions automatically:

1. **Builds** the package from source
2. **Publishes** to PyPI (if trusted publishing is configured)
3. **Creates** GitHub release (only if using script or manual release)
4. **Attaches** distribution files (.tar.gz and .whl)

---

## Troubleshooting

**If PyPI publish fails:**
- Check GitHub Actions logs
- Verify trusted publishing is configured: https://pypi.org/manage/account/publishing/
- See PYPI_RELEASE_CHECKLIST.md for detailed setup

**If release creation fails:**
- Make sure `gh` CLI is installed: `brew install gh`
- Authenticate: `gh auth login`
- Check tag exists: `git tag -l v1.0.0`

---

## Version Summary

**Current Version:** v0.1.2
**New Version:** v1.0.0

**Major Changes:**
- Connection history and favorites
- Vim-style filter activation
- Structured logging
- Service layer architecture
- PyPI packaging ready
- Comprehensive documentation

**Why 1.0.0?**
- Production-ready quality
- Comprehensive test coverage (66 tests)
- Professional architecture
- Full feature set for core functionality
- Complete documentation
- Automated CI/CD

---

Ready to release! 🚀
