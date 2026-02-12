#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log(){ printf '[push-to-ecr] %s\n' "$1"; return 0; }
die(){ printf '[push-to-ecr] ERROR: %s\n' "$1" >&2; exit 1; }

usage(){ cat >&2 <<'EOF'
Usage: push-to-ecr.sh <api-name> <local-image> <remote-image-name> <remote-image-tag> [version-tag]

Examples:
  DOCKER_TOKEN=$(printf '%s' '{"user":"example","password":"secret","registry":"https://1234567890.dkr.ecr.eu-west-2.amazonaws.com"}' | base64) \
    ./scripts/workflow/push-to-ecr.sh dos-search dos-search:local dos-search 123456
EOF
  exit 1
}

trim_ws(){
  local s="$1"
  s="${s#${s%%[![:space:]]*}}"
  s="${s%${s##*[![:space:]]}}"
  printf '%s' "$s"
  return 0
}

strip_quotes(){
  local s="$1"
  s="${s#\"}"
  s="${s%\"}"
  printf '%s' "$s"
  return 0
}

normalise_token(){
  local token="$1"
  token=$(printf '%s' "$token" | tr -d '\r\n')
  token="${token#\{}"
  token="${token%\}}"
  token="${token#\"}"
  token="${token%\"}"
  printf '%s' "$token"
  return 0
}

retry_push(){
  local tag="$1" attempt=1 retries=$(( ${PUSH_RETRIES:-3} ))
  until docker push "$tag"; do
    if (( attempt >= retries )); then die "docker push $tag failed after $retries attempts"; fi
    log "push $tag failed (attempt $attempt), retrying..."
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
  return 0
}

retry_pull(){
  local image="$1" attempt=1 retries=$(( ${PULL_RETRIES:-3} ))
  until docker pull "$image"; do
    if (( attempt >= retries )); then die "docker pull $image failed after $retries attempts"; fi
    log "pull $image failed (attempt $attempt), retrying..."
    sleep $(( attempt * 2 ))
    attempt=$(( attempt + 1 ))
  done
  return 0
}

init(){
  API_NAME="${1:-}"
  LOCAL_IMAGE="${2:-}"
  REMOTE_IMAGE_NAME="${3:-}"
  REMOTE_IMAGE_TAG="${4:-}"
  VERSION_TAG="${5:-}"
  PUSH_RETRIES=$(( ${PUSH_RETRIES:-3} ))
  [[ -n "$API_NAME" && -n "$LOCAL_IMAGE" && -n "$REMOTE_IMAGE_NAME" && -n "$REMOTE_IMAGE_TAG" ]] || usage
  return 0
}

fetch_proxygen_registry_credentials(){
  local raw_token="${DOCKER_TOKEN:-}"
  [[ -n "$raw_token" ]] || die "DOCKER_TOKEN not provided"

  if [[ "${DEBUG_PUSH_TO_ECR:-}" == "1" ]]; then
    local prefix suffix
    prefix=$(printf '%.6s' "$raw_token")
    suffix=$(printf '%s' "$raw_token" | tail -c 6)
    log "DEBUG: DOCKER_TOKEN length=${#raw_token}, prefix=${prefix}..., suffix=...${suffix}"
    if printf '%s' "$raw_token" | base64 --decode >/dev/null 2>&1; then
      local decoded
      decoded=$(printf '%s' "$raw_token" | base64 --decode 2>/dev/null || true)
      if [[ "$decoded" == *"user"* && "$decoded" == *"password"* && "$decoded" == *"registry"* ]]; then
        log "DEBUG: DOCKER_TOKEN looks like base64-encoded JSON"
      else
        log "DEBUG: DOCKER_TOKEN base64-decodes but missing expected keys"
      fi
    fi
  fi

  local token
  token=$(printf '%s' "$raw_token" | base64 --decode 2>/dev/null || printf '%s' "$raw_token")
  token=$(normalise_token "$token")

  if [[ "${DEBUG_PUSH_TO_ECR:-}" == "1" ]]; then
    local key_list
    key_list=$(printf '%s' "$token" | tr ',' '\n' | while IFS= read -r segment; do
      segment=$(trim_ws "$segment")
      [[ -n "$segment" ]] || continue
      local key
      key=$(strip_quotes "$(trim_ws "${segment%%:*}")")
      [[ -n "$key" ]] && printf '%s,' "$key"
    done)
    log "DEBUG: parsed token keys=${key_list%,}"
  fi

  local user="" password="" registry=""
  while IFS= read -r segment; do
    segment=$(trim_ws "$segment")
    [[ -n "$segment" ]] || continue
    local key=$(strip_quotes "$(trim_ws "${segment%%:*}")")
    local value=$(strip_quotes "$(trim_ws "${segment#*:}")")
    case "$key" in
      user) user="$value" ;;
      password) password="$value" ;;
      registry) registry="$value" ;;
    esac
  done <<< "$(printf '%s' "$token" | tr ',' '\n')"

  [[ -n "$user" ]] || die "Failed to parse user from DOCKER_TOKEN"
  [[ -n "$password" ]] || die "Failed to parse password from DOCKER_TOKEN"
  [[ -n "$registry" ]] || die "Failed to parse registry from DOCKER_TOKEN"

  USER="$user"
  PASSWORD="$password"
  REGISTRY="$registry"
  REGISTRY_HOST=$(printf '%s' "$REGISTRY" | sed -E 's#^https?://##' | sed -E 's#/$##')
  return 0
}

docker_login(){
  [[ -n "$USER" && -n "$PASSWORD" ]] || die "No usable login credentials returned from Proxygen"
  printf '%s' "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"
  return 0
}

remote_image_ref(){
  local tag="$1"
  printf '%s/%s:%s' "$REGISTRY_HOST" "$REMOTE_IMAGE_NAME" "$tag"
  return 0
}

push_image(){
  REMOTE_COMMIT_TAG="$(remote_image_ref "$REMOTE_IMAGE_TAG")"
  log "Tagging $LOCAL_IMAGE as $REMOTE_COMMIT_TAG"
  docker tag "$LOCAL_IMAGE" "$REMOTE_COMMIT_TAG"
  retry_push "$REMOTE_COMMIT_TAG"
  log "Image pushed successfully to ${REMOTE_COMMIT_TAG}"
  return 0
}

re_tag_image(){
  [[ -n "${VERSION_TAG:-}" ]] || return 0
  local source_ref="$(remote_image_ref "$REMOTE_IMAGE_TAG")"
  local version_ref="$(remote_image_ref "$VERSION_TAG")"
  log "Re-tagging ${source_ref} as ${version_ref}"
  log "Pulling ${source_ref} from remote registry"
  retry_pull "$source_ref"
  docker tag "$source_ref" "$version_ref"
  retry_push "$version_ref"
  log "Version tag pushed successfully to ${version_ref}"
  return 0
}

fetch_manifest_header(){
  curl -fsSI -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' \
    "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true
  return 0
}

print_manifest_metadata(){
  log "Accessing repository via Docker Registry HTTP API: ${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}"
  local manifest_tag
  if [[ -n "${VERSION_TAG:-}" ]]; then
    manifest_tag="${VERSION_TAG}"
  else
    manifest_tag="${REMOTE_IMAGE_TAG}"
  fi

  DIGEST=$(REMOTE_IMAGE_TAG="$manifest_tag" fetch_manifest_header || true)
  if [[ -z "${DIGEST:-}" ]]; then
    die "Failed to determine digest for ${REMOTE_IMAGE_NAME}:${manifest_tag} via manifest header"
  fi
  DIGEST="${DIGEST#sha256:}"
  DIGEST="sha256:${DIGEST}"
  log "Verified that pushed image exists in repository"
  printf '\n%-40s %s\n' "IMAGE" "DIGEST"
  printf '%-40s %s\n' "----------------------------------------" "----------------------------------------------------------------"
  printf '%-40s %s\n' "${REMOTE_IMAGE_NAME}:${manifest_tag}" "${DIGEST}"
  return 0
}

main(){
  init "$@"
  fetch_proxygen_registry_credentials
  docker_login
  if [[ -z "${VERSION_TAG:-}" ]]; then
    push_image
    log "No version tag supplied; skipping re-tag"
  else
    log "Version tag supplied; skipping commit-tag push and re-tagging existing image"
    re_tag_image
  fi
  print_manifest_metadata
  return 0
}

main "$@"
