#!/bin/bash

# Script to generate AWS AppConfig Feature Flags JSON from the toggle registry
# This script reads the toggle registry YAML and generates environment-specific feature flags

# fail on first error
set -e

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
TOGGLE_REGISTRY_FILE="${TOGGLE_REGISTRY_FILE:-"$ROOT_DIR/infrastructure/toggles/toggle-registry.yaml"}"
OUTPUT_FILE="${OUTPUT_FILE:-"$ROOT_DIR/infrastructure/toggles/feature-flags.json"}"
CREATED_DATE="${CREATED_DATE:-$(date -u +"%Y-%m-%dT%H:%M:%SZ")}"

# Validate required environment variables
if [ -z "$ENVIRONMENT" ]; then
  echo "Error: ENVIRONMENT environment variable is required"
  echo "Usage: ENVIRONMENT=dev $0"
  exit 1
fi

# Check if toggle registry file exists
if [ ! -f "$TOGGLE_REGISTRY_FILE" ]; then
  echo "Error: Toggle registry file not found: $TOGGLE_REGISTRY_FILE"
  exit 1
fi

echo "======================================"
echo "Generating Feature Flags"
echo "======================================"
echo "Environment: $ENVIRONMENT"
echo "Toggle Registry: $TOGGLE_REGISTRY_FILE"
echo "Output File: $OUTPUT_FILE"
echo "Created Date: $CREATED_DATE"
echo "======================================"

# Generate the feature flags JSON using Python script
GENERATED_FILE=$(ENVIRONMENT="$ENVIRONMENT" \
  TOGGLE_REGISTRY_FILE="$TOGGLE_REGISTRY_FILE" \
  OUTPUT_FILE="$OUTPUT_FILE" \
  CREATED_DATE="$CREATED_DATE" \
  python3 "$SCRIPT_DIR/generate_feature_flags.py")

if [ $? -eq 0 ]; then
  echo "✓ Feature flags generated successfully: $GENERATED_FILE"

  # Display a summary of the generated file
  if [ -f "$GENERATED_FILE" ]; then
    FLAG_COUNT=$(python3 -c "import json; f=open('$GENERATED_FILE'); data=json.load(f); print(len(data.get('flags', {})))")
    echo "✓ Total flags generated: $FLAG_COUNT"

    # Show enabled flags
    ENABLED_COUNT=$(python3 -c "import json; f=open('$GENERATED_FILE'); data=json.load(f); print(sum(1 for v in data.get('values', {}).values() if v.get('enabled')))")
    echo "✓ Flags enabled in $ENVIRONMENT: $ENABLED_COUNT"
  fi
else
  echo "✗ Failed to generate feature flags"
  exit 1
fi

echo "======================================"
