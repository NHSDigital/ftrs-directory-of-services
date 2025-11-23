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

fetch_manifest(){
  local out_file="$1"
  curl -fsS -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json,application/vnd.docker.distribution.manifest.list.v2+json' \
    "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" -o "$out_file"
}

fetch_manifest_header(){
  curl -fsSI -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' \
    "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true
}

choose_manifest_from_list(){
  local manifest_file="$1" platform="$2"
  if command -v jq >/dev/null 2>&1; then
    if [ -n "$platform" ]; then
      local os=${platform%%/*}
      local arch=${platform#*/}
      jq -r --arg os "$os" --arg arch "$arch" '.manifests[]? | select(.platform? and .platform.os==$os and .platform.architecture==$arch) | .digest' "$manifest_file" 2>/dev/null | head -n1 || true
    else
      jq -r '.manifests[]?.digest' "$manifest_file" 2>/dev/null | head -n1 || true
    fi
  else
    grep -o '"digest"[[:space:]]*:[[:space:]]*"[^\"]*"' "$manifest_file" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)"/\1/' | head -n1 || true
  fi
}

extract_config_digest(){
  local manifest_file="$1"
  if command -v jq >/dev/null 2>&1; then
    jq -r '.config.digest // empty' "$manifest_file" 2>/dev/null || true
  else
    grep -o '"config"[^{]*{[^}]*"digest"[[:space:]]*:[[:space:]]*"[^\"]*"' "$manifest_file" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)"/\1/' | head -1 || true
  fi
}

print_summary(){
  local image="$1" digest="$2"
  local col1=40
  local dash1 dash2
  dash1=$(printf '%*s' "$col1" '' | tr ' ' '-')
  dash2=$(printf '%*s' 72 '' | tr ' ' '-')
  local format="%-${col1}s | %s\n"
  printf '\n'
  printf '\nLatest pushed image summary for repository: %s on registry: %s\n\n' "${REMOTE_IMAGE_NAME}" "${REGISTRY_HOST}"
  printf "$format" "IMAGE" "DIGEST"
  printf "$format" "$dash1" "$dash2"
  printf '\n'
  printf "$format" "$image" "$digest"
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

check_deps(){
  for dep in curl jq docker; do
    command -v "$dep" >/dev/null 2>&1 || die "required dependency missing: $dep"
  done
}

get_apim_token_and_registry(){
  BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"
  TOKEN_RESPONSE=$(curl -fsS --request GET --url "${BASE_URL}/apis/${API_NAME}/docker-token" --header "Authorization: Bearer ${ACCESS_TOKEN}") || die "Failed to reach Proxygen API"
  USER=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.user // empty')
  PASSWORD=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.password // empty')
  REGISTRY=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.registry // empty')
  [ -n "$REGISTRY" ] || die "Malformed response from Proxygen: missing registry"
  REGISTRY_HOST=$(printf '%s' "$REGISTRY" | sed -E 's#^https?://##' | sed -E 's#/$##')
  log "Accessing registry via Docker Registry HTTP API"
  REGISTRY_ACCOUNT=$(printf '%s' "$REGISTRY_HOST" | cut -d'.' -f1)
  REGISTRY_REGION=$(printf '%s' "$REGISTRY_HOST" | awk -F'.' '{for(i=1;i<=NF;i++){ if($i=="ecr"){print $(i+1); exit}}}')
  AWS_CALLER_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || true)
  if [ -n "$AWS_CALLER_ACCOUNT" ] && [ "$AWS_CALLER_ACCOUNT" != "$REGISTRY_ACCOUNT" ]; then
    log "WARNING: AWS caller account ($AWS_CALLER_ACCOUNT) does not match registry account ($REGISTRY_ACCOUNT)"
  fi
  if [ -n "${AWS_REGION:-}" ] && [ -n "$REGISTRY_REGION" ] && [ "${AWS_REGION}" != "$REGISTRY_REGION" ]; then
    log "WARNING: AWS_REGION (${AWS_REGION}) does not match registry region (${REGISTRY_REGION})"
  fi
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

lookup_digest(){
  DIGEST=""
  TMP_MANIFEST=$(mktemp /tmp/registry_manifest.XXXXXX)
  TMP_MANIFEST_SELECTED=""
  trap 'rm -f "${TMP_MANIFEST}" "${TMP_MANIFEST_SELECTED}" 2>/dev/null || true' EXIT

  if fetch_manifest "$TMP_MANIFEST"; then
    DIGEST_HEADER=$(fetch_manifest_header)
    MANIFEST_TO_PARSE="$TMP_MANIFEST"
    if command -v jq >/dev/null 2>&1 && jq -e '.manifests' "$TMP_MANIFEST" >/dev/null 2>&1; then
      SELECT_DIGEST=$(choose_manifest_from_list "$TMP_MANIFEST" "${MANIFEST_PLATFORM:-}")
      if [ -n "$SELECT_DIGEST" ]; then
        if curl -fsS -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${SELECT_DIGEST}" -o "${TMP_MANIFEST}.selected"; then
          TMP_MANIFEST_SELECTED="${TMP_MANIFEST}.selected"
          MANIFEST_TO_PARSE="$TMP_MANIFEST_SELECTED"
          DIGEST="$SELECT_DIGEST"
        fi
      fi
    fi
    if [ -z "$DIGEST" ]; then
      if [ -n "$DIGEST_HEADER" ]; then
        DIGEST="$DIGEST_HEADER"
      else
        CONFIG_DIGEST=$(extract_config_digest "$MANIFEST_TO_PARSE")
        if [ -n "$CONFIG_DIGEST" ]; then
          DIGEST="$CONFIG_DIGEST"
        fi
      fi
    fi
    if [ -z "$DIGEST" ]; then
      die "Failed to determine image digest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
    fi
  else
    rm -f "$TMP_MANIFEST" 2>/dev/null || true
    die "Failed to fetch manifest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} using Proxygen credentials"
  fi
}

main(){
  init "$@"
  check_deps
  get_apim_token_and_registry
  docker_login
  push_image
  lookup_digest
  print_summary "${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}" "$DIGEST"
  log "Verified image: ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} digest=${DIGEST}"
  printf '\n'
}

main "$@"
