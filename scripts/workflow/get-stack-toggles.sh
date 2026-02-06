#!/usr/bin/env bash
set -euo pipefail

# Usage: get-stack-toggles.sh <path-to-stacks.tfvars>
# Reads toggle values from the provided tfvars file and writes outputs
# suitable for GitHub Actions via the GITHUB_OUTPUT file.

TFVARS_FILE="${1:-}"

if [[ -z "${TFVARS_FILE}" || ! -f "${TFVARS_FILE}" ]]; then
  if [[ -z "${TFVARS_FILE}" ]]; then
    echo "Error: Path to tfvars file is required as the first argument" >&2
  else
    echo "Warning: Stack toggles file not found: ${TFVARS_FILE}"
  fi
  echo "Defaulting stacks to enabled"
  echo "ui_enabled=true" >> "$GITHUB_OUTPUT"
  echo "read_only_viewer_enabled=true" >> "$GITHUB_OUTPUT"
  echo "open_search_enabled=true" >> "$GITHUB_OUTPUT"
  echo "athena_enabled=true" >> "$GITHUB_OUTPUT"
  exit 0
fi

UI_ENABLED=$(awk -F'= *' '/^ui_stack_enabled[[:space:]]*=/ {print $2}' "$TFVARS_FILE" | awk '{print $1}' | tr -d '"' | tr '[:upper:]' '[:lower:]')
UI_ENABLED=${UI_ENABLED:-true}
READ_ONLY_VIEWER_ENABLED=$(awk -F'= *' '/^read_only_viewer_stack_enabled[[:space:]]*=/ {print $2}' "$TFVARS_FILE" | awk '{print $1}' | tr -d '"' | tr '[:upper:]' '[:lower:]')
READ_ONLY_VIEWER_ENABLED=${READ_ONLY_VIEWER_ENABLED:-true}
OPEN_SEARCH_ENABLED=$(awk -F'= *' '/^opensearch_stack_enabled[[:space:]]*=/ {print $2}' "$TFVARS_FILE" | awk '{print $1}' | tr -d '"' | tr '[:upper:]' '[:lower:]')
OPEN_SEARCH_ENABLED=${OPEN_SEARCH_ENABLED:-true}
ATHENA_ENABLED=$(awk -F'= *' '/^athena_stack_enabled[[:space:]]*=/ {print $2}' "$TFVARS_FILE" | awk '{print $1}' | tr -d '"' | tr '[:upper:]' '[:lower:]')
ATHENA_ENABLED=${ATHENA_ENABLED:-true}

echo "ui_enabled=$UI_ENABLED" >> "$GITHUB_OUTPUT"
echo "athena_enabled=$ATHENA_ENABLED" >> "$GITHUB_OUTPUT"

echo "UI Stack Enabled: $UI_ENABLED"
echo "Read Only Viewer Stack Enabled: $READ_ONLY_VIEWER_ENABLED"
echo "Open Search Stack Enabled: $OPEN_SEARCH_ENABLED"
echo "Athena Stack Enabled: $ATHENA"
echo "Read Only Viewer Stack Enabled: $READ_ONLY_VIEWER_ENABLED"
echo "Open Search Stack Enabled: $OPEN_SEARCH_ENABLED"
