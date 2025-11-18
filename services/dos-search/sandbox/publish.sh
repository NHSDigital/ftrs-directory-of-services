#!/usr/bin/env bash

set -euo pipefail

ENVIRONMENT="${1:-}"
API_NAME="${2:-}"
OAS_SPEC_PATH="${3:-}"
ACCESS_TOKEN="${ACCESS_TOKEN:-}"

if [[ -z "$ENVIRONMENT" || -z "$API_NAME" || -z "$OAS_SPEC_PATH" ]]; then
  echo "Usage: $0 <environment> <api-name> <oas-spec-path>" >&2
  exit 1
fi

if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "ACCESS_TOKEN is not set. Export it first." >&2
  exit 1
fi

for dep in curl jq; do
  if ! command -v "$dep" >/dev/null 2>&1; then
    echo "Required dependency missing: $dep" >&2
    exit 1
  fi
done

if [[ ! -f "$OAS_SPEC_PATH" ]]; then
  echo "OAS spec file not found: $OAS_SPEC_PATH" >&2
  exit 1
fi

BASE_URL="https://proxygen.prod.api.platform.nhs.uk"

echo "Deploying API proxy instance for $API_NAME to $ENVIRONMENT..."
RESPONSE=$(curl -fsS -w '\n%{http_code}' --request POST \
  --url "${BASE_URL}/apis/${API_NAME}/environments/${ENVIRONMENT}/deploy" \
  --header "Authorization: Bearer ${ACCESS_TOKEN}" \
  --header "Content-Type: multipart/form-data" \
  --form "oasSpec=@${OAS_SPEC_PATH}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [[ "$HTTP_CODE" -ge 400 ]]; then
  echo "Deployment failed with status $HTTP_CODE" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "Deployment initiated for $API_NAME in $ENVIRONMENT"
