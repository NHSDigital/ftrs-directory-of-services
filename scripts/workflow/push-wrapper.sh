#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log() { printf '[push-wrapper] %s\n' "$1"; return 0; }
err() { printf '[push-wrapper] ERROR: %s\n' "$1" >&2; return 0; }

usage() {
  cat <<'EOF' >&2
Usage: push-wrapper.sh <api-name> <local-image> <remote-image-name> <remote-image-tag> [version-tag]

Reads DOCKER_TOKEN from the environment and invokes push-to-ecr.sh with the
provided metadata.

Environment (optional):
  API_NAME       (used if the first positional argument is omitted)
  LOCAL_IMAGE    (used if the second positional argument is omitted)
  REMOTE_NAME    (used if the third positional argument is omitted)
  REMOTE_TAG     (used if the fourth positional argument is omitted)
  VERSION_TAG    (used if the fifth positional argument is omitted)
  DOCKER_TOKEN   (must be set)

EOF
  exit 2
}

API_NAME="${1:-${API_NAME:-}}"
LOCAL_IMAGE="${2:-${LOCAL_IMAGE:-}}"
REMOTE_NAME="${3:-${REMOTE_NAME:-}}"
REMOTE_TAG="${4:-${REMOTE_TAG:-}}"
VERSION_TAG="${5:-${VERSION_TAG:-}}"
DOCKER_TOKEN="${DOCKER_TOKEN:-}"

if [[ -z "$API_NAME" || -z "$LOCAL_IMAGE" || -z "$REMOTE_NAME" || -z "$REMOTE_TAG" ]]; then
  usage
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PUSH_SCRIPT="$SCRIPT_DIR/push-to-ecr.sh"

if [[ ! -f "$PUSH_SCRIPT" ]]; then
  err "push script not found: $PUSH_SCRIPT"
  exit 1
fi
if [[ ! -x "$PUSH_SCRIPT" ]]; then
  chmod +x "$PUSH_SCRIPT" >/dev/null 2>&1 || true
fi

export DOCKER_TOKEN

log "Invoking push script"
exec "$PUSH_SCRIPT" "$API_NAME" "$LOCAL_IMAGE" "$REMOTE_NAME" "$REMOTE_TAG" "$VERSION_TAG"
