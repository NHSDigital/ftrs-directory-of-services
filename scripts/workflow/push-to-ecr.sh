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

# verify registry account and region match AWS environment (log warnings if not)
REGISTRY_ACCOUNT=$(printf '%s' "$REGISTRY_HOST" | cut -d'.' -f1)
REGISTRY_REGION=$(printf '%s' "$REGISTRY_HOST" | awk -F'.' '{for(i=1;i<=NF;i++){ if($i=="ecr"){print $(i+1); exit}}}')
if command -v aws >/dev/null 2>&1; then
  AWS_CALLER_ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || true)
  if [ -n "$AWS_CALLER_ACCOUNT" ] && [ "$AWS_CALLER_ACCOUNT" != "$REGISTRY_ACCOUNT" ]; then
    log "WARNING: AWS caller account ($AWS_CALLER_ACCOUNT) does not match registry account ($REGISTRY_ACCOUNT)"
  fi
else
  log "WARNING: aws CLI not available to validate registry/account"
fi
if [ -n "${AWS_REGION:-}" ] && [ -n "$REGISTRY_REGION" ] && [ "${AWS_REGION}" != "$REGISTRY_REGION" ]; then
  log "WARNING: AWS_REGION (${AWS_REGION}) does not match registry region (${REGISTRY_REGION})"
fi

[ -n "$USER" -a -n "$PASSWORD" ] || die "No usable login credentials returned from Proxygen"
printf '%s' "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"

REMOTE_COMMIT_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"

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

log "Image pushed successfully to ${REMOTE_COMMIT_TAG}"

IMAGE_NAME="${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
DIGEST=""
PUSHED_AT=""
PUSHED_AT_SOURCE=""

ECR_DESCRIBE_RETRIES=${ECR_DESCRIBE_RETRIES:-5}
ECR_DESCRIBE_SLEEP=${ECR_DESCRIBE_SLEEP:-1}
attempt=1
AWS_OUT=""

# Use registry API (manifest -> config) via Proxygen credentials to get digest and created/pushed time
TMP_MANIFEST=$(mktemp /tmp/registry_manifest.XXXXXX)
TMP_MANIFEST_SELECTED=""
TMP_CONFIG=$(mktemp /tmp/registry_config.XXXXXX)
if curl -fsS -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json, application/vnd.docker.distribution.manifest.list.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" -o "${TMP_MANIFEST}"; then
  DIGEST_HEADER=$(curl -fsSI -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${REMOTE_IMAGE_TAG}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true)
  # Determine if manifest is a manifest-list (multi-arch)
  if command -v jq >/dev/null 2>&1 && jq -e '.manifests' "${TMP_MANIFEST}" >/dev/null 2>&1; then
    # prefer linux/amd64 if present
    SELECT_DIGEST=$(jq -r '.manifests[] | select(.platform.platform? // empty | .os == "linux" and (.architecture // "") == "amd64") | .digest' "${TMP_MANIFEST}" 2>/dev/null | head -n1 || true)
    if [ -z "${SELECT_DIGEST}" ]; then
      SELECT_DIGEST=$(jq -r '.manifests[0].digest // empty' "${TMP_MANIFEST}" 2>/dev/null || true)
    fi
    if [ -n "${SELECT_DIGEST}" ]; then
      if curl -fsS -u "${USER}:${PASSWORD}" -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${SELECT_DIGEST}" -o "${TMP_MANIFEST}.selected"; then
        TMP_MANIFEST_SELECTED="${TMP_MANIFEST}.selected"
        MANIFEST_TO_PARSE="${TMP_MANIFEST_SELECTED}"
        DIGEST="${SELECT_DIGEST}"
      else
        MANIFEST_TO_PARSE="${TMP_MANIFEST}"
      fi
    else
      MANIFEST_TO_PARSE="${TMP_MANIFEST}"
    fi
  else
    MANIFEST_TO_PARSE="${TMP_MANIFEST}"
  fi

  if command -v jq >/dev/null 2>&1; then
    CONFIG_DIGEST=$(jq -r '.config.digest // empty' "${MANIFEST_TO_PARSE}" 2>/dev/null || true)
  else
    CONFIG_DIGEST=$(grep -o '"config"[^{]*{[^}]*"digest"[[:space:]]*:[[:space:]]*"[^" ]*"' "${MANIFEST_TO_PARSE}" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)"/\1/' | head -1 || true)
  fi

  if [ -n "${CONFIG_DIGEST}" ]; then
    if curl -fsS -u "${USER}:${PASSWORD}" "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/blobs/${CONFIG_DIGEST}" -o "${TMP_CONFIG}"; then
      if command -v jq >/dev/null 2>&1; then
        PUSHED_AT=$(jq -r '.created // .created_at // empty' "${TMP_CONFIG}" 2>/dev/null || true)
      else
        PUSHED_AT=$(grep -o '"created"[[:space:]]*:[[:space:]]*"[^\"]*"' "${TMP_CONFIG}" | head -1 | sed -E 's/.*:[[:space:]]*"([^\"]*)"/\1/' || true)
      fi
      [ -n "${PUSHED_AT}" ] && PUSHED_AT_SOURCE="registry"
    fi
  fi

  # If DIGEST still empty, prefer header or manifest config digest
  if [ -z "${DIGEST}" ]; then
    DIGEST=${DIGEST_HEADER:-}
    if [ -z "${DIGEST}" ] && [ -n "${CONFIG_DIGEST}" ]; then
      DIGEST=${CONFIG_DIGEST}
    fi
  fi

  ECR_AVAILABLE="false"
  rm -f "${TMP_MANIFEST}" "${TMP_MANIFEST_SELECTED}" "${TMP_CONFIG}" 2>/dev/null || true
  if [ -n "${DIGEST}" ]; then
    log "Registry manifest lookup provided digest for ${REMOTE_IMAGE_TAG}: ${DIGEST} (source=registry)"
  else
    log "WARNING: Registry manifest lookup did not return a digest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
  fi
else
  log "WARNING: Failed to fetch manifest for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG} using Proxygen credentials"
  rm -f "${TMP_MANIFEST}" "${TMP_MANIFEST_SELECTED}" "${TMP_CONFIG}" 2>/dev/null || true
  ECR_AVAILABLE="false"
fi

normalize_ts(){
  local ts="${1:-}" out
  [ -z "$ts" ] && { printf ''; return 0; }
  out=$(date -u -d "$ts" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || true)
  if [ -n "$out" ]; then
    printf '%s' "$out"
  else
    printf '%s' "$ts"
  fi
}

# normalize and prepare output
PUSHED_AT_NORM=$(normalize_ts "$PUSHED_AT")
DIGEST_CLEAN=${DIGEST#sha256:}

# always print the registry-qualified name when using ECR authoritative values
IMAGE_PRINT="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"

COL1=20
COL2=60

dash1=$(printf '%*s' "$COL1" '' | tr ' ' '-')
dash2=$(printf '%*s' "$COL2" '' | tr ' ' '-')
dash3=$(printf '%*s' 19 '' | tr ' ' '-')

FORMAT="%-${COL1}s  %-${COL2}s  %s\n"

print_header(){
  printf '\nLatest pushed image summary for repository: %s on registry: %s\n\n' "${REMOTE_IMAGE_NAME}" "${REGISTRY_HOST}"
  printf "$FORMAT" "IMAGE" "DIGEST" "PUSHED_AT (src:${PUSHED_AT_SOURCE:-unknown})"
  printf "$FORMAT" "$dash1" "$dash2" "$dash3"
  printf '\n'
}

print_row(){
  local img="$1" dig="$2" ts="$3"
  local dig_trunc
  dig_trunc=$(truncate_digest "$dig" "$COL2")
  printf "$FORMAT" "$img" "$dig_trunc" "$ts"
}

default_truncate_digest(){
  local d="$1" max="$2"
  [ -z "$d" ] && { printf ''; return 0; }
  if [ -z "$max" ]; then max=60; fi
  if [ ${#d} -le "$max" ]; then
    printf '%s' "$d"
    return 0
  fi
  local head_len=20 tail_len=20
  if [ $((head_len + tail_len + 3)) -gt "$max" ]; then
    head_len=$(( (max - 3) / 2 ))
    tail_len=$(( max - 3 - head_len ))
  fi
  local head="${d:0:head_len}"
  local tail="${d: -tail_len}"
  printf '%s...%s' "$head" "$tail"
}

# Provide a stable name the rest of the script expects
truncate_digest(){
  default_truncate_digest "$@"
}

print_header
print_row "$IMAGE_PRINT" "$DIGEST_CLEAN" "$PUSHED_AT_NORM"

if [ "${ECR_AVAILABLE:-}" = "true" ] || [ "${PUSHED_AT_SOURCE:-}" = "ecr" ]; then
  log "[push-to-ecr] Verified in ECR: ${IMAGE_PRINT} digest=${DIGEST} pushedAt=${PUSHED_AT}"
fi
