"""Secrets Manager testcontainer fixtures for integration testing.

This module provides pytest fixtures for running integration tests against
AWS Secrets Manager using LocalStack testcontainers.

Usage in conftest.py:
    from ftrs_common.testing.secrets_fixtures import (
        secrets_client,
        create_secret,
        get_secret,
        delete_secret,
    )

    # Re-export fixtures for pytest discovery
    secrets_client = secrets_client

Example test:
    def test_get_api_key(secrets_client):
        create_secret(
            secrets_client,
            secret_name="/ftrs/test/api-key",
            secret_value={"api_key": "test-key-123"},
        )
        secret = get_secret(secrets_client, "/ftrs/test/api-key")
        assert secret["api_key"] == "test-key-123"
"""

import json
from typing import Any, Generator

import boto3
import pytest
from loguru import logger
from testcontainers.localstack import LocalStackContainer


@pytest.fixture(scope="session")
def secrets_client(
    localstack_container: LocalStackContainer,
) -> Generator[Any, None, None]:
    """
    Boto3 Secrets Manager client connected to LocalStack.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Boto3 Secrets Manager client
    """
    endpoint_url = localstack_container.get_url()
    client = boto3.client(
        "secretsmanager",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )
    yield client


def create_secret(
    client: Any,
    secret_name: str,
    secret_value: str | dict,
    description: str = "",
) -> dict[str, Any]:
    """
    Create a secret in Secrets Manager.

    Args:
        client: Boto3 Secrets Manager client
        secret_name: Name/ID of the secret
        secret_value: Secret value (string or dict that will be JSON-serialized)
        description: Optional description

    Returns:
        Response from create_secret API call
    """
    # Convert dict to JSON string
    if isinstance(secret_value, dict):
        secret_string = json.dumps(secret_value)
    else:
        secret_string = secret_value

    try:
        response = client.create_secret(
            Name=secret_name,
            SecretString=secret_string,
            Description=description,
        )
        logger.debug(f"Created secret: {secret_name}")
        return response
    except client.exceptions.ResourceExistsException:
        # Secret already exists, update it
        response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=secret_string,
        )
        logger.debug(f"Updated existing secret: {secret_name}")
        return response
    except Exception as e:
        logger.error(f"Failed to create secret {secret_name}: {e}")
        raise


def get_secret(
    client: Any,
    secret_name: str,
    parse_json: bool = True,
) -> str | dict:
    """
    Get a secret from Secrets Manager.

    Args:
        client: Boto3 Secrets Manager client
        secret_name: Name/ID of the secret
        parse_json: If True, attempt to parse the secret as JSON

    Returns:
        Secret value (dict if JSON, otherwise string)
    """
    response = client.get_secret_value(SecretId=secret_name)
    secret_string = response["SecretString"]

    if parse_json:
        try:
            return json.loads(secret_string)
        except json.JSONDecodeError:
            return secret_string

    return secret_string


def delete_secret(
    client: Any,
    secret_name: str,
    force_delete: bool = True,
) -> None:
    """
    Delete a secret from Secrets Manager.

    Args:
        client: Boto3 Secrets Manager client
        secret_name: Name/ID of the secret
        force_delete: If True, delete immediately without recovery window
    """
    try:
        if force_delete:
            client.delete_secret(
                SecretId=secret_name,
                ForceDeleteWithoutRecovery=True,
            )
        else:
            client.delete_secret(SecretId=secret_name)
        logger.debug(f"Deleted secret: {secret_name}")
    except client.exceptions.ResourceNotFoundException:
        logger.debug(f"Secret {secret_name} does not exist")
    except Exception as e:
        logger.error(f"Failed to delete secret {secret_name}: {e}")


def list_secrets(client: Any, name_prefix: str | None = None) -> list[dict[str, Any]]:
    """
    List secrets in Secrets Manager.

    Args:
        client: Boto3 Secrets Manager client
        name_prefix: Optional prefix to filter secrets

    Returns:
        List of secret metadata dictionaries
    """
    secrets = []
    paginator = client.get_paginator("list_secrets")

    for page in paginator.paginate():
        for secret in page.get("SecretList", []):
            if name_prefix is None or secret["Name"].startswith(name_prefix):
                secrets.append(secret)

    return secrets


def create_etl_ods_secrets(
    client: Any,
    project_name: str = "ftrs",
    environment: str = "test",
    ods_api_key: str = "test-ods-api-key",
    jwt_private_key: str | None = None,
    jwt_key_id: str = "test-key-id",
    jwt_api_key: str = "test-jwt-api-key",
) -> dict[str, str]:
    """
    Create all secrets needed for ETL-ODS integration testing.

    Args:
        client: Boto3 Secrets Manager client
        project_name: Project name for prefix (default: ftrs)
        environment: Environment name (default: test)
        ods_api_key: API key for ODS Terminology API
        jwt_private_key: Private key for JWT signing (generates test key if None)
        jwt_key_id: Key ID for JWT
        jwt_api_key: API key for APIM

    Returns:
        Dict mapping secret type to secret name
    """
    resource_prefix = f"{project_name}/{environment}"

    # Default test private key placeholder (NOT for production use!)
    # Using a simple placeholder to avoid gitleaks false positives
    if jwt_private_key is None:
        jwt_private_key = "test-private-key-placeholder-for-integration-tests"

    secrets_created = {}

    # ODS Terminology API key
    ods_secret_name = f"/{resource_prefix}/ods-terminology-api-key"
    create_secret(
        client,
        ods_secret_name,
        {"api_key": ods_api_key},
        "ODS Terminology API key for testing",
    )
    secrets_created["ods_api_key"] = ods_secret_name

    # JWT credentials for APIM
    jwt_secret_name = f"/{resource_prefix}/apim-jwt-credentials"
    create_secret(
        client,
        jwt_secret_name,
        {
            "private_key": jwt_private_key,
            "key_id": jwt_key_id,
            "api_key": jwt_api_key,
        },
        "JWT credentials for APIM authentication",
    )
    secrets_created["jwt_credentials"] = jwt_secret_name

    logger.debug(f"Created ETL-ODS secrets with prefix: {resource_prefix}")
    return secrets_created


def cleanup_etl_ods_secrets(
    client: Any,
    project_name: str = "ftrs",
    environment: str = "test",
) -> None:
    """
    Delete all ETL-ODS secrets.

    Args:
        client: Boto3 Secrets Manager client
        project_name: Project name for prefix
        environment: Environment name
    """
    resource_prefix = f"/{project_name}/{environment}/"
    secrets = list_secrets(client, name_prefix=resource_prefix)

    for secret in secrets:
        delete_secret(client, secret["Name"])


@pytest.fixture(scope="function")
def etl_ods_secrets(
    secrets_client: Any,
) -> Generator[dict[str, str], None, None]:
    """
    Create ETL-ODS secrets for a single test.

    Args:
        secrets_client: Boto3 Secrets Manager client fixture

    Yields:
        Dict mapping secret type to secret name
    """
    secrets = create_etl_ods_secrets(secrets_client)

    yield secrets

    cleanup_etl_ods_secrets(secrets_client)


@pytest.fixture(scope="session")
def etl_ods_secrets_session(
    secrets_client: Any,
) -> Generator[dict[str, str], None, None]:
    """
    Create session-scoped ETL-ODS secrets.

    Args:
        secrets_client: Boto3 Secrets Manager client fixture

    Yields:
        Dict mapping secret type to secret name
    """
    secrets = create_etl_ods_secrets(secrets_client)

    yield secrets

    cleanup_etl_ods_secrets(secrets_client)
