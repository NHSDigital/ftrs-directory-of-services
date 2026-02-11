#!/bin/bash

# Script to prepare coverage files for SonarCloud analysis
# Downloads and flattens coverage XML files from GitHub Actions artifacts

set -e

ARTIFACTS_DIR="${ARTIFACTS_DIR:-coverage-artifacts}"
OUTPUT_DIR="${OUTPUT_DIR:-coverage}"

echo "=== Downloaded artifact structure ==="
find "$ARTIFACTS_DIR" -type f -o -type d 2>/dev/null | head -50 || echo "No artifacts found"

# Create flat coverage directory with actual XML files
mkdir -p "$OUTPUT_DIR"

# Handle both direct XML files and zipped XML files
find "$ARTIFACTS_DIR" -type f -name '*.xml' -exec cp {} "$OUTPUT_DIR/" \;
find "$ARTIFACTS_DIR" -type f -name '*.xml.zip' -exec sh -c 'unzip -o -j "$1" -d '"$OUTPUT_DIR"'/' _ {} \;

echo "=== Flattened coverage directory ==="
ls -la "$OUTPUT_DIR/" || echo "No coverage files found"

# Build comma-separated list of coverage files
FILES=$(find "$OUTPUT_DIR" -maxdepth 1 -type f -name '*.xml' 2>/dev/null | paste -sd "," - || echo "")
if [ -z "$FILES" ]; then
  echo "WARNING: No coverage XML files found!"
else
  echo "Coverage files for SonarCloud: $FILES"
fi

# Output the files list for GitHub Actions
echo "$FILES"
