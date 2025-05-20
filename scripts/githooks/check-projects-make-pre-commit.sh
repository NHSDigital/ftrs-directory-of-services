#!/bin/bash
set -euo pipefail

# Get the repository root directory
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Function to check if a Makefile has a pre-commit target
has_pre_commit_target() {
  if [ -f "$1/Makefile" ]; then
    grep -q "^pre-commit:" "$1/Makefile" && return 0
  fi
  return 1
}

# Function to check if a directory has staged changes
has_staged_changes() {
  dir_path="$1"
  # Get relative path from repo root
  relative_path="${dir_path#"$REPO_ROOT"/}"

  # Check if there are any staged changes in this directory
  git diff --cached --name-only | grep -q "^${relative_path}/" && return 0
  return 1
}

echo "Finding directories with Makefiles and staged changes..."
FOUND_DIRECTORIES=0
EXIT_CODE=0

# Create a temporary file with mktemp
TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

# Use find to locate all Makefiles
find "${REPO_ROOT}" -type f -name "Makefile" -not -path "*/\.*" > "$TEMP_FILE"
while read -r makefile; do
  DIR=$(dirname "$makefile")
  RELATIVE_DIR="${DIR#"$REPO_ROOT"/}"

  # Only process directories with staged changes
  if has_staged_changes "${DIR}"; then
    FOUND_DIRECTORIES=1
    if has_pre_commit_target "${DIR}"; then
      echo "Running pre-commit for directory with staged changes: ${RELATIVE_DIR}"
      # Change to the directory and run make pre-commit
      (cd "${DIR}" && make pre-commit)
      CURRENT_EXIT_CODE=$?

      if [ $CURRENT_EXIT_CODE -ne 0 ]; then
        echo "Pre-Commit failed for directory: ${RELATIVE_DIR}"
        EXIT_CODE=1
      fi
    else
      echo "No pre-commit target found for directory with staged changes: ${RELATIVE_DIR}"
    fi
  fi
done < "$TEMP_FILE"

# Check if any directories were processed
if [ $FOUND_DIRECTORIES -eq 0 ]; then
  echo "No directories with Makefiles and staged changes found"
  exit 0
fi

if [ $EXIT_CODE -eq 0 ]; then
  echo "All pre-commit checks passed"
  exit 0
else
  echo "One or more pre-commit checks failed"
  exit 1
fi
