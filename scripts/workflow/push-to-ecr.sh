#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"
export BASE_URL

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
  printf '\nLatest pushed image summary for repository: %s on registry: %s\n\n' "${REMOTE_IMAGE_NAME}" "${REGISTRY_HOST}"
  printf "$format" "IMAGE" "DIGEST"
  printf "$format" "$dash1" "$dash2"
  printf '\n'
  printf "$format" "$image" "$digest"
  printf '\n'
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

proxygen_describe(){
  local payload="$1"
  curl -sS -H "Authorization: Bearer ${ACCESS_TOKEN}" -H 'Content-Type: application/json' -d "$payload" "$PROXYGEN_API" || true
}

parse_proxygen_resp(){
  local resp="$1"
  DIGEST=$(printf '%s' "$resp" | jq -r '.imageDetails[0].imageDigest // empty' 2>/dev/null || true)
  CREATED=$(printf '%s' "$resp" | jq -r '.imageDetails[0].imagePushedAt // empty' 2>/dev/null || true)
}

fetch_image_metadata(){
  DIGEST=""
  CREATED=""
  PROXYGEN_API="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}/aws/ecr/DescribeImages"
  PAYLOAD=$(printf '{"repositoryName":"%s","imageIds":[{"imageTag":"%s"}]}' "${REMOTE_IMAGE_NAME}" "${REMOTE_IMAGE_TAG}")

  resp=$(proxygen_describe "$PAYLOAD")
  if [ -z "$resp" ]; then
    die "Failed to determine image digest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} via Proxygen"
  fi

  parse_proxygen_resp "$resp"
  if [ -z "$DIGEST" ]; then
    die "Failed to determine image digest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} via Proxygen"
  fi

  DIGEST="${DIGEST#sha256:}"
  DIGEST="sha256:${DIGEST}"
  [ -n "${CREATED:-}" ] && log "[push-to-ecr] Found pushed time for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} at ${CREATED}"
}

main(){
  init "$@"
  fetch_proxygen_registry_credentials
  docker_login
  push_image
  fetch_image_metadata
  print_summary "${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}" "$DIGEST"
  log "Verified image: ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} digest=${DIGEST}"
  printf '\n'
}

main "$@"
