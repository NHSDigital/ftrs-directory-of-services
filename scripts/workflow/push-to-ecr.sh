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

# Diagnostic: if aws CLI is available, show the AWS caller account and compare to registry account
if command -v aws >/dev/null 2>&1; then
  REGISTRY_ACCOUNT=$(echo "$REGISTRY_HOST" | cut -d. -f1 2>/dev/null || true)
  AWS_CALLER_ACCOUNT="$(aws sts get-caller-identity --region "${AWS_REGION:-}" --query Account --output text 2>/dev/null || true)"
  log "Registry account: ${REGISTRY_ACCOUNT:-unknown}, AWS caller account: ${AWS_CALLER_ACCOUNT:-unknown}"
  if [ -n "${REGISTRY_ACCOUNT:-}" ] && [ -n "${AWS_CALLER_ACCOUNT:-}" ] && [ "${REGISTRY_ACCOUNT}" != "${AWS_CALLER_ACCOUNT}" ]; then
    log "Warning: AWS caller account does not match registry account — describe-images may query a different account than the registry you pushed to"
  fi
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

# Print repository images for the repo after a successful push (ECR listing only)
log "Listing images for repository ${REMOTE_IMAGE_NAME} at ${REGISTRY_HOST}"
# Prefer AWS ECR API when available and registry is ECR
if command -v aws >/dev/null 2>&1 && echo "${REGISTRY_HOST}" | grep -qE 'dkr\\.ecr\\.'; then
  # Use AWS_REGION from environment
  ECR_REGION="${AWS_REGION:-}"
  if [ -z "${ECR_REGION}" ]; then
    log "AWS_REGION not set; skipping ECR listing"
  else
    log "Querying ECR (${ECR_REGION}) for repository ${REMOTE_IMAGE_NAME}"
    # Capture raw JSON or error output so we can diagnose empty/permission issues
    IMAGES_RAW="$(aws ecr describe-images --repository-name "${REMOTE_IMAGE_NAME}" --region "${ECR_REGION}" --output json 2>&1 || true)"
    AWS_RC=$?
    if [ $AWS_RC -ne 0 ]; then
      log "Failed to call AWS ECR describe-images (exit $AWS_RC) — raw output follows"
      printf '%s\n' "$IMAGES_RAW"
      log "Checking AWS caller identity (may help diagnose permissions)"
      aws sts get-caller-identity --region "${ECR_REGION}" 2>&1 || log "Failed to query sts get-caller-identity"
      log "Checking repository existence"
      aws ecr describe-repositories --repository-names "${REMOTE_IMAGE_NAME}" --region "${ECR_REGION}" 2>&1 || log "Failed to describe repository"
    else
      # parse number of images
      IMAGE_COUNT=$(echo "$IMAGES_RAW" | jq '.imageDetails | length' 2>/dev/null || echo 0)
      if [ "$IMAGE_COUNT" -gt 0 ]; then
        log "Found ${IMAGE_COUNT} images in ECR repo ${REMOTE_IMAGE_NAME}; printing table"
        aws ecr describe-images --repository-name "${REMOTE_IMAGE_NAME}" --region "${ECR_REGION}" \
          --query 'imageDetails[].{Tags:imageTags, Digest:imageDigest, PushedAt:imagePushedAt}' --output table || log "Failed to render images table"
      else
        log "No images returned for repository ${REMOTE_IMAGE_NAME} (imageDetails empty) — raw output follows"
        printf '%s\n' "$IMAGES_RAW"
        log "Checking repository existence"
        aws ecr describe-repositories --repository-names "${REMOTE_IMAGE_NAME}" --region "${ECR_REGION}" 2>&1 || log "Failed to describe repository"
        log "Check caller identity to verify permissions"
        aws sts get-caller-identity --region "${ECR_REGION}" 2>&1 || log "Failed to query sts get-caller-identity"
      fi
    fi
  fi
else
  # AWS/ECR path not available; try skopeo (uses docker/auth) to list remote tags
  if command -v skopeo >/dev/null 2>&1; then
    log "AWS CLI not available or registry not ECR; using skopeo to list tags for ${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}"
    # capture both stdout and stderr to a temp file so we can always inspect it
    if skopeo list-tags --tls-verify=false docker://${REGISTRY_HOST}/${REMOTE_IMAGE_NAME} > /tmp/skopeo_out.$$ 2>&1; then
      # pretty print skopeo output (JSON) if possible
      if command -v jq >/dev/null 2>&1; then
        jq . /tmp/skopeo_out.$$ || cat /tmp/skopeo_out.$$
      else
        cat /tmp/skopeo_out.$$
      fi
      rm -f /tmp/skopeo_out.$$ || true
    else
      log "skopeo failed to list tags for ${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}; raw output follows"
      cat /tmp/skopeo_out.$$ 2>/dev/null || true
      rm -f /tmp/skopeo_out.$$ || true
    fi
  else
    log "Skipping remote listing: AWS CLI unavailable or registry not ECR, and 'skopeo' not installed to query the registry directly"
    log "To enable remote listing either install 'aws' and provide AWS_REGION and credentials, or install 'skopeo' so the script can query the registry using the existing docker credentials"
  fi
fi
