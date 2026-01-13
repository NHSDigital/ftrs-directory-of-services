import json
import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from common.secrets import get_ods_terminology_api_key, get_resource_prefix


def test_get_resource_prefix() -> None:
    """Test get_resource_prefix returns correct prefix."""
    with patch.dict(
        os.environ,
        {"PROJECT_NAME": "ftrs-dos", "ENVIRONMENT": "dev"},
    ):
        result = get_resource_prefix()
        assert result == "ftrs-dos/dev"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local", "LOCAL_ODS_TERMINOLOGY_API_KEY": "local-ods-key"},
)
def test_get_ods_terminology_api_key_local_environment() -> None:
    """Test get_ods_terminology_api_key returns local key in local environment."""
    result = get_ods_terminology_api_key()
    assert result == "local-ods-key"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local", "LOCAL_API_KEY": "fallback-key"},
)
def test_get_ods_terminology_api_key_local_fallback() -> None:
    """Test get_ods_terminology_api_key falls back to LOCAL_API_KEY."""
    result = get_ods_terminology_api_key()
    assert result == "fallback-key"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local"},
    clear=True,
)
def test_get_ods_terminology_api_key_local_no_keys() -> None:
    """Test get_ods_terminology_api_key returns empty string when no local keys set."""
    with patch.dict(os.environ, {"ENVIRONMENT": "local"}, clear=True):
        result = get_ods_terminology_api_key()
        assert result == ""


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_ods_terminology_api_key_from_secrets_manager(
    mock_boto_client: MagicMock,
) -> None:
    """Test get_ods_terminology_api_key retrieves key from Secrets Manager."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "ods-terminology-key"}'
    }

    result = get_ods_terminology_api_key()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/ftrs-dos/dev/ods-terminology-api-key"
    )
    assert result == "ods-terminology-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_ods_terminology_api_key_client_error_logs(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_ods_terminology_api_key logs and raises ClientError when secret not found."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "ResourceNotFoundException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(ClientError):
            get_ods_terminology_api_key()
        assert "Error with secret: /ftrs-dos/dev/ods-terminology-api-key" in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_ods_terminology_api_key_client_error_non_resource_not_found(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_ods_terminology_api_key raises ClientError without logging for non-ResourceNotFoundException."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "AccessDeniedException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(ClientError):
            get_ods_terminology_api_key()
        assert "Error with secret:" not in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "ftrs-dos",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_ods_terminology_api_key_json_decode_error(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_ods_terminology_api_key logs and raises JSONDecodeError."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "not-a-json-string"
    }

    with caplog.at_level("WARNING"):
        with pytest.raises(json.JSONDecodeError):
            get_ods_terminology_api_key()
        assert "Error decoding json with issue:" in caplog.text
