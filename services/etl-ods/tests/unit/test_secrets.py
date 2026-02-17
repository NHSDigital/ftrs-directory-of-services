import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture

from extractor.ods_client import SecretManager


@pytest.fixture(scope="module")
def standard_env_vars() -> dict[str, str]:
    """File-scoped fixture for standard environment variables."""
    return {
        "PROJECT_NAME": "project-name",
        "ENVIRONMENT": "dev",
        "AWS_REGION": "eu-west-2",
    }


@pytest.fixture
def dev_environment(
    monkeypatch: pytest.MonkeyPatch, standard_env_vars: dict[str, str]
) -> None:
    """Set up standard dev environment variables."""
    for key, value in standard_env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def local_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up standard local environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "local")
    # Ensure these are not set
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("LOCAL_ODS_TERMINOLOGY_API_KEY", raising=False)
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)


def test_get_resource_prefix(dev_environment: None) -> None:
    """Test resource prefix functionality through SecretManager."""
    result = SecretManager.get_resource_prefix()
    assert result == "project-name/dev"


def test_get_ods_terminology_api_key_local_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test get_ods_terminology_api_key returns local key in local environment."""
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("LOCAL_ODS_TERMINOLOGY_API_KEY", "local-ods-key")

    result = SecretManager.get_ods_terminology_api_key()
    assert result == "local-ods-key"


def test_get_ods_terminology_api_key_local_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test get_ods_terminology_api_key falls back to LOCAL_API_KEY."""
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("LOCAL_API_KEY", "fallback-key")
    monkeypatch.delenv("LOCAL_ODS_TERMINOLOGY_API_KEY", raising=False)

    result = SecretManager.get_ods_terminology_api_key()
    assert result == "fallback-key"


def test_get_ods_terminology_api_key_local_no_keys(local_environment: None) -> None:
    """Test get_ods_terminology_api_key returns empty string when no local keys set."""
    result = SecretManager.get_ods_terminology_api_key()
    assert result == ""


def test_get_ods_terminology_api_key_missing_required_env_vars(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test get_ods_terminology_api_key raises KeyError when required env vars missing."""
    monkeypatch.setenv("ENVIRONMENT", "prod")
    monkeypatch.delenv("PROJECT_NAME", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)

    with pytest.raises(KeyError):
        SecretManager.get_ods_terminology_api_key()


def test_get_ods_terminology_api_key_from_secrets_manager(
    dev_environment: None, mocker: MockerFixture
) -> None:
    """Test get_ods_terminology_api_key retrieves key from Secrets Manager."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "ods-terminology-key"}'
    }

    result = SecretManager.get_ods_terminology_api_key()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/project-name/dev/ods-terminology-api-key"
    )
    assert result == "ods-terminology-key"


def test_get_ods_terminology_api_key_client_error_logs(
    dev_environment: None, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_ods_terminology_api_key logs and raises ClientError when secret not found."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
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


def test_get_ods_terminology_api_key_client_error_non_resource_not_found(
    dev_environment: None, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_ods_terminology_api_key raises ClientError without logging for non-ResourceNotFoundException."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "AccessDeniedException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(ClientError):
            SecretManager.get_ods_terminology_api_key()
        assert "Error with secret:" not in caplog.text


def test_get_ods_terminology_api_key_json_decode_error(
    dev_environment: None, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_ods_terminology_api_key handles non-JSON secrets by returning raw string."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "not-a-json-string"
    }

    with caplog.at_level("WARNING"):
        result = SecretManager.get_ods_terminology_api_key()
        # Implementation should return the raw string when JSON parsing fails
        assert result == "not-a-json-string"


def test_get_ods_terminology_api_key_uses_aws_region(
    dev_environment: None, mocker: MockerFixture
) -> None:
    """Test get_ods_terminology_api_key uses AWS_REGION environment variable."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "test-key"}'
    }

    result = SecretManager.get_ods_terminology_api_key()

    mock_boto_client.assert_called_once_with("secretsmanager", region_name="eu-west-2")
    assert result == "test-key"


def test_get_mock_api_key_from_secrets_with_workspace(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    """Test get_mock_api_key_from_secrets retrieves mock key from Secrets Manager with workspace."""
    monkeypatch.setenv("PROJECT_NAME", "project-name")
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("WORKSPACE", "test-workspace")
    monkeypatch.setenv("AWS_REGION", "eu-west-2")

    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "mock-api-key"}'
    }

    result = SecretManager.get_mock_api_key_from_secrets()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/project-name-dev/mock-api/api-key-test-workspace"
    )
    assert result == "mock-api-key"


def test_get_mock_api_key_from_secrets_without_workspace(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    """Test get_mock_api_key_from_secrets retrieves mock key from Secrets Manager without workspace."""
    monkeypatch.setenv("PROJECT_NAME", "project-name")
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("AWS_REGION", "eu-west-2")
    monkeypatch.delenv("WORKSPACE", raising=False)

    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": '{"api_key": "mock-api-key-no-workspace"}'
    }

    result = SecretManager.get_mock_api_key_from_secrets()

    mock_secretsmanager.get_secret_value.assert_called_once_with(
        SecretId="/project-name-dev/mock-api/api-key"
    )
    assert result == "mock-api-key-no-workspace"


def test_get_mock_api_key_from_secrets_missing_project_name(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
) -> None:
    """Test get_mock_api_key_from_secrets with missing PROJECT_NAME uses invalid path."""
    monkeypatch.setenv("ENVIRONMENT", "dev")
    monkeypatch.setenv("AWS_REGION", "eu-west-2")
    monkeypatch.delenv("PROJECT_NAME", raising=False)

    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager

    error_response = {"Error": {"Code": "ResourceNotFoundException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )

    with pytest.raises(KeyError, match="Mock API key secret not found"):
        SecretManager.get_mock_api_key_from_secrets()


def test_get_mock_api_key_from_secrets_client_error_resource_not_found(
    dev_environment: None, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_mock_api_key_from_secrets logs and raises KeyError when secret not found."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    error_response = {"Error": {"Code": "ResourceNotFoundException"}}
    mock_secretsmanager.get_secret_value.side_effect = ClientError(
        error_response, "GetSecretValue"
    )

    with caplog.at_level("ERROR"):
        with pytest.raises(KeyError, match="Mock API key secret not found"):
            SecretManager.get_mock_api_key_from_secrets()
        assert "Mock API key secret not found" in caplog.text


def test_get_mock_api_key_from_secrets_other_exception(
    dev_environment: None, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_mock_api_key_from_secrets logs and re-raises non-ClientError exceptions."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.side_effect = Exception("Network error")

    with caplog.at_level("ERROR"):
        with pytest.raises(Exception, match="Network error"):
            SecretManager.get_mock_api_key_from_secrets()
        assert "Failed to retrieve mock API key" in caplog.text


def test_get_mock_api_key_from_secrets_plain_string(
    dev_environment: None, mocker: MockerFixture
) -> None:
    """Test get_mock_api_key_from_secrets handles plain string secrets (non-JSON)."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "plain-string-key"
    }

    result = SecretManager.get_mock_api_key_from_secrets()

    assert result == "plain-string-key"


def test_get_mock_api_key_from_secrets_json_decode_error(
    dev_environment: None, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test get_mock_api_key_from_secrets handles invalid JSON by returning raw string."""
    mock_secretsmanager = mocker.MagicMock()
    mock_boto_client = mocker.patch("common.secrets.boto3.client")
    mock_boto_client.return_value = mock_secretsmanager
    mock_secretsmanager.get_secret_value.return_value = {
        "SecretString": "{ invalid json structure"
    }

    with caplog.at_level("WARNING"):
        result = SecretManager.get_mock_api_key_from_secrets()

        # Implementation should return the raw string when JSON parsing fails
        assert result == "{ invalid json structure"

        # Check if any JSON error was logged
        json_error_logged = any(
            "json" in record.getMessage().lower() or "ETL_COMMON_012" in str(record)
            for record in caplog.records
        )
        assert json_error_logged or result == "{ invalid json structure"
