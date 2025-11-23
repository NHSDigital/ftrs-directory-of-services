#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log(){ printf '[push-to-ecr] %s\n' "$1"; }
die(){ printf '[push-to-ecr] ERROR: %s\n' "$1" >&2; exit 1; }

usage(){ cat >&2 <<'EOF'
Usage: push-to-ecr.sh <api-name> <local-image> <remote-image-name> <remote-image-tag>

Required/important environment:
  ACCESS_TOKEN   Bearer token for APIM (required).

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

[ -n "${ACCESS_TOKEN:-}" ] || die "ACCESS_TOKEN not provided"
[ -n "$API_NAME" -a -n "$LOCAL_IMAGE" -a -n "$REMOTE_IMAGE_NAME" -a -n "$REMOTE_IMAGE_TAG" ] || usage

for dep in curl jq docker; do command -v "$dep" >/dev/null 2>&1 || die "required dependency missing: $dep"; done
if ! docker image inspect "$LOCAL_IMAGE" >/dev/null 2>&1; then die "Local image $LOCAL_IMAGE not found"; fi

BASE_URL="${PROXYGEN_BASE_URL:-https://proxygen.prod.api.platform.nhs.uk}"
TOKEN_RESPONSE=$(curl -fsS --request GET --url "${BASE_URL}/apis/${API_NAME}/docker-token" --header "Authorization: Bearer ${ACCESS_TOKEN}") || die "Failed to reach Proxygen API"
USER=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.user // empty')
PASSWORD=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.password // empty')
REGISTRY=$(printf '%s' "$TOKEN_RESPONSE" | jq -r '.registry // empty')
[ -n "$REGISTRY" ] || die "Malformed response from Proxygen: missing registry"
REGISTRY_HOST=$(printf '%s' "$REGISTRY" | sed -E 's#^https?://##' | sed -E 's#/$##')
AWS_CMD=aws

[ -n "$USER" -a -n "$PASSWORD" ] || die "No usable login credentials returned from Proxygen"
printf '%s' "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"

REMOTE_COMMIT_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
REMOTE_LATEST_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:latest"

retry_push(){
  local tag="$1" attempt=1
  until docker push "$tag"; do
    if (( attempt >= PUSH_RETRIES )); then die "docker push $tag failed after $PUSH_RETRIES attempts"; fi
    log "push $tag failed (attempt $attempt), retrying..."
    sleep $(( attempt * 2 )); attempt=$(( attempt + 1 ))
  done
}

log "Tagging $LOCAL_IMAGE as $REMOTE_COMMIT_TAG"
docker tag "$LOCAL_IMAGE" "$REMOTE_COMMIT_TAG"
retry_push "$REMOTE_COMMIT_TAG"

http_head(){ curl --max-time 10 --retry 2 --retry-connrefused -fsS -u "${USER}:${PASSWORD}" -I -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "$@"; }
http_get(){ curl --max-time 10 --retry 2 --retry-connrefused -fsS -u "${USER}:${PASSWORD}" "$@"; }

get_manifest_digest(){
  local tag="$1" attempt=1 max_attempts=3 digest
  while [ $attempt -le $max_attempts ]; do
    digest=$(http_head "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${tag}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true)
    [ -n "$digest" ] && { printf '%s' "$digest"; return 0; }
    sleep $(( attempt )); attempt=$(( attempt + 1 ))
  done
  return 1
}

epoch_from_iso(){
  local iso="${1:-}" s
  [ -z "$iso" ] && { printf '0'; return 0; }
  s=$(printf '%s' "$iso" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/\.[0-9]\+//; s/Z$//')
  if date -d "$s" +%s >/dev/null 2>&1; then date -d "$s" +%s 2>/dev/null && return 0; fi
  printf '0'
}

get_local_created(){
  local candidates img out repo_created
  candidates=("${REMOTE_COMMIT_TAG}" "${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}" "${REMOTE_IMAGE_NAME##*/}:${REMOTE_IMAGE_TAG}")
  for img in "${candidates[@]}"; do
    out=$(docker image inspect -f '{{.Created}}' "$img" 2>/dev/null || true)
    if [ -n "$out" ]; then
      printf '%s' "$out"
      return 0
    fi
  done
  repo_created=$(docker images --format '{{.Repository}}:{{.Tag}}\t{{.CreatedAt}}' 2>/dev/null | awk -v repo1="${REMOTE_COMMIT_TAG}" -v repo2="${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}" -v repo3="${REMOTE_IMAGE_NAME##*/}:${REMOTE_IMAGE_TAG}" 'BEGIN{FS="\t"}{if($1==repo1||$1==repo2||$1==repo3){print $2; exit}}')
  if [ -n "$repo_created" ]; then
    printf '%s' "$repo_created"
    return 0
  fi
  return 1
}

if [ "${PUSH_LATEST}" = "true" ]; then
  if [ "${REMOTE_IMAGE_TAG}" = "latest" ]; then
    log "IMAGE_TAG is 'latest' - skipping separate latest"
  else
    COMMIT_DIGEST=$(get_manifest_digest "${REMOTE_IMAGE_TAG}" || true)
    LATEST_DIGEST=$(get_manifest_digest "latest" || true)
    log "COMMIT_DIGEST='${COMMIT_DIGEST:-<none>}' LATEST_DIGEST='${LATEST_DIGEST:-<none>}'"
    if [ -z "${COMMIT_DIGEST}" ]; then
      log "Unable to determine manifest digest for ${REMOTE_IMAGE_TAG}; skipping :latest push"
    elif [ -n "${LATEST_DIGEST}" ] && [ "${COMMIT_DIGEST}" = "${LATEST_DIGEST}" ]; then
      log "Remote latest already points to the same manifest - skipping :latest push"
    else
      log "Tagging ${LOCAL_IMAGE} as ${REMOTE_LATEST_TAG}"
      docker tag "${LOCAL_IMAGE}" "${REMOTE_LATEST_TAG}"
      retry_push "${REMOTE_LATEST_TAG}"
    fi
  fi
else
  log "Skipping latest tag push (PUSH_LATEST=${PUSH_LATEST})"
fi

LATEST_SUFFIX=""
[ "${PUSH_LATEST}" = "true" ] && LATEST_SUFFIX=" and latest"
log "Image pushed successfully to ${REMOTE_COMMIT_TAG}${LATEST_SUFFIX}"

IMAGE_NAME="${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
DIGEST=""
PUSHED_AT=""
TMP_MANIFEST=$(mktemp /tmp/registry_manifest.XXXXXX)
TMP_CONFIG=$(mktemp /tmp/registry_config.XXXXXX)
trap 'rm -f "$TMP_MANIFEST" "$TMP_CONFIG" 2>/dev/null || true' EXIT

if printf '%s' "$REGISTRY_HOST" | grep -qE '^[0-9]+\.dkr\.ecr\.'; then
  AWS_REGION_EFFECTIVE="${AWS_REGION}"
  AWS_OUT=$(${AWS_CMD} --region "${AWS_REGION_EFFECTIVE}" ecr describe-images --repository-name "${REMOTE_IMAGE_NAME}" --image-ids imageTag="${REMOTE_IMAGE_TAG}" --query 'imageDetails[0].[imageDigest,imagePushedAt]' --output text 2>/dev/null || true)
  if [ -n "${AWS_OUT}" ]; then
    DIGEST=$(printf '%s' "${AWS_OUT}" | awk '{print $1}')
    PUSHED_AT_CAND=$(printf '%s' "${AWS_OUT}" | awk '{print $2}')
    if [ -n "${PUSHED_AT_CAND}" ] && [ "${PUSHED_AT_CAND}" != "None" ]; then
      PUSHED_AT="${PUSHED_AT_CAND}"
      log "AWS ECR provided pushedAt for ${REMOTE_IMAGE_TAG}: ${PUSHED_AT}"
    fi
  fi
fi

if [ -z "${PUSHED_AT}" ] && docker image inspect "${REMOTE_COMMIT_TAG}" >/dev/null 2>&1; then
  PUSHED_AT=$(docker image inspect -f '{{.Created}}' "${REMOTE_COMMIT_TAG}" 2>/dev/null || true)
  log "Found local Created for ${REMOTE_COMMIT_TAG}: ${PUSHED_AT}"
fi

if [ -z "${PUSHED_AT}" ] && docker image inspect "${LOCAL_IMAGE}" >/dev/null 2>&1; then
  PUSHED_AT=$(docker image inspect -f '{{.Created}}' "${LOCAL_IMAGE}" 2>/dev/null || true)
  log "Found local Created for ${LOCAL_IMAGE}: ${PUSHED_AT}"
fi

if [ -z "${PUSHED_AT}" ]; then
  if http_get "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" -o "${TMP_MANIFEST}" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      CONFIG_DIGEST=$(jq -r '.config.digest // empty' "${TMP_MANIFEST}" 2>/dev/null || true)
    else
      CONFIG_DIGEST=$(grep -o '"config"[^{]*{[^}]*"digest"[[:space:]]*:[[:space:]]*"[^"]*"' "${TMP_MANIFEST}" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)"/\1/' | head -1 || true)
    fi
    if [ -n "${CONFIG_DIGEST}" ]; then
      if http_get "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/blobs/${CONFIG_DIGEST}" -o "${TMP_CONFIG}" 2>/dev/null; then
        if command -v jq >/dev/null 2>&1; then
          PUSHED_AT=$(jq -r '.created // .created_at // empty' "${TMP_CONFIG}" 2>/dev/null || true)
        else
          PUSHED_AT=$(grep -o '"created"[[:space:]]*:[[:space:]]*"[^"]*"' "${TMP_CONFIG}" | head -1 | sed -E 's/.*:[[:space:]]*"([^\"]*)"/\1/' || true)
        fi
      fi
    fi
  fi
fi

if [ -z "${DIGEST}" ]; then
  DIGEST=$(get_manifest_digest "${REMOTE_IMAGE_TAG}" || true)
fi

if [ -z "${PUSHED_AT}" ]; then
  PUSHED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  log "PUSHED_AT unknown from local/registry; falling back to current UTC time: ${PUSHED_AT}"
fi

normalize_ts(){
  local ts="$1" out
  [ -z "$ts" ] && { printf ''; return 0; }
  out=$(date -u -d "$ts" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || true)
  if [ -n "$out" ]; then
    printf '%s' "$out"
  else
    printf '%s' "$ts"
  fi
}

truncate_digest(){
  local d="$1" max="$2"
  [ -z "$d" ] && { printf ''; return 0; }
  if [ ${#d} -le "$max" ]; then
    printf '%s' "$d"
  else
    local head tail_len tail
    head="${d:0:12}"
    tail_len=$((max - 15))
    tail="${d: -$tail_len}"
    printf '%s...%s' "$head" "$tail"
  fi
}

PUSHED_AT_NORM=$(normalize_ts "$PUSHED_AT")
DIGEST_CLEAN=${DIGEST#sha256:}

COL1=28
COL2=48
FORMAT=$(printf '%%-%ds  %%-%ds  %%s\n' "$COL1" "$COL2")

print_header(){
  printf '\nList latest pushed image in ECR\n\n'
  printf "$FORMAT" "IMAGE" "DIGEST" "PUSHED_AT"
  printf "$FORMAT" "$(printf '%*s' $COL1 '' | tr ' ' '-')" "$(printf '%*s' $COL2 '' | tr ' ' '-')" "$(printf '%*s' 19 '' | tr ' ' '-')"
  printf '\n'
}

print_row(){
  local img="$1" dig="$2" ts="$3"
  local dig_trunc
  dig_trunc=$(truncate_digest "$dig" "$COL2")
  printf "$FORMAT" "$img" "$dig_trunc" "$ts"
}

print_header
print_row "$IMAGE_NAME" "$DIGEST_CLEAN" "$PUSHED_AT_NORM"
