#!/bin/bash

# Script to generate stack toggle tfvars files from the toggle registry
# This script reads the toggle registry YAML and generates environment-specific stack.auto.tfvars files

# fail on first error
set -e

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
TOGGLE_REGISTRY_FILE="${TOGGLE_REGISTRY_FILE:-"$ROOT_DIR/infrastructure/toggles/toggle-registry.yaml"}"
TOGGLE_DIR="${TOGGLE_DIR:-"$ROOT_DIR/infrastructure/toggles"}"

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

# Check if output directory exists
if [ ! -d "$TOGGLE_DIR" ]; then
  echo "Error: Output directory not found: $TOGGLE_DIR"
  exit 1
fi

echo "======================================"
echo "Generating Stack Toggles"
echo "======================================"
echo "Environment: $ENVIRONMENT"
echo "Toggle Registry: $TOGGLE_REGISTRY_FILE"
echo "Output Directory: $TOGGLE_DIR"
echo "======================================"

# Generate the stack toggles using Python script
GENERATED_FILE=$(ENVIRONMENT="$ENVIRONMENT" \
  TOGGLE_REGISTRY_FILE="$TOGGLE_REGISTRY_FILE" \
  TOGGLE_DIR="$TOGGLE_DIR" \
  python3 "$SCRIPT_DIR/generate-stack-toggles.py")

# Check if the generation was successful
if [ $? -ne 0 ]; then
  echo "✗ Failed to generate stack toggles for environment: $ENVIRONMENT"
  echo "✗ Python script exited with error code: $?"
  exit 1
fi

# Use the returned path from the Python script
if [ -n "$GENERATED_FILE" ] && [ -f "$GENERATED_FILE" ]; then
  echo "✓ Stack toggles generated successfully: $GENERATED_FILE"

  # Display a summary of the generated file
  TOGGLE_COUNT=$(grep -c "^[a-zA-Z_]" "$GENERATED_FILE" || echo "0")
  echo "✓ Total stack toggles generated: $TOGGLE_COUNT"

  # Show which toggles are enabled
  ENABLED_COUNT=$(grep -c "= true" "$GENERATED_FILE" || echo "0")
  echo "✓ Stack toggles enabled in $ENVIRONMENT: $ENABLED_COUNT"
else
  echo "ℹ No stack toggles applicable for $ENVIRONMENT; no file created"
fi

echo "======================================"
