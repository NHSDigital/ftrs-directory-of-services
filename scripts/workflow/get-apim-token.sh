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

# Create Python script for JWT generation
cat > /tmp/create_jwt.py << 'PYTHON_SCRIPT'
import uuid
from time import time

import jwt
import sys
import os
import json

def create_signed_jwt(proxygen_jwt_secrets):
    """Create a signed JWT for APIM authentication"""
    try:
        proxygen_jwt_creds = json.loads(proxygen_jwt_secrets)

        # Set JWT claims
        claims = {
            "sub": proxygen_jwt_creds["client_id"],
            "iss": proxygen_jwt_creds["client_id"],
            "jti": str(uuid.uuid4()),
            "aud": proxygen_jwt_creds["token_url"],
            "exp": int(time()) + 300,
        }

        signed_jwt = jwt.encode(
          claims, proxygen_jwt_creds["private_key"], algorithm="RS512", headers={'kid': proxygen_jwt_creds["kid"]}
        )

        return signed_jwt

    except Exception as e:
        print(f"Error creating signed JWT: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    proxygen_jwt_secrets = os.environ.get('PROXYGEN_JWT_SECRETS')

    signed_jwt = create_signed_jwt(proxygen_jwt_secrets)
    print(signed_jwt)
PYTHON_SCRIPT

# Generate signed JWT
echo "Creating signed JWT..." >&2
SIGNED_JWT=$(token_url="$token_url" python3 /tmp/create_jwt.py)

if [ -z "$SIGNED_JWT" ]; then
    echo "Error: Failed to create signed JWT" >&2
    rm -f /tmp/create_jwt.py
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

# Clean up temporary file
rm -f /tmp/create_jwt.py

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
echo $ACCESS_TOKEN
