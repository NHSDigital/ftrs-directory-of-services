#!/bin/bash

# Script to generate JWT and retrieve APIM access token
# Required environment variables: PRIVATE_KEY, KID, API_ID

set -e

# Check required environment variables
if [ -z "$PRIVATE_KEY" ] || [ -z "$KID" ] || [ -z "$API_ID" ]; then
    echo "Error: Missing required environment variables (PRIVATE_KEY, KID, or API_ID)" >&2
    exit 1
fi

# Configuration
AUTH_ENDPOINT="https://api.service.nhs.uk/oauth2/token"
REALM_URL="https://api.service.nhs.uk/oauth2/token"

# Create Python script for JWT generation
cat > /tmp/create_jwt.py << 'PYTHON_SCRIPT'
import jwt
import time
import sys
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def create_signed_jwt(private_key_pem, kid, api_id, realm_url):
    """Create a signed JWT for APIM authentication"""
    try:
        # Load the private key from PEM format
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8'),
            password=None,
            backend=default_backend()
        )

        # Set JWT claims
        current_time = int(time.time())
        payload = {
            'iss': api_id,
            'sub': api_id,
            'aud': realm_url,
            'exp': current_time + 300,  # 5 minutes expiry
            'iat': current_time,
            'jti': f"{api_id}-{current_time}"
        }

        # Create signed JWT
        headers = {
            'kid': kid,
            'alg': 'RS256',
            'typ': 'JWT'
        }

        signed_jwt = jwt.encode(
            payload,
            private_key,
            algorithm='RS256',
            headers=headers
        )

        return signed_jwt

    except Exception as e:
        print(f"Error creating signed JWT: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    private_key = os.environ.get('PRIVATE_KEY')
    kid = os.environ.get('KID')
    api_id = os.environ.get('API_ID')
    realm_url = os.environ.get('REALM_URL')

    if not all([private_key, kid, api_id, realm_url]):
        print("Missing required environment variables", file=sys.stderr)
        sys.exit(1)

    signed_jwt = create_signed_jwt(private_key, kid, api_id, realm_url)
    print(signed_jwt)
PYTHON_SCRIPT

# Generate signed JWT
echo "Creating signed JWT..." >&2
SIGNED_JWT=$(REALM_URL="$REALM_URL" python3 /tmp/create_jwt.py)

if [ -z "$SIGNED_JWT" ]; then
    echo "Error: Failed to create signed JWT" >&2
    rm -f /tmp/create_jwt.py
    exit 1
fi

# Request access token
echo "Requesting access token from APIM..." >&2
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$AUTH_ENDPOINT" \
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
echo "$ACCESS_TOKEN"
