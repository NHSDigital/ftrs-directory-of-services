#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log(){ printf '[push-to-ecr] %s\n' "$1"; }
die(){ printf '[push-to-ecr] ERROR: %s\n' "$1" >&2; exit 1; }

usage(){ cat >&2 <<'EOF'
Usage: push-to-ecr.sh <api-name> <local-image> <remote-image-name> <remote-image-tag>

Examples:
  DOCKER_TOKEN=$(printf '%s' '{"user":"example","password":"secret","registry":"https://1234567890.dkr.ecr.eu-west-2.amazonaws.com"}' | base64) \
    ./scripts/workflow/push-to-ecr.sh dos-search dos-search:local dos-search 123456
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
  [ -n "$API_NAME" -a -n "$LOCAL_IMAGE" -a -n "$REMOTE_IMAGE_NAME" -a -n "$REMOTE_IMAGE_TAG" ] || usage
}

fetch_proxygen_registry_credentials(){
  log "fetch_proxygen_registry_credentials DOCKER_TOKEN: ${DOCKER_TOKEN:-<empty>}"

  token="${token//$'\n'/}"
  token="${token//$'\r'/}"
  token="${token#\{}"
  token="${token%\}}"

  local saved_ifs="$IFS"
  IFS=',' read -ra parts <<< "$token"
  IFS="$saved_ifs"

  local user="" password="" registry=""
  for part in "${parts[@]}"; do
    part=$(printf '%s' "$part" | sed -e 's/^ *//' -e 's/ *$//')
    local key=${part%%:*}
    local value=${part#*:}
    if [ -z "$key" ] || [ "$value" = "$key" ]; then
      continue
    fi
    key=$(printf '%s' "$key" | sed -e 's/^ *//' -e 's/ *$//')
    value=$(printf '%s' "$value" | sed -e 's/^ *//' -e 's/ *$//')
    value=${value#"}
    value=${value%"}
    case "$key" in
      user) user="$value" ;;
      password) password="$value" ;;
      registry) registry="$value" ;;
    esac
  done

  [ -n "$user" ] || die "Failed to parse user from DOCKER_TOKEN"
  [ -n "$password" ] || die "Failed to parse password from DOCKER_TOKEN"
  [ -n "$registry" ] || die "Failed to parse registry from DOCKER_TOKEN"

  USER="$user"
  PASSWORD="$password"
  REGISTRY="$registry"
  log "Parsed credentials user=$USER registry=$REGISTRY password_prefix=${PASSWORD:0:12}"

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
  log "Accessing repository via Docker Registry HTTP API: ${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}"
  DIGEST=$(fetch_manifest_header || true)
  if [ -z "${DIGEST:-}" ]; then
    die "Failed to determine digest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} via manifest header"
  fi
  DIGEST="${DIGEST#sha256:}"
  DIGEST="sha256:${DIGEST}"
  log "Verified that pushed image exists in repository"
  printf '\n%-40s %s\n' "IMAGE" "DIGEST"
  printf '%-40s %s\n' "----------------------------------------" "----------------------------------------------------------------"
  printf '%-40s %s\n' "${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}" "${DIGEST}"
}

main(){
  init "$@"
  fetch_proxygen_registry_credentials
  docker_login
  push_image
  print_manifest_metadata
}

main "$@"
