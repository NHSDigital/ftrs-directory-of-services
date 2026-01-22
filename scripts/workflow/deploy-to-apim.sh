#!/bin/bash

# Script to deploy API spec to Proxygen APIM
# Required environment variables: API_NAME, PROXY_ENV, ACCESS_TOKEN, MODIFIED_SPEC_PATH, PROXYGEN_URL
# Optional environment variables: WORKSPACE (when specified deploy a workspaced proxy)

set -e

# Validate required environment variables
if [ -z "$API_NAME" ]; then
    echo "Error: API_NAME environment variable is required" >&2
    exit 1
fi

if [ -z "$PROXY_ENV" ]; then
    echo "Error: PROXY_ENV environment variable is required" >&2
    exit 1
fi

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: ACCESS_TOKEN environment variable is required" >&2
    exit 1
fi

if [ -z "$MODIFIED_SPEC_PATH" ]; then
    echo "Error: MODIFIED_SPEC_PATH environment variable is required" >&2
    exit 1
fi

if [ -z "$PROXYGEN_URL" ]; then
    echo "Error: PROXYGEN_URL environment variable is required" >&2
    exit 1
fi

# Map internal API names to Proxygen API names
PROXYGEN_API_NAME="${API_NAME}"
if [ "$API_NAME" = "dos-ingest" ]; then
    PROXYGEN_API_NAME="uec-dos-ingestion"
fi

echo "Using internal API name: $API_NAME" >&2
echo "Mapped Proxygen API name: $PROXYGEN_API_NAME" >&2

if [ ! -f "$MODIFIED_SPEC_PATH" ]; then
    echo "Error: Modified spec file not found at $MODIFIED_SPEC_PATH" >&2
    exit 1
fi

# Set instance name based on workspace
if [ -n "$WORKSPACE" ]; then
    # If workspace is set, deploy a workspaced proxy
    # e.g., dos-search-ftrs-000_FHIR_R4
    INSTANCE_NAME="${API_NAME}-${WORKSPACE}_FHIR_R4"
else
    # Otherwise use just the API_NAME
    # e.g., dos-search_FHIR_R4
    INSTANCE_NAME="${API_NAME}_FHIR_R4"
fi

# Deploy to Proxygen using the environment/instance endpoint
echo "Deploying to Proxygen API..." >&2
echo "Endpoint: PUT ${PROXYGEN_URL}/apis/${API_NAME}/environments/${PROXY_ENV}/instances/${INSTANCE_NAME}" >&2

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=2

# Attempt deployment with retries
for attempt in $(seq 1 $MAX_RETRIES); do
    if [ $attempt -gt 1 ]; then
        echo "Retry attempt $attempt of $MAX_RETRIES..." >&2
        sleep $RETRY_DELAY
        RETRY_DELAY=$((RETRY_DELAY * 2))  # Exponential backoff
    fi

    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
        "${PROXYGEN_URL}/apis/${PROXYGEN_API_NAME}/environments/${PROXY_ENV}/instances/${INSTANCE_NAME}" \
        -H "Authorization: Bearer $ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d @"$MODIFIED_SPEC_PATH")

    # Extract HTTP status code and response body
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)

    # Check if successful
    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ] || [ "$HTTP_CODE" -eq 204 ]; then
        break
    fi

    if [ $attempt -lt $MAX_RETRIES ]; then
        echo "Request failed with HTTP $HTTP_CODE, retrying..." >&2
    fi
done

# Clean up temporary spec file
rm -f "$MODIFIED_SPEC_PATH"

# Check response
if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
    echo "✓ Successfully deployed API spec to Proxygen" >&2
    echo "$BODY"
    exit 0
elif [ "$HTTP_CODE" -eq 204 ]; then
    echo "✓ Successfully deployed API spec to Proxygen (no content returned)" >&2
    exit 0
else
    echo "Error: Failed to deploy API spec (HTTP $HTTP_CODE)" >&2
    echo "Response: $BODY" >&2
    exit 1
fi
