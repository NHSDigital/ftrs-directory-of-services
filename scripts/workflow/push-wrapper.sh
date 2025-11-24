#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log() { printf '[push-wrapper] %s\n' "$1"; }
err() { printf '[push-wrapper] ERROR: %s\n' "$1" >&2; }

usage() {
  cat <<'EOF' >&2
Usage: push-wrapper.sh <api-name> <local-image> <remote-image-name> <remote-image-tag> <environment>

Captures an APIM token (in-memory) and invokes push-to-ecr.sh with ACCESS_TOKEN exported.

Environment (optional):
  AWS_REGION     (read from environment if set)

EOF
  exit 2
}

API_NAME="${1:-}"
LOCAL_IMAGE="${2:-}"
REMOTE_NAME="${3:-}"
REMOTE_TAG="${4:-}"
ENVIRONMENT="${5:-}"
AWS_REGION="${AWS_REGION:-}"

if [ -z "$API_NAME" ] || [ -z "$LOCAL_IMAGE" ] || [ -z "$REMOTE_NAME" ] || [ -z "$REMOTE_TAG" ] || [ -z "$ENVIRONMENT" ]; then
  usage
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GET_APIM_TOKEN_SCRIPT="$SCRIPT_DIR/get-apim-token.sh"
PUSH_SCRIPT="$SCRIPT_DIR/push-to-ecr.sh"

# Ensure ENVIRONMENT is present in the process environment for child scripts
export ENVIRONMENT
export ENV="$ENVIRONMENT"

if [ ! -f "$GET_APIM_TOKEN_SCRIPT" ]; then
  err "token script not found: $GET_APIM_TOKEN_SCRIPT"
  exit 1
fi
if [ ! -x "$GET_APIM_TOKEN_SCRIPT" ]; then
  chmod +x "$GET_APIM_TOKEN_SCRIPT" >/dev/null 2>&1 || true
fi
if [ ! -f "$PUSH_SCRIPT" ]; then
  err "push script not found: $PUSH_SCRIPT"
  exit 1
fi
if [ ! -x "$PUSH_SCRIPT" ]; then
  chmod +x "$PUSH_SCRIPT" >/dev/null 2>&1 || true
fi

log "Requesting APIM token for API: $API_NAME"
TOKEN_OUTPUT=$(API_NAME="$API_NAME" ENV="$ENVIRONMENT" ENVIRONMENT="$ENVIRONMENT" AWS_REGION="$AWS_REGION" /bin/bash "$GET_APIM_TOKEN_SCRIPT" 2>&1)
TOKEN_RC=$?

if [ $TOKEN_RC -ne 0 ]; then
  err "get-apim-token.sh failed with exit code $TOKEN_RC: $TOKEN_OUTPUT"
  exit 1
fi

ACCESS_TOKEN=$(printf '%s' "$TOKEN_OUTPUT" | tr -d '\r\n')

if [ -z "$ACCESS_TOKEN" ]; then
  err "Failed to obtain ACCESS_TOKEN from get-apim-token.sh stdout"
  exit 1
fi

export ACCESS_TOKEN
export AWS_REGION

log "Invoking push script"
exec "$PUSH_SCRIPT" "$API_NAME" "$LOCAL_IMAGE" "$REMOTE_NAME" "$REMOTE_TAG"
