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
  local dir_path="$1"
  # Get relative path from repo root
  local relative_path="${dir_path#"$REPO_ROOT"/}"

  # Check if there are any staged changes in this directory
  git diff --cached --name-only | grep -q "^${relative_path}/" && return 0
  return 1
}

# Function to run make pre-commit for a directory
run_make_pre_commit() {
  local dir="$1"
  local relative_dir="${dir#"$REPO_ROOT"/}"

  echo "Running make pre-commit for directory with staged changes: ${relative_dir}"
  # Change to the directory and run make pre-commit
  if (cd "${dir}" && make pre-commit); then
    return 0
  else
    echo "make pre-commit failed for directory: ${relative_dir}"
    return 1
  fi
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
      if ! run_make_pre_commit "${DIR}"; then
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
elif [ $EXIT_CODE -eq 0 ]; then
  echo "All pre-commit checks passed"
else
  echo "One or more pre-commit checks failed"
fi

exit $EXIT_CODE
