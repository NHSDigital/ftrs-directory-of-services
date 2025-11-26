#!/usr/bin/env bash

# Minimal index-creation script — prefer awscurl when available, otherwise curl
set -euo pipefail
IFS=$'\n\t'

OPEN_SEARCH_DOMAIN="${OPEN_SEARCH_DOMAIN:-""}"
INDEX="${INDEX:-""}"
WORKSPACE="${WORKSPACE:-""}"
AWS_REGION="${AWS_REGION:-""}"
AWS_SERVICE="${AWS_SERVICE:-aoss}"

log(){ printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }

# Basic validation
if [[ -z "$OPEN_SEARCH_DOMAIN" || -z "$INDEX" ]]; then
  log "ERROR: OPEN_SEARCH_DOMAIN and INDEX must be set"
  log "  Received: OPEN_SEARCH_DOMAIN='${OPEN_SEARCH_DOMAIN:-<unset>}' INDEX='${INDEX:-<unset>}'"
  log "  Tip: pass the OpenSearch endpoint as the 'domain' input to the action/workflow (or ensure aws CLI can resolve the collection name)"
  exit 2
fi

# If OPEN_SEARCH_DOMAIN looks like a short collection name (no dot), try to resolve it via the AWS CLI
if [[ "$OPEN_SEARCH_DOMAIN" != *.* ]]; then
  log "OPEN_SEARCH_DOMAIN appears to be a collection name: '${OPEN_SEARCH_DOMAIN}' — attempting AWS lookup"

  # Try modern OpenSearch API first (silence errors)
  AWS_HOST="$(aws opensearch describe-domain --domain-name "${OPEN_SEARCH_DOMAIN}" --query 'DomainStatus.Endpoint' --output text 2>/dev/null || true)"

  if [[ -n "$AWS_HOST" && "$AWS_HOST" != "None" ]]; then
    log "AWS lookup found endpoint: ${AWS_HOST}"
    OPEN_SEARCH_DOMAIN="$AWS_HOST"
  else
    log "ERROR: AWS lookup did not find a domain named '${OPEN_SEARCH_DOMAIN}'"
    log "  Ensure the OpenSearch domain exists and the runner has permissions (cloud: opensearch:DescribeDomain or es:DescribeElasticsearchDomain)."
    log "  Alternatively, pass the explicit FQDN as 'domain' when calling the action/workflow."
    exit 2
  fi
fi

# normalize workspace to a leading dash when provided
if [[ -n "$WORKSPACE" && "${WORKSPACE:0:1}" != "-" ]]; then
  WORKSPACE="-${WORKSPACE}"
fi
FINAL_INDEX="${INDEX}${WORKSPACE}"
log "Creating index: ${FINAL_INDEX} on https://${OPEN_SEARCH_DOMAIN}"

# compact mapping payload
read -r -d '' INDEX_PAYLOAD <<'JSON' || true
{
  "settings": { "number_of_shards": 1 },
  "mappings": {
    "properties": {
      "primary_key": { "type": "keyword" },
      "sgsd": {
        "type": "nested",
        "properties": {
          "sg": { "type": "integer" },
          "sd": { "type": "integer" }
        }
      }
    }
  }
}
JSON

URL="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"

# prefer awscurl for SigV4 signing (serverless); fallback to curl
if command -v awscurl >/dev/null 2>&1; then
  log "Using awscurl to PUT index (service=${AWS_SERVICE}, region=${AWS_REGION:-<not-set>})"
  awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X PUT "${URL}" -H "Content-Type: application/json" -d "${INDEX_PAYLOAD}"
else
  log "awscurl not found — using curl to PUT index"
  curl -sS -X PUT "${URL}" -H "Content-Type: application/json" -d "${INDEX_PAYLOAD}"
fi

log "Index ${FINAL_INDEX} created (or already exists) on ${OPEN_SEARCH_DOMAIN}"
