import json
import os
import uuid
from functools import cache
from time import time
from typing import Dict, Optional

import boto3
import jwt
import requests
from botocore.exceptions import ClientError


class JWTCredentialsError(ValueError):
    """Raised when JWT credentials are missing or invalid."""

    def __init__(self, missing_items: list[str], item_type: str = "environment variables") -> None:
        self.missing_items = missing_items
        self.item_type = item_type
        super().__init__(f"Missing required {item_type}: {missing_items}")


class JWTSecretError(RuntimeError):
    """Raised when JWT secret retrieval fails."""

    def __init__(self, secret_name: str, original_error: Exception) -> None:
        self.secret_name = secret_name
        self.original_error = original_error
        super().__init__(f"Failed to get secret {secret_name}: {original_error}")


class JWTTokenError(RuntimeError):
    """Raised when JWT token generation fails."""

    def __init__(self, error_type: str = "general", response_body: dict = None, original_error: Exception = None) -> None:
        self.error_type = error_type
        self.response_body = response_body
        self.original_error = original_error

        if error_type == "no_access_token":
            message = f"No access token in response: {response_body}"
        elif error_type == "request_failed":
            message = "Failed to fetch bearer token"
        else:
            message = "JWT token generation failed"

        super().__init__(message)


class JWTAuthenticator:
    def __init__(self, environment: Optional[str] = None, region: str = "eu-west-2", secret_name: Optional[str] = None) -> None:
        self.environment = environment or os.environ.get("ENVIRONMENT", "local")
        self.region = region or os.environ.get("AWS_REGION", "eu-west-2")
        self.custom_secret_name = secret_name

    def get_jwt_credentials(self) -> Dict[str, str]:
        if self.environment == "local":
            return self._get_local_credentials()
        return self._get_aws_credentials()

    def _get_local_credentials(self) -> Dict[str, str]:
        required_vars = ["LOCAL_API_KEY", "LOCAL_PRIVATE_KEY", "LOCAL_KID", "LOCAL_TOKEN_URL"]
        missing_vars = [var for var in required_vars if not os.environ.get(var)]

        if missing_vars:
            raise JWTCredentialsError(missing_vars, "environment variables")

        return {
            "api_key": os.environ["LOCAL_API_KEY"],
            "private_key": os.environ["LOCAL_PRIVATE_KEY"],
            "kid": os.environ["LOCAL_KID"],
            "token_url": os.environ["LOCAL_TOKEN_URL"]
        }

    def _get_aws_credentials(self) -> Dict[str, str]:
        if self.custom_secret_name:
            secret_name = self.custom_secret_name
        else:
            project = os.environ.get("PROJECT_NAME", "ftrs")
            secret_name = f"/{project}/{self.environment}/apim-jwt-credentials"

        try:
            client = boto3.client("secretsmanager", region_name=self.region)
            response = client.get_secret_value(SecretId=secret_name)
            secret_str = response["SecretString"]
            creds = json.loads(secret_str)

            required_keys = ["api_key", "private_key", "kid", "token_url"]
            missing_keys = [key for key in required_keys if key not in creds]

            if missing_keys:
                raise JWTCredentialsError(missing_keys, "JWT credential keys")
            else:
                return creds
        except ClientError as e:
            raise JWTSecretError(secret_name, e) from e

    def generate_assertion(self, expiry_seconds: int = 300) -> str:
        creds = self.get_jwt_credentials()
        now = int(time())

        claims = {
            "sub": creds["api_key"],
            "iss": creds["api_key"],
            "jti": str(uuid.uuid4()),
            "aud": creds["token_url"],
            "exp": now + expiry_seconds,
        }
        headers = {"kid": creds["kid"]}

        token = jwt.encode(claims, creds["private_key"], algorithm="RS512", headers=headers)
        return token

    @cache
    def get_bearer_token(self) -> str:
        creds = self.get_jwt_credentials()
        jwt_assertion = self.generate_assertion()

        data = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": jwt_assertion,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            resp = requests.post(creds["token_url"], data=data, headers=headers, timeout=10)
            resp.raise_for_status()
            body = resp.json()
            token = body.get("access_token")
            if not token:
                raise JWTTokenError("no_access_token", body)
            else:
                return token
        except requests.exceptions.RequestException as e:
            raise JWTTokenError("request_failed", original_error=e) from e

    def get_auth_headers(self) -> Dict[str, str]:
        bearer_token = self.get_bearer_token()
        return {"Authorization": f"Bearer {bearer_token}"}
