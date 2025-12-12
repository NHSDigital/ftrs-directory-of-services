#!/usr/bin/env python3

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
