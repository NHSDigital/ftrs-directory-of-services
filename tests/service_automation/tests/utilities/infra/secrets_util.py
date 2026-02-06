import os
from typing import Optional

import boto3
from loguru import logger


class GetSecretWrapper:
    """Secrets Manager wrapper that supports both real AWS and LocalStack.

    Args:
        endpoint_url: Optional endpoint URL for LocalStack or other compatible services.
                     If not provided, checks AWS_ENDPOINT_URL environment variable,
                     then falls back to real AWS.
    """

    def __init__(self, endpoint_url: Optional[str] = None):
        endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
        client_kwargs = {}
        if endpoint:
            client_kwargs["endpoint_url"] = endpoint
            logger.debug(f"Using Secrets Manager endpoint: {endpoint}")
        self.client = boto3.client("secretsmanager", **client_kwargs)

    def get_secret(self, secret_name):
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_name
            )
            logger.info("Secret retrieved successfully.")
            return get_secret_value_response["SecretString"]
        except self.client.exceptions.ResourceNotFoundException:
            msg = f"The requested secret {secret_name} was not found."
            logger.info(msg)
            return msg
        except Exception as e:
            logger.error(f"An unknown error occurred: {str(e)}.")
            raise
