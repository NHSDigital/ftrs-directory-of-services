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

Example:
  ACCESS_TOKEN=eyJ... ./scripts/workflow/push-to-ecr.sh dos-search dos-search:local dos-search 123456
EOF
  exit 1
}

API_NAME="${1:-}"
LOCAL_IMAGE="${2:-}"
REMOTE_IMAGE_NAME="${3:-}"
REMOTE_IMAGE_TAG="${4:-}"

PUSH_LATEST_RAW="${PUSH_LATEST:-false}"
PUSH_LATEST_LC=$(printf '%s' "$PUSH_LATEST_RAW" | tr '[:upper:]' '[:lower:]')
case "$PUSH_LATEST_LC" in
  1|true|yes) PUSH_LATEST="true" ;;
  *) PUSH_LATEST="false" ;;
esac

PUSH_RETRIES=$(( ${PUSH_RETRIES:-3} ))

if [ -z "${ACCESS_TOKEN:-}" ]; then
  die "ACCESS_TOKEN not provided"
fi

if [ -z "$API_NAME" ] || [ -z "$LOCAL_IMAGE" ] || [ -z "$REMOTE_IMAGE_NAME" ] || [ -z "$REMOTE_IMAGE_TAG" ]; then
  usage
fi

for dep in curl jq docker; do
  command -v "$dep" >/dev/null 2>&1 || die "required dependency missing: $dep"
done

if ! docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then
  die "Local image $LOCAL_IMAGE not found"
fi

BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"
log "Requesting registry credentials from APIM for API: $API_NAME"
TOKEN_RESPONSE=$(curl -fsS --request GET --url "${BASE_URL}/apis/${API_NAME}/docker-token" --header "Authorization: Bearer ${ACCESS_TOKEN}") || die "Failed to reach Proxygen API"

USER=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.user // empty')
PASSWORD=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.password // empty')
REGISTRY=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.registry // empty')

if [ -z "$REGISTRY" ]; then
  die "Malformed response from Proxygen: missing registry"
fi

REGISTRY_HOST=$(printf '%s' "$REGISTRY" | sed -E 's#^https?://##' | sed -E 's#/$##')

if [ -n "$USER" ] && [ -n "$PASSWORD" ]; then
  log "Logging in to registry: $REGISTRY_HOST"
  printf '%s' "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"
else
  die "No usable login credentials returned from Proxygen"
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
    attempt=$(( attempt + 1 ))
  done
}

log "Tagging $LOCAL_IMAGE as $REMOTE_COMMIT_TAG"
docker tag "$LOCAL_IMAGE" "$REMOTE_COMMIT_TAG"
retry_push "$REMOTE_COMMIT_TAG"

get_manifest_digest() {
  local tag="$1"
  local attempt=1
  local max_attempts=3
  while [ $attempt -le $max_attempts ]; do
    local digest
    digest=$(curl -fsS -u "${USER}:${PASSWORD}" -I -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${tag}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true)
    if [ -n "$digest" ]; then
      printf '%s' "$digest"
      return 0
    fi
    sleep $(( attempt ))
    attempt=$(( attempt + 1 ))
  done
  return 1
}

if [ "$PUSH_LATEST" = "true" ]; then
  if [ "$REMOTE_IMAGE_TAG" = "latest" ]; then
    log "IMAGE_TAG is 'latest' - skipping separate :latest push"
  else
    COMMIT_DIGEST=$(get_manifest_digest "$REMOTE_IMAGE_TAG" || true)
    LATEST_DIGEST=$(get_manifest_digest "latest" || true)
    log "COMMIT_DIGEST='${COMMIT_DIGEST:-<none>}' LATEST_DIGEST='${LATEST_DIGEST:-<none>}'"
    if [ -z "$COMMIT_DIGEST" ]; then
      log "Unable to determine manifest digest for ${REMOTE_IMAGE_TAG}; skipping :latest push"
    elif [ -n "$LATEST_DIGEST" ] && [ "$COMMIT_DIGEST" = "$LATEST_DIGEST" ]; then
      log "Remote latest already points to the same manifest - skipping :latest push"
    else
      log "Tagging $LOCAL_IMAGE as $REMOTE_LATEST_TAG"
      docker tag "$LOCAL_IMAGE" "$REMOTE_LATEST_TAG"
      retry_push "$REMOTE_LATEST_TAG"
    fi
  fi
else
  log "Skipping latest tag push (PUSH_LATEST=${PUSH_LATEST})"
fi

if [ "$PUSH_LATEST" = "true" ]; then
  LATEST_SUFFIX=" and latest"
else
  LATEST_SUFFIX=""
fi
log "Image pushed successfully to ${REMOTE_COMMIT_TAG}${LATEST_SUFFIX}"

LIST_LIMIT=${LIST_LIMIT:-5}
TMP_TAGS=$(mktemp /tmp/registry_tags.XXXXXX)
TMP_MANIFEST=$(mktemp /tmp/registry_manifest.XXXXXX)
TMP_CONFIG=$(mktemp /tmp/registry_config.XXXXXX)
TMP_INDEX=$(mktemp /tmp/registry_index.XXXXXX)
trap 'rm -f "$TMP_TAGS" "$TMP_MANIFEST" "$TMP_CONFIG" "$TMP_INDEX" 2>/dev/null || true' EXIT

if ! curl -fsS -u "${USER}:${PASSWORD}" "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/tags/list" -o "$TMP_TAGS" 2>/dev/null; then
  log "Failed to fetch tags for ${REMOTE_IMAGE_NAME}" && sed -n '1,200p' "$TMP_TAGS" || true
  exit 0
fi

if command -v jq >/dev/null 2>&1; then
  TAGS=$(jq -r '.tags[]' "$TMP_TAGS" 2>/dev/null || true)
else
  TAGS=$(sed -n 's/.*"tags"[[:space:]]*:[[:space:]]*\[//p' "$TMP_TAGS" | tr -d '[]" ' | tr ',' '\n' || true)
fi

if [ -z "${TAGS}" ]; then
  log "No tags found for ${REMOTE_IMAGE_NAME}"
  exit 0
fi

: >"$TMP_INDEX"
for tag in ${TAGS}; do
  if curl -fsS -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${tag}" -o "$TMP_MANIFEST" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      CONFIG_DIGEST=$(jq -r '.config.digest // empty' "$TMP_MANIFEST" 2>/dev/null || true)
    else
      CONFIG_DIGEST=$(grep -o '"config"[^{]*{[^}]*"digest"[[:space:]]*:[[:space:]]*"[^"]*"' "$TMP_MANIFEST" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)"/\1/' | head -1 || true)
    fi
    MANIFEST_DIGEST=$(curl -fsS -u "${USER}:${PASSWORD}" -I -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${tag}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true)
  else
    CONFIG_DIGEST=""
    MANIFEST_DIGEST=""
  fi
  CREATED=""
  DIGEST=""
  if [ -n "$CONFIG_DIGEST" ]; then
    if curl -fsS -u "${USER}:${PASSWORD}" "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/blobs/${CONFIG_DIGEST}" -o "$TMP_CONFIG" 2>/dev/null; then
      if command -v jq >/dev/null 2>&1; then
        CREATED=$(jq -r '.created // .created // empty' "$TMP_CONFIG" 2>/dev/null || true)
      else
        CREATED=$(grep -o '"created"[[:space:]]*:[[:space:]]*"[^"]*"' "$TMP_CONFIG" | head -1 | sed -E 's/.*:[[:space:]]*"([^\"]*)"/\1/' || true)
      fi
      if [ -n "$MANIFEST_DIGEST" ]; then
        DIGEST="$MANIFEST_DIGEST"
      else
        DIGEST="$CONFIG_DIGEST"
      fi
    fi
  fi
  [ -z "$CREATED" ] && CREATED="1970-01-01T00:00:00Z"
  printf '%s\t%s\t%s\n' "$CREATED" "$tag" "$DIGEST" >>"$TMP_INDEX"
done

sort -r "$TMP_INDEX" | head -n "$LIST_LIMIT" >"${TMP_INDEX}.top" || true

printf '%s\t%s\t%s\n' "IMAGE" "DIGEST" "PUSHED_AT"
while IFS=$'\t' read -r CREATED TAG DIGEST; do
  IMAGE_NAME="${REMOTE_IMAGE_NAME}:${TAG}"
  if [ "$CREATED" = "1970-01-01T00:00:00Z" ]; then
    DISPLAY_CREATED=""
  else
    DISPLAY_CREATED="$CREATED"
  fi
  printf '%s\t%s\t%s\n' "$IMAGE_NAME" "$DIGEST" "$DISPLAY_CREATED"
done <"${TMP_INDEX}.top" | (command -v column >/dev/null 2>&1 && column -t -s $'\t' || cat)
