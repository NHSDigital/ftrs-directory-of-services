#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[push-to-ecr] %s\n' "$1"
}

die() {
  log "ERROR: $1" >&2
  exit 1
}

usage() {
  cat >&2 <<'EOF'
Usage: push-to-ecr.sh <api-name> <local-image> <remote-image-name> <remote-image-tag>

Required/important environment:
  OUTPUT_FILE    Path to a file containing the APIM bearer token (preferred). The script reads the token from this file.
  ENVIRONMENT    Name of the environment (e.g., dev). When OUTPUT_FILE is not set the script derives the canonical
                  token path as /tmp/ftrs_apim_<api>_<env> (so ENVIRONMENT must be set in that case).

Optional:
  PUSH_LATEST    Optional flag (default: false) to also push a :latest tag
  PUSH_RETRIES   Optional retry attempts for docker push (default: 3)

Security/notes:
  - The token file should contain only the bearer token and be readable only by the runner (e.g. chmod 600).
  - The Makefile or token generator should create and clean up the token file; this script will fail if the file
    is missing or empty.

Example:
  OUTPUT_FILE=/tmp/ftrs_apim_dos-search_dev ./scripts/workflow/push-to-ecr.sh dos-search dos-search:local dos-search 123456

EOF
  exit 1
}

API_NAME="${1:-}"
LOCAL_IMAGE="${2:-}"
REMOTE_IMAGE_NAME="${3:-}"
REMOTE_IMAGE_TAG="${4:-}"
## ACCESS_TOKEN will be loaded from a token file below; do not rely on env
unset ACCESS_TOKEN 2>/dev/null || true
PUSH_LATEST="${PUSH_LATEST:-false}"
PUSH_RETRIES=$(( ${PUSH_RETRIES:-3} ))

# Always read ACCESS_TOKEN from a token file produced by the token script.
# Prefer explicit OUTPUT_FILE; otherwise require ENVIRONMENT to build the canonical filename.
if [ -n "${OUTPUT_FILE:-}" ]; then
  TOKEN_FILE="${OUTPUT_FILE}"
else
  # require ENVIRONMENT when OUTPUT_FILE not provided
  if [ -n "${ENVIRONMENT:-}" ]; then
    TOKEN_FILE="/tmp/ftrs_apim_${API_NAME}_${ENVIRONMENT}"
  else
    die "Token file path ambiguous: set OUTPUT_FILE or ENVIRONMENT"
  fi
fi

if [ -s "${TOKEN_FILE}" ]; then
  # Read token and trim any trailing newline safely
  ACCESS_TOKEN="$(tr -d '\r\n' < "${TOKEN_FILE}")"
  log "Loaded ACCESS_TOKEN from token file: ${TOKEN_FILE}"
else
  die "Token file not found or empty: ${TOKEN_FILE} (ensure get-apim-token.sh wrote the token to this file)"
fi

if [[ -z "$API_NAME" || -z "$LOCAL_IMAGE" || -z "$REMOTE_IMAGE_NAME" || -z "$REMOTE_IMAGE_TAG" ]]; then
  usage
fi

if [[ -z "${ACCESS_TOKEN}" ]]; then
  die "ACCESS_TOKEN is not set"
fi

for dep in curl jq docker; do
  command -v "$dep" >/dev/null 2>&1 || die "Required dependency missing: $dep"
done

if ! docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then
  die "Local image $LOCAL_IMAGE not found"
fi

BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"

log "Fetching Docker token for API: $API_NAME via $BASE_URL..."
TOKEN_RESPONSE=$(curl -fsS --request GET \
  --url "${BASE_URL}/apis/${API_NAME}/docker-token" \
  --header "Authorization: Bearer ${ACCESS_TOKEN}") || die "Failed to reach Proxygen API"

USER=$(echo "$TOKEN_RESPONSE" | jq -r '.user // empty')
PASSWORD=$(echo "$TOKEN_RESPONSE" | jq -r '.password // empty')
REGISTRY=$(echo "$TOKEN_RESPONSE" | jq -r '.registry // empty')

if [[ -z "$REGISTRY" ]]; then
  die "Malformed response from Proxygen: missing registry"
fi

REGISTRY_HOST=$(echo "$REGISTRY" | sed -E 's#^https?://##' | sed -E 's#/$##')


if [[ -n "$USER" && -n "$PASSWORD" ]]; then
  log "Logging in to Docker registry (user/password) at: $REGISTRY_HOST"
  echo "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"
else
  die "No usable login credentials returned from Proxygen; expected 'user' and 'password' in response"
fi

REMOTE_COMMIT_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
REMOTE_LATEST_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:latest"

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
