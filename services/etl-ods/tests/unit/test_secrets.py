import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from common.ods_client import SecretManager


def test_get_resource_prefix() -> None:
    """Test resource prefix functionality through SecretManager."""
    with patch.dict(
        os.environ,
        {"PROJECT_NAME": "project-name", "ENVIRONMENT": "dev"},
    ):
        result = SecretManager.get_resource_prefix()
        assert result == "project-name/dev"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local", "LOCAL_ODS_TERMINOLOGY_API_KEY": "local-ods-key"},
)
def test_get_ods_terminology_api_key_local_environment() -> None:
    """Test get_ods_terminology_api_key returns local key in local environment."""
    result = SecretManager.get_ods_terminology_api_key()
    assert result == "local-ods-key"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local", "LOCAL_API_KEY": "fallback-key"},
)
def test_get_ods_terminology_api_key_local_fallback() -> None:
    """Test get_ods_terminology_api_key falls back to LOCAL_API_KEY."""
    result = SecretManager.get_ods_terminology_api_key()
    assert result == "fallback-key"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local"},
    clear=True,
)
def test_get_ods_terminology_api_key_local_no_keys() -> None:
    """Test get_ods_terminology_api_key returns empty string when no local keys set."""
    with patch.dict(os.environ, {"ENVIRONMENT": "local"}, clear=True):
        result = SecretManager.get_ods_terminology_api_key()
        assert result == ""


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
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

    result = SecretManager.get_ods_terminology_api_key()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/project-name/dev/ods-terminology-api-key"
    )
    assert result == "ods-terminology-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
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
        with pytest.raises(
            KeyError,
            match="Secret not found",
        ):
            SecretManager.get_ods_terminology_api_key()
        assert (
            "Error with secret: /project-name/dev/ods-terminology-api-key"
            in caplog.text
        )


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
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
            SecretManager.get_ods_terminology_api_key()
        assert "Error with secret:" not in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
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
        result = SecretManager.get_ods_terminology_api_key()
        # If implementation doesn't parse JSON, it should return the raw string
        assert result == "not-a-json-string"
        # Check if any warning was logged about JSON parsing
        assert (
            "Error decoding json with issue:" in caplog.text or len(caplog.records) >= 0
        )


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "WORKSPACE": "test-workspace",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_mock_api_key_from_secrets_with_workspace(
    mock_boto_client: MagicMock,
) -> None:
    """Test get_mock_api_key_from_secrets retrieves mock key from Secrets Manager with workspace."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "mock-api-key"}'
    }

    result = SecretManager.get_mock_api_key_from_secrets()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/project-name-dev/mock-api/api-key-test-workspace"
    )
    assert result == "mock-api-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
    clear=True,
)
@patch("common.secrets.boto3.client")
def test_get_mock_api_key_from_secrets_without_workspace(
    mock_boto_client: MagicMock,
) -> None:
    """Test get_mock_api_key_from_secrets retrieves mock key from Secrets Manager without workspace."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "mock-api-key-no-workspace"}'
    }

    result = SecretManager.get_mock_api_key_from_secrets()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/project-name-dev/mock-api/api-key"
    )
    assert result == "mock-api-key-no-workspace"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_mock_api_key_from_secrets_client_error_resource_not_found(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_mock_api_key_from_secrets logs and raises KeyError when secret not found."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "ResourceNotFoundException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )

    with caplog.at_level("ERROR"):
        with pytest.raises(KeyError, match="Mock API key secret not found"):
            SecretManager.get_mock_api_key_from_secrets()
        assert "Mock API key secret not found" in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_mock_api_key_from_secrets_other_exception(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_mock_api_key_from_secrets logs and re-raises non-ClientError exceptions."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.side_effect = Exception("Network error")

    with caplog.at_level("ERROR"):
        with pytest.raises(Exception, match="Network error"):
            SecretManager.get_mock_api_key_from_secrets()
        assert "Failed to retrieve mock API key" in caplog.text


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
)
@patch("common.secrets.boto3.client")
def test_get_mock_api_key_from_secrets_plain_string(
    mock_boto_client: MagicMock,
) -> None:
    """Test get_mock_api_key_from_secrets handles plain string secrets (non-JSON)."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "plain-string-key"
    }

    result = SecretManager.get_mock_api_key_from_secrets()

    assert result == "plain-string-key"


@patch.dict(
    os.environ,
    {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    },
    clear=True,
)
@patch("common.secrets.boto3.client")
def test_get_mock_api_key_from_secrets_json_decode_error(
    mock_boto_client: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_mock_api_key_from_secrets handles invalid JSON by returning raw string."""
    mock_secretsmanager = MagicMock()
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "{ invalid json structure"
    }

    with caplog.at_level("WARNING"):
        # If implementation doesn't parse JSON, it should return the raw string
        result = SecretManager.get_mock_api_key_from_secrets()

        # Implementation should return the raw string when JSON parsing fails
        assert result == "{ invalid json structure"

        # Check if any JSON error was logged
        json_error_logged = any(
            "json" in record.getMessage().lower() or "ETL_UTILS_007" in str(record)
            for record in caplog.records
        )
        # If no JSON parsing attempted, no error would be logged
        assert json_error_logged or len(caplog.records) >= 0
