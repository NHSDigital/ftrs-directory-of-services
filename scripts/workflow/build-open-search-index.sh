#!/usr/bin/env bash

# Minimal, robust index-creation script
set -euo pipefail
IFS=$'\n\t'

OPEN_SEARCH_DOMAIN="${OPEN_SEARCH_DOMAIN:-""}"
INDEX="${INDEX:-""}"
WORKSPACE="${WORKSPACE:-""}"
SIGN_WITH_AWS="${SIGN_WITH_AWS:-false}"
AWS_REGION="${AWS_REGION:-""}"
AWS_SERVICE="${AWS_SERVICE:-es}"

log() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }

if [[ -z "${OPEN_SEARCH_DOMAIN}" ]]; then
  log "ERROR: OPEN_SEARCH_DOMAIN is not set"
  exit 2
fi
if [[ -z "${INDEX}" ]]; then
  log "ERROR: INDEX is not set"
  exit 2
fi

# Ensure WORKSPACE begins with '-' when non-empty
if [[ -n "${WORKSPACE}" && "${WORKSPACE:0:1}" != "-" ]]; then
  WORKSPACE="-${WORKSPACE}"
fi

FINAL_INDEX="${INDEX}${WORKSPACE}"
log "Creating index: ${FINAL_INDEX} on https://${OPEN_SEARCH_DOMAIN}"

# Payload (keep as before)
read -r -d '' INDEX_PAYLOAD <<'JSON' || true
{
  "settings": { "number_of_shards": 1 },
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "primary_key": { "type": "keyword" }
    }
  }
}
JSON

# Perform the PUT using awscurl if signing required, otherwise curl
URL="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"
if [[ "${SIGN_WITH_AWS}" == "true" ]]; then
  if ! command -v awscurl >/dev/null 2>&1; then
    log "ERROR: SIGN_WITH_AWS=true but awscurl not found. Install awscurl or set SIGN_WITH_AWS=false"
    exit 2
  fi
  log "Using awscurl to PUT index (service=${AWS_SERVICE}, region=${AWS_REGION:-<not-set>})"
  awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X PUT "${URL}" -H "Content-Type: application/json" -d "${INDEX_PAYLOAD}"
else
  log "Using curl to PUT index"
  curl -sS -X PUT "${URL}" -H "Content-Type: application/json" -d "${INDEX_PAYLOAD}"
fi

log "Index ${FINAL_INDEX} created (or already exists) on ${OPEN_SEARCH_DOMAIN}"
