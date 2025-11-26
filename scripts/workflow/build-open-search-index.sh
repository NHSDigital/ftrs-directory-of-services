#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

OPEN_SEARCH_DOMAIN=${OPEN_SEARCH_DOMAIN:-}
INDEX=${INDEX:-}
WORKSPACE=${WORKSPACE:-}
AWS_REGION=${AWS_REGION:-}
AWS_SERVICE=${AWS_SERVICE:-aoss}

err(){ printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >&2; }
[ -n "$OPEN_SEARCH_DOMAIN" ] || { err "ERROR: OPEN_SEARCH_DOMAIN not set"; exit 2; }
[ -n "$INDEX" ] || { err "ERROR: INDEX not set"; exit 2; }

# If short collection name, resolve via OpenSearch Serverless API
if [[ "$OPEN_SEARCH_DOMAIN" != *.* ]]; then
  AWS_HOST=$(aws opensearchserverless get-collection --id "$OPEN_SEARCH_DOMAIN" --query 'collection.endpoint' --output text 2>/dev/null || true)
  if [[ -z "$AWS_HOST" || "$AWS_HOST" == "None" ]]; then
    err "ERROR: could not resolve serverless collection '$OPEN_SEARCH_DOMAIN' via AWS API"
    exit 2
  fi
  OPEN_SEARCH_DOMAIN=${AWS_HOST#https://}
fi

# normalize workspace
if [[ -n "$WORKSPACE" && "${WORKSPACE:0:1}" != "-" ]]; then WORKSPACE="-$WORKSPACE"; fi
FINAL_INDEX="${INDEX}${WORKSPACE}"

PAYLOAD='{"settings":{"number_of_shards":1},"mappings":{"properties":{"primary_key":{"type":"keyword"}}}}'
URL="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"

if command -v awscurl >/dev/null 2>&1; then
  awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X PUT "${URL}" -H "Content-Type: application/json" -d "${PAYLOAD}"
else
  curl -sS -X PUT "${URL}" -H "Content-Type: application/json" -d "${PAYLOAD}"
fi

err "Index ${FINAL_INDEX} created (or already exists) on ${OPEN_SEARCH_DOMAIN}"
