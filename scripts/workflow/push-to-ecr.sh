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

if printf '%s' "${REGISTRY_HOST}" | grep -qE '^[0-9]+\.dkr\.ecr\.'; then
  AWS_OUT=$(aws --region "${AWS_REGION}" ecr describe-images --repository-name "${REMOTE_IMAGE_NAME}" --image-ids imageTag="${REMOTE_IMAGE_TAG}" --query 'imageDetails[0].[imageDigest,imagePushedAt]' --output text 2>/dev/null || true)
  if [ -n "${AWS_OUT}" ]; then
    DIGEST=$(printf '%s' "${AWS_OUT}" | awk '{print $1}')
    PUSHED_AT=$(printf '%s' "${AWS_OUT}" | awk '{print $2}')
    PUSHED_AT_SOURCE="ecr"
    ECR_AVAILABLE="true"
    log "ECR provided digest and pushedAt for ${REMOTE_IMAGE_TAG}: ${DIGEST}, ${PUSHED_AT}"
  else
    log "WARNING: ECR returned no metadata for ${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}; continuing without ECR authoritative values"
    ECR_AVAILABLE="false"
  fi
else
  log "WARNING: Registry ${REGISTRY_HOST} does not appear to be ECR; skipping authoritative ECR listing"
  ECR_AVAILABLE="false"
fi

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

print_header
print_row "$IMAGE_PRINT" "$DIGEST_CLEAN" "$PUSHED_AT_NORM"

if [ "${ECR_AVAILABLE:-}" = "true" ] || [ "${PUSHED_AT_SOURCE:-}" = "ecr" ]; then
  log "[push-to-ecr] Verified in ECR: ${IMAGE_PRINT} digest=${DIGEST} pushedAt=${PUSHED_AT}"
fi
