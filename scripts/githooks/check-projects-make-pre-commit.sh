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
EXIT_CODE=0
FOUND_DIRECTORIES=0

# Use a standard find command and process the output directly
find "${REPO_ROOT}" -type f -name "Makefile" -not -path "*/\.*" | while read -r makefile; do
  DIR=$(dirname "$makefile")
  DIR_NAME=$(basename "${DIR}")
  RELATIVE_DIR="${DIR#"$REPO_ROOT"/}"

  # Only process directories with staged changes
  if has_staged_changes "${DIR}"; then
    FOUND_DIRECTORIES=1
    if has_pre_commit_target "${DIR}"; then
      echo "Running pre-commit for directory with staged changes: ${RELATIVE_DIR}"
      # Change to the directory and run make pre-commit
      (cd "${DIR}" && make pre-commit) || {
        echo "Pre-Commit failed for directory: ${RELATIVE_DIR}"
        EXIT_CODE=1
      }
    else
      echo "No pre-commit target found for directory with staged changes: ${RELATIVE_DIR}"
    fi
  fi
done

# Since we're using a pipeline with 'while', we need to capture the exit code differently
# Store the original EXIT_CODE value
ORIGINAL_EXIT_CODE=$EXIT_CODE

# Check if any directories were processed
if [ $FOUND_DIRECTORIES -eq 0 ]; then
  echo "No directories with Makefiles and staged changes found"
else
  echo "Completed"
fi

exit $ORIGINAL_EXIT_CODE
