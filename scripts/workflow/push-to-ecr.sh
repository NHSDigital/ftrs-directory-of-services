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
IS_ECR=false
if printf '%s' "$REGISTRY_HOST" | grep -q 'dkr.ecr.'; then IS_ECR=true; fi
AWS_AVAILABLE=false
if command -v aws >/dev/null 2>&1; then AWS_AVAILABLE=true; fi
[ -n "$USER" -a -n "$PASSWORD" ] || die "No usable login credentials returned from Proxygen"
printf '%s' "$PASSWORD" | docker login --username "$USER" --password-stdin "$REGISTRY_HOST"

REMOTE_COMMIT_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:${REMOTE_IMAGE_TAG}"
REMOTE_LATEST_TAG="${REGISTRY_HOST}/${REMOTE_IMAGE_NAME}:latest"

LATEST_PUSHED=false

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
  s=$(printf '%s' "$iso" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/\.[0-9]+//; s/Z$//')
  if date -d "$s" +%s >/dev/null 2>&1; then date -d "$s" +%s 2>/dev/null && return 0; fi
  printf '0'
}

if [ "$PUSH_LATEST" = "true" ]; then
  if [ "$REMOTE_IMAGE_TAG" = "latest" ]; then
    log "IMAGE_TAG is 'latest' - skipping separate latest"
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
      LATEST_PUSHED=true
    fi
  fi
else
  log "Skipping latest tag push (PUSH_LATEST=${PUSH_LATEST})"
fi

LATEST_SUFFIX=""
[ "$PUSH_LATEST" = "true" ] && LATEST_SUFFIX=" and latest"
log "Image pushed successfully to ${REMOTE_COMMIT_TAG}${LATEST_SUFFIX}"

LIST_LIMIT=${LIST_LIMIT:-5}
TMP_TAGS=$(mktemp /tmp/registry_tags.XXXXXX)
TMP_MANIFEST=$(mktemp /tmp/registry_manifest.XXXXXX)
TMP_CONFIG=$(mktemp /tmp/registry_config.XXXXXX)
TMP_INDEX=$(mktemp /tmp/registry_index.XXXXXX)
TMP_TAG_LIST=$(mktemp /tmp/registry_tags_list.XXXXXX)
trap 'rm -f "$TMP_TAGS" "$TMP_MANIFEST" "$TMP_CONFIG" "$TMP_INDEX" "$TMP_TAG_LIST" 2>/dev/null || true' EXIT

if ! http_get "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/tags/list" -o "$TMP_TAGS" 2>/dev/null; then
  log "Failed to fetch tags for ${REMOTE_IMAGE_NAME}" && sed -n '1,200p' "$TMP_TAGS" || true
  exit 0
fi

if command -v jq >/dev/null 2>&1; then jq -r '.tags[]' "$TMP_TAGS" > "$TMP_TAG_LIST" 2>/dev/null || true; else sed -n 's/.*"tags"[[:space:]]*:[[:space:]]*\[//p' "$TMP_TAGS" | tr -d '[]" ' | tr ',' '\n' > "$TMP_TAG_LIST" || true; fi
TAG_COUNT=$(wc -l < "$TMP_TAG_LIST" 2>/dev/null || echo 0)
log "Found ${TAG_COUNT} tags for ${REMOTE_IMAGE_NAME} (is_ecr=${IS_ECR}, aws_available=${AWS_AVAILABLE})"
[ -s "$TMP_TAG_LIST" ] || { log "No tags found for ${REMOTE_IMAGE_NAME}"; exit 0; }

: >"$TMP_INDEX"
while IFS= read -r tag; do
  if http_get "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${tag}" -o "$TMP_MANIFEST" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then CONFIG_DIGEST=$(jq -r '.config.digest // empty' "$TMP_MANIFEST" 2>/dev/null || true); else CONFIG_DIGEST=$(grep -o '"config"[^{]*{[^}]*"digest"[[:space:]]*:[[:space:]]*"[^"]*"' "$TMP_MANIFEST" | sed -E 's/.*"digest"[[:space:]]*:[[:space:]]*"([^\"]*)"/\1/' | head -1 || true); fi
    MANIFEST_DIGEST=$(http_head "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/manifests/${tag}" 2>/dev/null | awk -F': ' '/[Dd]ocker-Content-Digest/ {print $2}' | tr -d '\r' || true)
  else
    CONFIG_DIGEST=""
    MANIFEST_DIGEST=""
  fi
  CREATED=""
  DIGEST=""
  if [ -n "$CONFIG_DIGEST" ]; then
    if [ "$IS_ECR" = "true" ] && [ "$AWS_AVAILABLE" = "true" ]; then
      AWS_REGION_EFFECTIVE="${AWS_REGION:-eu-west-2}"
      AWS_PUSHDAT=$(aws ecr describe-images --repository-name "$REMOTE_IMAGE_NAME" --region "$AWS_REGION_EFFECTIVE" --image-ids imageTag="$tag" --query 'imageDetails[0].imagePushedAt' --output text 2>/dev/null || true)
      if [ -n "$AWS_PUSHDAT" ] && [ "$AWS_PUSHDAT" != "None" ]; then
        CREATED="$AWS_PUSHDAT"
        log "AWS ECR provided pushedAt for ${tag}: ${CREATED}"
      fi
    fi
    if curl --max-time 10 --retry 2 --retry-connrefused -fsS -u "${USER}:${PASSWORD}" "https://${REGISTRY_HOST}/v2/${REMOTE_IMAGE_NAME}/blobs/${CONFIG_DIGEST}" -o "$TMP_CONFIG" 2>/dev/null; then
      if command -v jq >/dev/null 2>&1; then
        CREATED=$(jq -r '.created // .created_at // empty' "$TMP_CONFIG" 2>/dev/null || true)
        if [ -z "$CREATED" ]; then
          CREATED=$(jq -r '.history[]? | try (fromjson | .created) // empty' "$TMP_CONFIG" 2>/dev/null | head -n1 || true)
        fi
      else
        CREATED=$(grep -o '"created"[[:space:]]*:[[:space:]]*"[^"]*"' "$TMP_CONFIG" | head -1 | sed -E 's/.*:[[:space:]]*"([^\"]*)"/\1/' || true)
        if [ -z "$CREATED" ]; then
          CREATED=$(grep -o '"v1Compatibility"[^{]*{[^}]*"created"[[:space:]]*:[[:space:]]*"[^"]*"' "$TMP_CONFIG" | sed -E 's/.*"created"[[:space:]]*:[[:space:]]*"([^\"]*)".*/\1/' | head -n1 || true)
        fi
      fi
      if [ -n "$MANIFEST_DIGEST" ]; then
        DIGEST="$MANIFEST_DIGEST"
      else
        DIGEST="$CONFIG_DIGEST"
      fi
    fi
  fi
  if [ -z "$CREATED" ]; then EPOCH=0; CREATED=""; else EPOCH=$(epoch_from_iso "$CREATED" 2>/dev/null || echo 0); fi
  printf '%s\t%s\t%s\t%s\n' "$EPOCH" "$CREATED" "$tag" "$DIGEST" >>"$TMP_INDEX"
done < "$TMP_TAG_LIST"
rm -f "$TMP_TAG_LIST" || true

sort -nr "$TMP_INDEX" | head -n "$LIST_LIMIT" >"${TMP_INDEX}.top" || true

printf '%s\t%s\t%s\n' "IMAGE" "DIGEST" "PUSHED_AT"
while IFS=$'\t' read -r EPOCH CREATED TAG DIGEST; do
  if printf '%s' "$TAG" | grep -qE '^sha256:' || printf '%s' "$TAG" | grep -qE '^[0-9a-f]{64}$'; then
    IMAGE_NAME="${REMOTE_IMAGE_NAME}@${TAG}"
  else
    IMAGE_NAME="${REMOTE_IMAGE_NAME}:${TAG}"
  fi
  [ -z "${CREATED}" ] && DISPLAY_CREATED="" || DISPLAY_CREATED="${CREATED}"
  printf '%s\t%s\t%s\n' "$IMAGE_NAME" "$DIGEST" "$DISPLAY_CREATED"
done <"${TMP_INDEX}.top" | (command -v column >/dev/null 2>&1 && column -t -s $'\t' || cat)

printf '\nLATEST_PUSHED=%s\n' "$LATEST_PUSHED"
