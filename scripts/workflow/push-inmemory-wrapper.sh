#!/usr/bin/env bash
set -euo pipefail

# In-memory wrapper: capture APIM token from get-apim-token.sh stdout and call push-to-ecr.sh with ACCESS_TOKEN in env
# Usage: ./push-inmemory-wrapper.sh <api-name> <local-image> <remote-image-name> <remote-image-tag>

API_NAME="${1:-dos-search}"
LOCAL_IMAGE="${2:-${API_NAME}:local}"
REMOTE_NAME="${3:-${API_NAME}}"
REMOTE_TAG="${4:-latest}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
AWS_REGION="${AWS_REGION:-eu-west-2}"

GET_APIM_TOKEN_SCRIPT="$(pwd)/scripts/workflow/get-apim-token.sh"
PUSH_SCRIPT="$(pwd)/scripts/workflow/push-to-ecr.sh"

if [ ! -f "$GET_APIM_TOKEN_SCRIPT" ]; then
  echo "get-apim-token script not found: $GET_APIM_TOKEN_SCRIPT" >&2
  exit 1
fi

# Capture token from stdout, avoid writing file
ACCESS_TOKEN="$(${GET_APIM_TOKEN_SCRIPT} >/dev/null 2>&1 || true)"
# Above line intentionally quiet; we'll run properly below

# Run the token command and capture stdout (status messages go to stderr from the token script)
ACCESS_TOKEN="$(API_NAME="$API_NAME" ENV="$ENVIRONMENT" AWS_REGION="$AWS_REGION" WRITE_TOKEN_FILE=false /bin/bash "$GET_APIM_TOKEN_SCRIPT" | tr -d '\r\n')"

if [ -z "$ACCESS_TOKEN" ]; then
  echo "Failed to obtain ACCESS_TOKEN from get-apim-token.sh stdout" >&2
  exit 1
fi

# Export token in environment and invoke push script in the same process
export ACCESS_TOKEN
export ENVIRONMENT
export AWS_REGION

# Call push script with ACCESS_TOKEN available via env
"$PUSH_SCRIPT" "$API_NAME" "$LOCAL_IMAGE" "$REMOTE_NAME" "$REMOTE_TAG"

