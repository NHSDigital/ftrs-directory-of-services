#! /bin/bash

set -e

echo "Fetching tags..."
git fetch --tags

# Get latest stable tag
latest_stable=$(git tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | head -n 1 || true)
echo "Latest stable tag: ${latest_stable:-none}"

# Get latest prerelease tag
latest_pre=$(git tag --sort=-v:refname | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+-pre\.[0-9]+$' | head -n 1 || true)
echo "Latest prerelease tag: ${latest_pre:-none}"

# Function to bump patch version
bump_patch() {
  local version="$1"
  IFS='.' read -r major minor patch <<<"${version#v}"
  patch=$((patch + 1))
  echo "v${major}.${minor}.${patch}"
}

# Determine base version
if [[ -z "$latest_stable" ]]; then
  base="v0.1.0"
else
  base="$latest_stable"
fi

# Determine next patch version for prerelease
next_base=$(bump_patch "$base")

# Determine next prerelease number
pre_tags=$(git tag --list "${next_base}-pre.*" | sort -V)
if [[ -n "$pre_tags" ]]; then
  last_pre=$(echo "$pre_tags" | tail -n 1)
  pre_num=$(echo "$last_pre" | grep -oE 'pre.[0-9]+' | cut -d. -f2)
  next_pre=$((pre_num + 1))
else
  next_pre=1
fi

next_tag="${next_base}-pre.${next_pre}"

# If this exact tag exists find next available
while git tag --list "$next_tag" >/dev/null 2>&1 && git tag --list "$next_tag" | grep -q .; do
  echo "Tag $next_tag already exists, incrementing prerelease number..."
  next_pre=$((next_pre + 1))
  next_tag="${next_base}-pre.${next_pre}"
done

echo "Next prerelease tag: ${next_tag}"

# Create and push the new tag
git tag "$next_tag"
git push origin "$next_tag"

echo "Prerelease generation complete."
