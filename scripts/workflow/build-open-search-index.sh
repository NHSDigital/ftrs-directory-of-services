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

# Resolve a Serverless collection name to an endpoint using list -> batch-get
resolve_serverless_collection(){
  local name="$1" region_arg aws_json id endpoint
  region_arg=${2:+--region "$2"}

  # find collection id by name
  id=$(aws opensearchserverless list-collections ${AWS_REGION:+--region "$AWS_REGION"} --query "collectionSummaries[?name=='${name}'].id | [0]" --output text 2>/dev/null || true)
  if [[ -z "$id" || "$id" == "None" ]]; then
    return 1
  fi

  # fetch details and try to extract the endpoint; try the common key first
  endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" ${AWS_REGION:+--region "$AWS_REGION"} --query 'collectionDetails[0].collectionEndpoint' --output text 2>/dev/null || true)
  if [[ -z "$endpoint" || "$endpoint" == "None" ]]; then
    endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" ${AWS_REGION:+--region "$AWS_REGION"} --query 'collectionDetails[0].endpoint' --output text 2>/dev/null || true)
  fi
  if [[ -z "$endpoint" || "$endpoint" == "None" ]]; then
    endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" ${AWS_REGION:+--region "$AWS_REGION"} --output json 2>/dev/null || true)
    # try a simple grep/json parse fallback if needed (pure shell: grep+sed)
    if [[ -n "$endpoint" ]]; then
      parsed=$(printf '%s' "$endpoint" | grep -o '"[^"]*endpoint[^"]*"[[:space:]]*:[[:space:]]*"[^"]*"' | sed -E 's/.*:[[:space:]]*"(.*)"/\1/' | head -n1 || true)
      if [[ -n "$parsed" ]]; then
        endpoint="$parsed"
      fi
    fi
  fi

  if [[ -n "$endpoint" && "$endpoint" != "None" ]]; then
    printf '%s' "$endpoint"
    return 0
  fi
  return 1
}

# If short collection name (no dot) try to resolve via Serverless APIs
if [[ "$OPEN_SEARCH_DOMAIN" != *.* ]]; then
  err "Resolving serverless collection '${OPEN_SEARCH_DOMAIN}' via AWS API"
  RESOLVED=$(resolve_serverless_collection "$OPEN_SEARCH_DOMAIN" "$AWS_REGION" || true)
  if [[ -n "$RESOLVED" ]]; then
    OPEN_SEARCH_DOMAIN=${RESOLVED#https://}
    err "AWS lookup found endpoint: ${OPEN_SEARCH_DOMAIN}"
  else
    err "ERROR: could not resolve serverless collection '${OPEN_SEARCH_DOMAIN}' via AWS API"
    err "Ensure the collection exists, the AWS CLI supports opensearchserverless, and the runner has proper permissions"
    exit 2
  fi
fi

# normalize workspace
if [[ -n "$WORKSPACE" && "${WORKSPACE:0:1}" != "-" ]]; then WORKSPACE="-$WORKSPACE"; fi
FINAL_INDEX="${INDEX}${WORKSPACE}"

PAYLOAD='{
  "mappings": {
    "properties": {
      "primary_key": {"type": "keyword"},
      "sgsd": {
        "type": "nested",
        "properties": {
          "sg": {"type": "integer"},
          "sd": {"type": "integer"}
        }
      }
    }
  }
}'
URL="https://${OPEN_SEARCH_DOMAIN}/${FINAL_INDEX}"

if command -v awscurl >/dev/null 2>&1; then
  awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X PUT "${URL}" -H "Content-Type: application/json" -d "${PAYLOAD}"
else
  curl -sS --fail --max-time 30 --retry 2 -X PUT "${URL}" -H "Content-Type: application/json" -d "${PAYLOAD}"
fi

err "Index ${FINAL_INDEX} created (or already exists) on ${OPEN_SEARCH_DOMAIN}"
