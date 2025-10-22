import os
import sys
import json
import uuid
import boto3
import jwt
import requests
from time import time

def get_config(env_name=None, region_name="eu-west-2"):
    """Load config from AWS Secrets Manager or environment variables."""
    config = {}

    secret_name = None
    if env_name:
        secret_name = f"/ftrs-dos/{env_name}/apim-jwt-credentials"

    if secret_name:
        try:
            client = boto3.client("secretsmanager", region_name=region_name)
            response = client.get_secret_value(SecretId=secret_name)
            secret_dict = json.loads(response["SecretString"])
            config.update(secret_dict)
            print(f"Loaded configuration from AWS Secrets Manager: {secret_name}")
        except Exception as e:
            print(f"Could not load secret from AWS Secrets Manager ({secret_name}): {e}")

    # Fallback to environment variables if secret missing or incomplete
    config.setdefault("api_key", os.getenv("API_KEY"))
    config.setdefault("private_key", os.getenv("PRIVATE_KEY"))
    config.setdefault("kid", os.getenv("KID"))
    config.setdefault("token_url", os.getenv("TOKEN_URL"))

    # Validate config
    required = ["api_key", "private_key", "kid", "token_url"]
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise ValueError(f"Missing required configuration keys: {', '.join(missing)}")

    # Restore newlines in private key if escaped
    config["private_key"] = config["private_key"].replace("\\n", "\n")

    return config

def generate_jwt(api_key, private_key, kid, token_url):
    """Generate a signed JWT using RS512 algorithm."""
    now = int(time())
    claims = {
        "sub": api_key,
        "iss": api_key,
        "jti": str(uuid.uuid4()),
        "aud": token_url,
        "exp": now + 600,  # 10 minutes
    }

    headers = {"kid": kid}

    token = jwt.encode(claims, private_key, algorithm="RS512", headers=headers)
    return token

def exchange_for_bearer(jwt_token, token_url):
    """Exchange the signed JWT for a Bearer token."""
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_token,
    }

    response = requests.post(token_url, data=data, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Token request failed: {response.status_code} - {response.text}")

    return response.json()["access_token"]

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_bearer_token.py <env>")
        sys.exit(1)

    env_name = sys.argv[1]
    config = get_config(env_name)

    jwt_token = generate_jwt(
        config["api_key"],
        config["private_key"],
        config["kid"],
        config["token_url"]
    )

    print("\nGenerated JWT successfully.\n")

    bearer_token = exchange_for_bearer(jwt_token, config["token_url"])

    print("🔐 Bearer Token:\n")
    print(bearer_token)


if __name__ == "__main__":
    main()
