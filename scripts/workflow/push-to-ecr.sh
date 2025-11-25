#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log(){ printf '[push-to-ecr] %s\n' "$1"; }
die(){ printf '[push-to-ecr] ERROR: %s\n' "$1" >&2; exit 1; }

usage(){ cat >&2 <<'EOF'
Usage: push-to-ecr.sh <api-name> <local-image> <remote-image-name> <remote-image-tag>

Example:
  ACCESS_TOKEN=eyJ... ./scripts/workflow/push-to-ecr.sh dos-search dos-search:local dos-search 123456
EOF
  exit 1
}

retry_push(){
  local tag="$1" attempt=1 retries=$(( ${PUSH_RETRIES:-3} ))
  until docker push "$tag"; do
    if (( attempt >= retries )); then die "docker push $tag failed after $retries attempts"; fi
    log "push $tag failed (attempt $attempt), retrying..."
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
}

init(){
  API_NAME="${1:-}"
  LOCAL_IMAGE="${2:-}"
  REMOTE_IMAGE_NAME="${3:-}"
  REMOTE_IMAGE_TAG="${4:-}"
  PUSH_RETRIES=$(( ${PUSH_RETRIES:-3} ))
  [ -n "${ACCESS_TOKEN:-}" ] || die "ACCESS_TOKEN not provided"
  [ -n "$API_NAME" -a -n "$LOCAL_IMAGE" -a -n "$REMOTE_IMAGE_NAME" -a -n "$REMOTE_IMAGE_TAG" ] || usage
}

fetch_proxygen_registry_credentials(){
  BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"
  TOKEN_RESPONSE=$(curl -fsS --request GET --url "${BASE_URL}/apis/${API_NAME}/docker-token" --header "Authorization: Bearer ${ACCESS_TOKEN}") || die "Failed to reach Proxygen API"
  USER=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.user // empty')
  PASSWORD=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.password // empty')
  REGISTRY=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.registry // empty')
  [ -n "$REGISTRY" ] || die "Malformed response from Proxygen: missing registry"
  REGISTRY_HOST=$(printf '%s' "$REGISTRY" | sed -E 's#^https?://##' | sed -E 's#/$##')
  REGISTRY_ACCOUNT=$(printf '%s' "$REGISTRY_HOST" | cut -d'.' -f1)
  REGISTRY_REGION=$(printf '%s' "$REGISTRY_HOST" | awk -F'.' '{for(i=1;i<=NF;i++){ if($i=="ecr"){print $(i+1); exit}}}')
}

docker_login(){
  [ -n "$USER" -a -n "$PASSWORD" ] || die "No usable login credentials returned from Proxygen"
  printf '%s' "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"
}

push_image(){
  REMOTE_COMMIT_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
  log "Tagging $LOCAL_IMAGE as $REMOTE_COMMIT_TAG"
  docker tag "$LOCAL_IMAGE" "$REMOTE_COMMIT_TAG"
  retry_push "$REMOTE_COMMIT_TAG"
  log "Image pushed successfully to ${REMOTE_COMMIT_TAG}"
}

fetch_manifest_header(){
  curl -fsSI -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' \
    "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true
}

print_manifest_metadata(){
  TMP_MANIFEST=$(mktemp /tmp/manifest.XXXXXX)
  TMP_CONFIG=$(mktemp /tmp/config.XXXXXX)
  trap 'rm -f "$TMP_MANIFEST" "$TMP_CONFIG" 2>/dev/null || true' RETURN

  curl -fsS -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json,application/vnd.docker.distribution.manifest.list.v2+json' \
    "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" -o "$TMP_MANIFEST" || die "Failed to download manifest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"

  DIGEST=$(fetch_manifest_header || true)
  if [ -z "${DIGEST:-}" ]; then
    DIGEST=$(jq -r '.config.digest // .manifests[0].digest // empty' "$TMP_MANIFEST" 2>/dev/null || true)
  fi
  if [ -z "${DIGEST:-}" ]; then
    DIGEST=$(grep -o '"digest"[[:space:]]*:[[:space:]]*"[^"]*"' "$TMP_MANIFEST" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)".*/\1/' | head -n1 || true)
  fi
  if [ -z "${DIGEST:-}" ]; then
    rm -f "$TMP_MANIFEST" "$TMP_CONFIG" 2>/dev/null || true
    die "Failed to determine digest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
  fi
  DIGEST="${DIGEST#sha256:}"
  DIGEST="sha256:${DIGEST}"

  CONFIG_DIGEST=$(jq -r '.config.digest // empty' "$TMP_MANIFEST")
  [ -n "${CONFIG_DIGEST:-}" ] || die "Manifest does not contain a config.digest"

  curl -fsS -u "${USER}:${PASSWORD}" "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/blobs/${CONFIG_DIGEST}" -o "$TMP_CONFIG" || die "Failed to fetch config blob ${CONFIG_DIGEST}"

  CREATED=$(jq -r '.created // empty' "$TMP_CONFIG" 2>/dev/null || true)
  AUTHOR=$(jq -r '.author // empty' "$TMP_CONFIG" 2>/dev/null || true)
  CREATED_BY=$(jq -r '( .history[0].created_by // .created_by // empty )' "$TMP_CONFIG" 2>/dev/null || true)

  printf 'IMAGE\tDIGEST\tCREATED\tAUTHOR\tCREATED_BY\tOS/ARCH\tUSER\tWORKDIR\tEXPOSED_PORTS\tVOLUMES\tLAYERS\tSIZE\tLABELS\n'
  printf '%s\t%s\t%s\t%s\t%s\t%s/%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}" "${DIGEST}" "${CREATED}" "${AUTHOR}" "${CREATED_BY}" "${OS}" "${ARCH}" "${USER_CFG}" "${WORKDIR}" "${EXPOSED_PORTS}" "${VOLUMES}" "${LAYERS_COUNT}" "${TOTAL_SIZE}" "${LABELS}"

  rm -f "$TMP_MANIFEST" "$TMP_CONFIG" 2>/dev/null || true
}

main(){
  init "$@"
  fetch_proxygen_registry_credentials
  docker_login
  push_image
  print_manifest_metadata
}

main "$@"
