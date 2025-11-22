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
  ACCESS_TOKEN   Bearer token for APIM (required). Provide this via the environment (preferred for in-memory flow).

Optional:
  PUSH_LATEST    Optional flag (default: false) to also push a :latest tag
  PUSH_RETRIES   Optional retry attempts for docker push (default: 3)

Security/notes:
  - Prefer providing the token in-memory via environment to avoid writing credentials to disk.
  - Avoid printing the full token in shared CI logs; use masked logging for debugging.

Example:
  ACCESS_TOKEN=eyJ... ./scripts/workflow/push-to-ecr.sh dos-search dos-search:local dos-search 123456

EOF
  exit 1
}

API_NAME="${1:-}"
LOCAL_IMAGE="${2:-}"
REMOTE_IMAGE_NAME="${3:-}"
REMOTE_IMAGE_TAG="${4:-}"

# Require ACCESS_TOKEN from environment (in-memory flow only)
PUSH_LATEST="${PUSH_LATEST:-false}"
PUSH_RETRIES=$(( ${PUSH_RETRIES:-3} ))

# ACCESS_TOKEN must be supplied by the caller (wrapper or Makefile)
if [ -z "${ACCESS_TOKEN:-}" ]; then
  die "ACCESS_TOKEN not provided: capture with get-apim-token.sh and provide via ACCESS_TOKEN environment variable"
else
  log "Using ACCESS_TOKEN from environment"
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

log "Listing images for repository ${REMOTE_IMAGE_NAME} at ${REGISTRY_HOST} using skopeo"
if command -v skopeo >/dev/null 2>&1; then
  TMP_OUT="/tmp/skopeo_out.$$"
  if skopeo list-tags --tls-verify=false docker://${REGISTRY_HOST}/${REMOTE_IMAGE_NAME} >"${TMP_OUT}" 2>&1; then
    # Extract tags
    if command -v jq >/dev/null 2>&1; then
      TAGS=$(jq -r '.Tags[]' "${TMP_OUT}" 2>/dev/null || true)
    else
      # crude fallback to parse tags from JSON
      TAGS=$(grep -o '"Tags"[[:space:]]*:[[:space:]]*\[[^]]*\]' "${TMP_OUT}" | sed -E 's/.*\[|\].*//g' | tr -d '" ' | tr ',' '\n' || true)
    fi

    if [ -z "${TAGS}" ]; then
      log "No tags found for ${REMOTE_IMAGE_NAME} (empty tag list)"
      cat "${TMP_OUT}"
    else
      # Print header (include fully-qualified IMAGE column)
      printf '%s\t%s\t%s\t%s\n' "IMAGE" "TAG" "DIGEST" "PUSHED_AT"
      # Inspect each tag and print image (registry/repo:tag), tag, digest and created timestamp
      for tag in ${TAGS}; do
        INFO_TMP="/tmp/skopeo_inspect.$$"
        IMAGE_FQ="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${tag}"
        if skopeo inspect --tls-verify=false docker://${IMAGE_FQ} >"${INFO_TMP}" 2>/dev/null; then
          if command -v jq >/dev/null 2>&1; then
            DIGEST=$(jq -r '.Digest // empty' "${INFO_TMP}" 2>/dev/null || echo "")
            CREATED=$(jq -r '.Created // empty' "${INFO_TMP}" 2>/dev/null || echo "")
          else
            DIGEST=$(grep -o '"Digest"[[:space:]]*:[[:space:]]*"[^"]*"' "${INFO_TMP}" | head -1 | sed -E 's/.*:"?([^"}]+)"?/\1/' || echo "")
            CREATED=$(grep -o '"Created"[[:space:]]*:[[:space:]]*"[^"]*"' "${INFO_TMP}" | head -1 | sed -E 's/.*:"?([^"}]+)"?/\1/' || echo "")
          fi
          printf '%s\t%s\t%s\t%s\n' "${IMAGE_FQ}" "${tag}" "${DIGEST:-}" "${CREATED:-}"
        else
          printf '%s\t%s\t%s\t%s\n' "${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${tag}" "${tag}" "(inspect failed)" ""
        fi
        rm -f "${INFO_TMP}" 2>/dev/null || true
      done | (command -v column >/dev/null 2>&1 && column -t -s $'\t' || cat)
    fi
  else
    log "skopeo failed to list tags for ${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}; raw output follows"
    cat "${TMP_OUT}" 2>/dev/null || true
  fi
  rm -f "${TMP_OUT}" || true
else
  log "skopeo not installed; cannot list remote images via registry auth"
  log "Install 'skopeo' on the runner or use the AWS CLI (requires AWS creds for registry account)"
fi
