#!/usr/bin/env bash
set -euo pipefail

# Usage: push-wrapper.sh <get-apim-token-script> <push-script> <api_name> <push_image> <image_tag> <env> <aws_region>
GET_TOKEN_SCRIPT="$1"
PUSH_SCRIPT="$2"
API_NAME="$3"
PUSH_IMAGE="$4"
IMAGE_TAG="$5"
ENVIRONMENT_ARG="${6:-}
"
AWS_REGION_ARG="${7:-}"

# Prefer externally provided ACCESS_TOKEN
if [ -n "${ACCESS_TOKEN:-}" ]; then
  echo "Using ACCESS_TOKEN from environment (len=$(echo -n "$ACCESS_TOKEN" | wc -c))"
else
  echo "No ACCESS_TOKEN in environment; attempting to obtain one using token script"
  # Ensure python deps
  python -m pip install --upgrade pip || true
  python -m pip install "PyJWT>=2.0.0" "cryptography>=3.4" || true

  if [ ! -x "$GET_TOKEN_SCRIPT" ]; then
    if [ -f "$GET_TOKEN_SCRIPT" ]; then
      chmod +x "$GET_TOKEN_SCRIPT" || true
    else
      echo "Token script not found: $GET_TOKEN_SCRIPT" >&2
      exit 1
    fi
  fi

  # Run token script and capture stdout (let stderr show for diagnostics)
  ACCESS_TOKEN_OUTPUT="$($GET_TOKEN_SCRIPT "$API_NAME" "$ENVIRONMENT_ARG" "$AWS_REGION_ARG" 2>&1 || true)"

  # token script may print token or JSON; attempt to extract token if it's on stdout
  ACCESS_TOKEN="$ACCESS_TOKEN_OUTPUT"
  if [ -z "${ACCESS_TOKEN:-}" ]; then
    echo "Failed to obtain ACCESS_TOKEN from token script" >&2
    exit 1
  fi
fi

# Export and exec push script
export ACCESS_TOKEN
exec "$PUSH_SCRIPT" "$API_NAME" "$PUSH_IMAGE" "$API_NAME" "$IMAGE_TAG"

