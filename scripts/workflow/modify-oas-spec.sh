#!/bin/bash

# Script to modify OAS spec with workspace information
# Required environment variables: API_NAME, PROXY_ENV
# Optional environment variables: WORKSPACE (when specified deploys a workspaced proxy)
# Outputs the path to the modified spec file to stdout

set -e

# Validate required environment variables
if [ -z "$API_NAME" ]; then
    echo "Error: API_NAME environment variable is required" >&2
    exit 1
fi

if [ -z "$PROXY_ENV" ]; then
    echo "Error: PROXY_ENV environment variable is required" >&2
    exit 1
fi

# Set the spec file path (relative to repository root)
SPEC_FILE="docs/specification/${API_NAME}.yaml"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Error: Spec file not found at $SPEC_FILE" >&2
    echo "Current directory: $(pwd)" >&2
    echo "Looking for file at: $(realpath $SPEC_FILE 2>/dev/null || echo $SPEC_FILE)" >&2
    exit 1
fi

if [ -n "$WORKSPACE" ]; then
    echo "Modifying OAS spec for workspace: $WORKSPACE" >&2
else
    echo "Modifying OAS spec (no workspace)" >&2
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Modify the spec
echo "Processing specification file..." >&2
MODIFIED_SPEC=$(WORKSPACE="$WORKSPACE" API_NAME="$API_NAME" SPEC_FILE="$SPEC_FILE" PROXY_ENV="$PROXY_ENV" python3 "$SCRIPT_DIR/modify_spec.py")

if [ ! -f "$MODIFIED_SPEC" ]; then
    echo "Error: Failed to create modified spec" >&2
    exit 1
fi

echo "Modified spec created successfully as JSON" >&2

# Debug: Show the first server URL from the modified spec
echo "Checking modified server URLs..." >&2
python3 -c "import json; f=open('$MODIFIED_SPEC'); spec=json.load(f); print(f\"First server URL: {spec['servers'][0]['url']}\", file=__import__('sys').stderr)"

# Output the path to the modified spec file to stdout
echo "$MODIFIED_SPEC"
