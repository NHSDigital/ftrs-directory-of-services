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

# Debug: print AWS region(s) so we can see what the runner is using
err "AWS_REGION: ${AWS_REGION:-<unset>}"
if [ -n "${AWS_DEFAULT_REGION:-}" ]; then
  err "AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}"
fi

# Print AWS account number for debugging (safe, region-aware)
if command -v aws >/dev/null 2>&1; then
  # Print aws CLI version so logs show whether aws is installed and which version
  AWS_CLI_VERSION=$(aws --version 2>&1 || true)
  err "aws CLI: ${AWS_CLI_VERSION}"

  # Capture aws STS output (stdout or stderr) for diagnostics. Don't print secrets.
  # Rely on AWS_REGION/AWS_DEFAULT_REGION environment variables instead of passing --region
  STS_OUT=$(aws sts get-caller-identity --query Account --output text 2>&1 || true)

  # If the output looks like an account number (digits), it's successful
  if [[ "${STS_OUT}" =~ ^[0-9]+$ ]]; then
    AWS_ACCOUNT="${STS_OUT}"
    err "AWS account: $AWS_ACCOUNT"
  else
    err "AWS account: unavailable (aws sts returned empty or failed)"
    # Print the aws CLI error text for debugging (may show AccessDenied, could not find credentials, etc.)
    err "aws sts error: ${STS_OUT}"
    err "Failing early because valid AWS credentials are required to resolve serverless collections"
    exit 3
  fi
else
  err "aws CLI not found; cannot determine AWS account"
  err "Failing early because aws CLI is required"
  exit 4
fi

# Resolve a Serverless collection name to an endpoint using list -> batch-get
resolve_serverless_collection(){
  local name="$1" region_arg aws_json id endpoint
  region_arg=${2:+--region "$2"}

  # find collection id by name
  id=$(aws opensearchserverless list-collections --query "collectionSummaries[?name=='${name}'].id | [0]" --output text 2>/dev/null || true)
  if [[ -z "$id" || "$id" == "None" ]]; then
    return 1
  fi

  # fetch details and try to extract the endpoint; try the common key first
  endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" --query 'collectionDetails[0].collectionEndpoint' --output text 2>/dev/null || true)
  if [[ -z "$endpoint" || "$endpoint" == "None" ]]; then
    endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" --query 'collectionDetails[0].endpoint' --output text 2>/dev/null || true)
  fi
  if [[ -z "$endpoint" || "$endpoint" == "None" ]]; then
    endpoint=$(aws opensearchserverless batch-get-collection --ids "$id" --output json 2>/dev/null || true)
    # try a simple grep/json parse fallback if needed (pure shell: grep+sed)
    if [[ -n "$endpoint" ]]; then
      parsed=$(printf '%s' "$endpoint" | grep -o '"[^" ]*endpoint[^" ]*"[[:space:]]*:[[:space:]]*"[^" ]*"' | sed -E 's/.*:[[:space:]]*"(.*)"/\1/' | head -n1 || true)
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

# Try awscurl first (signed requests), then curl as a fallback
if command -v awscurl >/dev/null 2>&1; then
  err "Using awscurl to create index"
  # Print awscurl version if available
  AWSCURL_VERSION=$(awscurl --version 2>&1 || true)
  err "awscurl: ${AWSCURL_VERSION}"

  # Use -- to separate options from the URI to avoid argv parsing issues
  awscurl --service "${AWS_SERVICE}" ${AWS_REGION:+--region "${AWS_REGION}"} -X PUT -H "Content-Type: application/json" -d "${PAYLOAD}" -- "${URL}"
else
  err "awscurl not found; falling back to curl (unsigned request may return 403)"
  curl -sS --fail --max-time 30 --retry 2 -X PUT "${URL}" -H "Content-Type: application/json" -d "${PAYLOAD}"
fi

err "Index ${FINAL_INDEX} created (or already exists) on ${OPEN_SEARCH_DOMAIN}"
