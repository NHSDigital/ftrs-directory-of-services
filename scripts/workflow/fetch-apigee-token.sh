#!/bin/bash

set -euo pipefail

# Fetch and export Apigee access token via Proxygen
# Usage: API_NAME=<api_name> ACCESS_TOKEN=<access_token> PROXYGEN_BASE_URL=<proxygen_base_url> fetch-apigee-token.sh

if [[ -z "${ACCESS_TOKEN}" ]]; then
  echo "ACCESS_TOKEN environment variable is required" >&2
  exit 1
fi

if [[ -z "${API_NAME}" ]]; then
  echo "API_NAME environment variable is required" >&2
  exit 1
fi

if [[ -z "${PROXYGEN_BASE_URL}" ]]; then
  echo "PROXYGEN_BASE_URL environment variable is required" >&2
  exit 1
fi

BASE_URL="${PROXYGEN_BASE_URL%/}"
TOKEN_ENDPOINT="${BASE_URL}/apis/${API_NAME}/pytest-nhsd-apim-token"

RESPONSE=$(curl -fsS --request GET --url "$TOKEN_ENDPOINT" --header "Authorization: Bearer ${ACCESS_TOKEN}") || {
  echo "Failed to reach Proxygen API" >&2
  exit 1
}

APIGEE_ACCESS_TOKEN=$(echo "$RESPONSE" | yq -r .pytest_nhsd_apim_token | tr -d '\n') || {
  echo "Failed to extract token from response" >&2
  exit 1
}

echo "$APIGEE_ACCESS_TOKEN"
