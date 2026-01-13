#!/bin/bash

# Script to generate JWT and retrieve APIM access token
# Required environment variables: PRIVATE_KEY, KID, CLIENT_ID, TOKEN_URL

set -e

# Get the secret string
    export PROXYGEN_JWT_SECRETS=$(aws secretsmanager get-secret-value \
      --secret-id /ftrs-dos/$ENV/$API_NAME-proxygen-jwt-credentials \
      --query SecretString \
      --region $AWS_REGION \
      --output text)

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Generate signed JWT
echo "Creating signed JWT..." >&2
SIGNED_JWT=$(PROXYGEN_JWT_SECRETS="$PROXYGEN_JWT_SECRETS" python3 "$SCRIPT_DIR/create_jwt.py")

if [ -z "$SIGNED_JWT" ]; then
    echo "Error: Failed to create signed JWT" >&2
    exit 1
fi

TOKEN_URL=$(echo "$PROXYGEN_JWT_SECRETS" | jq -r .token_url)
# Request access token
echo "Requesting access token from APIM..." >&2
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$TOKEN_URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer" \
    -d "client_assertion=$SIGNED_JWT")

# Extract HTTP status code and response body
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

# Check response
if [ "$HTTP_CODE" -ne 200 ]; then
    echo "Error: Failed to get access token (HTTP $HTTP_CODE)" >&2
    echo "Response: $BODY" >&2
    exit 1
fi

# Extract access token
ACCESS_TOKEN=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$ACCESS_TOKEN" ]; then
    echo "Error: No access token in response" >&2
    echo "Response: $BODY" >&2
    exit 1
fi

echo "Successfully retrieved access token" >&2
echo "$ACCESS_TOKEN"
