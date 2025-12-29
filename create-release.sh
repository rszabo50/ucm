#!/bin/bash

# UCM Release Creation Script
# This script helps create a GitHub release with proper formatting

set -e

VERSION="${1:-v1.0.0}"
RELEASE_TITLE="UCM 1.0.0 - Production-Ready Terminal Connection Manager with History, Favorites, and Enhanced UX"

echo "Creating release: $VERSION"
echo "Title: $RELEASE_TITLE"
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install with: brew install gh"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check if tag exists
if ! git rev-parse "$VERSION" &> /dev/null 2>&1; then
    echo "⚠️  Tag $VERSION does not exist"
    echo ""
    read -p "Create tag $VERSION now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag "$VERSION"
        echo "✅ Tag $VERSION created"
    else
        echo "❌ Aborted - tag required for release"
        exit 1
    fi
fi

# Check if we should push the tag
if ! git ls-remote --tags origin | grep -q "$VERSION"; then
    echo "⚠️  Tag $VERSION not pushed to origin"
    echo ""
    read -p "Push tag $VERSION to origin? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "$VERSION"
        echo "✅ Tag $VERSION pushed"
    else
        echo "⚠️  Warning: Tag not pushed, release will be local only"
    fi
fi

# Check if release notes file exists
if [ ! -f "RELEASE_NOTES_SHORT.md" ]; then
    echo "❌ RELEASE_NOTES_SHORT.md not found"
    exit 1
fi

echo ""
echo "Creating GitHub release..."
echo ""

# Create the release using gh CLI
gh release create "$VERSION" \
    --title "$RELEASE_TITLE" \
    --notes-file RELEASE_NOTES_SHORT.md \
    --verify-tag

echo ""
echo "✅ Release $VERSION created successfully!"
echo ""
echo "View at: https://github.com/rszabo50/ucm/releases/tag/$VERSION"
echo ""
echo "Next steps:"
echo "  1. Verify the release looks correct on GitHub"
echo "  2. Monitor GitHub Actions for PyPI publish"
echo "  3. Test: pip install ucm"
echo "  4. Update Homebrew formula with SHA256 checksums"
echo ""
