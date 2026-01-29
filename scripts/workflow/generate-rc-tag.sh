#!/bin/bash
set -euo pipefail

# ==============================
# Script to generate next RC tag
# ==============================

# Inputs
LAST_RELEASE_VERSION="$1"   # e.g., 1.6.0 (from semantic-release or manually)
GIT_REMOTE="${2:-origin}"   # Optional, defaults to 'origin'

# Base RC tag with v prefix
RC_BASE="v${LAST_RELEASE_VERSION}-rc"

# Fetch all tags from remote
git fetch --tags "$GIT_REMOTE"

# Find the last RC tag for this version
LAST_RC=$(git tag --list "${RC_BASE}.*" | sort -V | tail -n 1)

# Determine next RC number
if [ -z "$LAST_RC" ]; then
  NEXT_RC_NUMBER=1
else
  LAST_NUMBER=${LAST_RC##*-rc.}    # Extract the number after -rc.
  NEXT_RC_NUMBER=$((LAST_NUMBER + 1))
fi

# Create new RC tag
RC_TAG="${RC_BASE}.${NEXT_RC_NUMBER}"
git tag "$RC_TAG"
git push "$GIT_REMOTE" "$RC_TAG"

# Output for CI/CD pipelines
echo "$RC_TAG"
