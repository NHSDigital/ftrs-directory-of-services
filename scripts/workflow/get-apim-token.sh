#!/bin/bash

# Script to generate JWT and retrieve APIM access token
# Required environment variables: PRIVATE_KEY, KID, CLIENT_ID, TOKEN_URL

set -euo pipefail

log() { echo "[get-apim-token] $*" >&2; }
die() { log "ERROR: $*"; exit 1; }

# Determine which env value to use for secret path
# Prefer ENV (caller may pass), fall back to ENVIRONMENT, then to mgmt
SECRET_ENV="${ENV:-${ENVIRONMENT:-mgmt}}"

# Build candidate secret ids
SECRET_CANDIDATES=(
  "/ftrs-dos/${SECRET_ENV}/${API_NAME}-proxygen-jwt-credentials"
  "/ftrs-dos/${ENVIRONMENT:-mgmt}/${API_NAME}-proxygen-jwt-credentials"
  "/ftrs-dos/mgmt/${API_NAME}-proxygen-jwt-credentials"
)

PROXYGEN_JWT_SECRETS=""
for sid in "${SECRET_CANDIDATES[@]}"; do
  log "Trying to read secret id: $sid"
  if PROXYGEN_JWT_SECRETS=$(
    aws secretsmanager get-secret-value \
      --secret-id "$sid" \
      --region "${AWS_REGION:-${AWS_DEFAULT_REGION:-}}" \
      --query SecretString \
      --output text 2>/dev/null
  ); then
    log "Found secret: $sid"
    break
  else
    log "Secret not found or inaccessible: $sid"
  fi
done

if [ -z "${PROXYGEN_JWT_SECRETS:-}" ]; then
  die "Unable to read proxygen JWT secrets from Secrets Manager; tried: ${SECRET_CANDIDATES[*]}"
fi

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

# Export the secrets to the environment so python script can read them
export PROXYGEN_JWT_SECRETS

log "Creating signed JWT..."
SIGNED_JWT=$(python3 /tmp/create_jwt.py)

if [ -z "$SIGNED_JWT" ]; then
    rm -f /tmp/create_jwt.py
    die "Failed to create signed JWT"
fi

TOKEN_URL=$(echo "$PROXYGEN_JWT_SECRETS" | jq -r .token_url)
if [ -z "$TOKEN_URL" ] || [ "$TOKEN_URL" = "null" ]; then
  die "token_url missing from secrets"
fi

log "Requesting access token from APIM..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$TOKEN_URL" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=client_credentials" \
    -d "client_assertion_type=urn:ietf:params:oauth:client-assertion-type:jwt-bearer" \
    -d "client_assertion=$SIGNED_JWT") || die "Failed to reach APIM token endpoint"

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

rm -f /tmp/create_jwt.py

if [ "$HTTP_CODE" -ne 200 ]; then
    log "APIM token request failed (HTTP $HTTP_CODE)"
    log "Response body: $BODY"
    die "Failed to get access token (HTTP $HTTP_CODE)"
fi

ACCESS_TOKEN=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$ACCESS_TOKEN" ]; then
    log "APIM response body: $BODY"
    die "No access token in response"
fi

log "Successfully retrieved access token"
echo "$ACCESS_TOKEN"
