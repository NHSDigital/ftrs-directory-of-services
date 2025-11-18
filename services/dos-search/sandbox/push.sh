#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[push.sh] %s\n' "$1"
}

die() {
  log "ERROR: $1" >&2
  exit 1
}

usage() {
  cat >&2 <<'EOF'
Usage: push.sh <api-name> <local-image> <remote-image-name> <remote-image-tag>
Environment:
  ACCESS_TOKEN   Bearer token used when calling the Proxygen API
  PUSH_LATEST    Optional flag (default: true) to mirror image to :latest
  PUSH_RETRIES   Optional retry attempts for docker push (default: 3)
EOF
  exit 1
}

API_NAME="${1:-}"
LOCAL_IMAGE="${2:-}"
REMOTE_IMAGE_NAME="${3:-}"
REMOTE_IMAGE_TAG="${4:-}"
ACCESS_TOKEN="${ACCESS_TOKEN:-}"
PUSH_LATEST="${PUSH_LATEST:-true}"
PUSH_RETRIES=$(( ${PUSH_RETRIES:-3} ))

if [[ -z "$API_NAME" || -z "$LOCAL_IMAGE" || -z "$REMOTE_IMAGE_NAME" || -z "$REMOTE_IMAGE_TAG" ]]; then
  usage
fi

if [[ -z "$ACCESS_TOKEN" ]]; then
  die "ACCESS_TOKEN is not set"
fi

if ! docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then
  die "Local image $LOCAL_IMAGE not found"
fi

for dep in curl jq docker; do
  command -v "$dep" >/dev/null 2>&1 || die "Required dependency missing: $dep"
done

BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"

log "Fetching Docker token for API: $API_NAME via $BASE_URL..."
TOKEN_RESPONSE=$(curl -fsS --request GET \
  --url "${BASE_URL}/apis/${API_NAME}/docker-token" \
  --header "Authorization: Bearer ${ACCESS_TOKEN}") || die "Failed to reach Proxygen API"

LOGIN_CMD=$(echo "$TOKEN_RESPONSE" | jq -r '.loginCommand // empty')
REGISTRY=$(echo "$TOKEN_RESPONSE" | jq -r '.registry // empty')

if [[ -z "$LOGIN_CMD" || -z "$REGISTRY" ]]; then
  die "Malformed response from Proxygen: $TOKEN_RESPONSE"
fi

log "Logging in to Docker registry: $REGISTRY"
eval "$LOGIN_CMD"

REMOTE_COMMIT_TAG="${REGISTRY}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
REMOTE_LATEST_TAG="${REGISTRY}/${REMOTE_IMAGE_NAME}:latest"

retry_push() {
  local tag="$1"
  local attempt=1
  until docker push "$tag"; do
    if (( attempt >= PUSH_RETRIES )); then
      die "docker push $tag failed after $PUSH_RETRIES attempts"
    fi
    log "push $tag failed (attempt $attempt), retrying..."
    sleep $(( attempt * 2 ))
    (( attempt++ ))
  done
}

log "Tagging ${LOCAL_IMAGE} as ${REMOTE_COMMIT_TAG}"
docker tag "$LOCAL_IMAGE" "$REMOTE_COMMIT_TAG"
retry_push "$REMOTE_COMMIT_TAG"

if [[ "$PUSH_LATEST" == "true" ]]; then
  log "Tagging ${LOCAL_IMAGE} as ${REMOTE_LATEST_TAG}"
  docker tag "$LOCAL_IMAGE" "$REMOTE_LATEST_TAG"
  retry_push "$REMOTE_LATEST_TAG"
else
  log "Skipping latest tag push (PUSH_LATEST=$PUSH_LATEST)"
fi

log "Image pushed successfully to ${REMOTE_COMMIT_TAG}${PUSH_LATEST:+ and latest}"
