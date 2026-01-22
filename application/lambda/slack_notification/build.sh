#!/usr/bin/env bash
# Build and package the Slack notification Lambda function

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
OUTPUT_DIR="${SCRIPT_DIR}"

# Clean previous build
rm -rf "${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

# Copy the Lambda function code
cp "${SCRIPT_DIR}/index.py" "${BUILD_DIR}/"

# Install dependencies to build directory
pip install -r "${SCRIPT_DIR}/requirements.txt" -t "${BUILD_DIR}" --quiet

# Create ZIP file
cd "${BUILD_DIR}"
zip -r -q "${OUTPUT_DIR}/slack_notification.zip" .
cd "${SCRIPT_DIR}"

# Clean up build directory
rm -rf "${BUILD_DIR}"

echo "✓ Successfully created slack_notification.zip"
