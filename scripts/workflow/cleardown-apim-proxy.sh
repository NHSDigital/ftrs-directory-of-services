#!/bin/bash

# Script to cleardown APIM proxy instance
# Required environment variables: API_NAME, PROXY_ENV, ACCESS_TOKEN, PROXYGEN_URL
# Optional environment variables: WORKSPACE (when specified, clears down a workspaced proxy)

set -e
EXPORTS_SET=0

# Validate required environment variables
if [[ -z "$API_NAME" ]]; then
  echo "Error: API_NAME is not set" >&2
  EXPORTS_SET=1
fi

if [[ -z "$PROXY_ENV" ]]; then
  echo "Error: PROXY_ENV is not set" >&2
  EXPORTS_SET=1
fi

if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "Error: ACCESS_TOKEN is not set" >&2
  EXPORTS_SET=1
fi

if [[ -z "$PROXYGEN_URL" ]]; then
  echo "Error: PROXYGEN_URL is not set" >&2
  EXPORTS_SET=1
fi

if [[ $EXPORTS_SET -eq 1 ]]; then
  echo "One or more required environment variables are missing. Exiting." >&2
  exit 1
fi

# Set instance name based on workspace
if [ -n "$WORKSPACE" ]; then
    INSTANCE_NAME="${API_NAME}-${WORKSPACE}_FHIR_R4"
else
    INSTANCE_NAME="${API_NAME}_FHIR_R4"
fi

echo "Clearing down proxy instance $INSTANCE_NAME from environment $PROXY_ENV for API $API_NAME" >&2

RESPONSE=$(curl -s -w "\n%{http_code}" --connect-timeout 10 --max-time 30 -X DELETE \
    "${PROXYGEN_URL}/apis/${API_NAME}/environments/${PROXY_ENV}/instances/${INSTANCE_NAME}" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✓ Proxy instance deleted" >&2
    exit 0
elif [ "$HTTP_CODE" -eq 404 ]; then
    echo "✓ Proxy instance not found" >&2
    echo "Response: $BODY" >&2
    exit 0
else
    echo "Error: Failed to cleardown proxy instance (HTTP $HTTP_CODE)" >&2
    echo "Response: $BODY" >&2
    exit 1
fi
