"""BDD step definitions for feature flags integration tests with real Lambda handlers."""

import sys
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_bdd import given, parsers, scenarios, then, when

# Import common step definitions for Background steps
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403

# Add data-migration service to path to import Lambda handlers
DATA_MIGRATION_PATH = Path(__file__).parents[5] / "services" / "data-migration" / "src"
sys.path.insert(0, str(DATA_MIGRATION_PATH))

scenarios("../features/data_migration_features/feature_flags_integration.feature")


@pytest.fixture
def lambda_context() -> LambdaContext:
    """Create a mock Lambda context for testing."""
    context = MagicMock(spec=LambdaContext)
    context.function_name = "test-function"
    context.function_version = "1"
    # gitleaks:allow
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:test"
    context.memory_limit_in_mb = 128
    context.aws_request_id = str(uuid4())
    context.log_group_name = "/aws/lambda/test-function"
    context.log_stream_name = "2026/02/04/[$LATEST]test"
    context.get_remaining_time_in_millis = lambda: 300000
    return context


@pytest.fixture
def reset_feature_flags_client() -> None:
    """Reset FeatureFlagsClient singleton before test (use explicitly when needed)."""
    from ftrs_common.feature_flags.feature_flags_client import (  # noqa: PLC0415
        FeatureFlagsClient,
    )

    FeatureFlagsClient._instance = None
    FeatureFlagsClient._feature_flags = None


@pytest.fixture
def integration_context() -> Dict[str, Any]:
    """Context for storing integration test state."""
    return {
        "appconfig_mock": None,
        "lambda_exception": None,
        "logs": "",
        "appconfig_call_count": 0,
    }


@pytest.fixture
def mock_dependencies(monkeypatch: pytest.MonkeyPatch) -> Dict[str, Any]:
    """Mock external AWS dependencies that are not part of feature flags integration."""
    from common.config import DatabaseConfig  # noqa: PLC0415
    from pydantic import SecretStr  # noqa: PLC0415

    mocks = {}

    # Create real DatabaseConfig object with test values
    mock_db_config = DatabaseConfig(
        host="localhost",
        port=5432,
        username="test",
        password=SecretStr("test"),
        dbname="test",
    )

    # Mock the from_secretsmanager classmethod to return our test config
    with patch.object(
        DatabaseConfig, "from_secretsmanager", return_value=mock_db_config
    ):
        mocks["db_config"] = mock_db_config

    # Mock database engine to avoid real database connections
    mock_engine = MagicMock()
    mocks["engine"] = mock_engine

    # Mock SQS client to avoid real SQS calls
    mock_sqs = MagicMock()
    mocks["sqs"] = mock_sqs

    # Set required environment variable for SQS
    monkeypatch.setenv("SQS_QUEUE_URL", "https://sqs.test.amazonaws.com/test-queue")

    return mocks


@given(parsers.parse('AppConfig returns "{flag_name}" as enabled'))
def given_appconfig_returns_flag_enabled(
    integration_context: Dict[str, Any],
    flag_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mock AppConfig to return specific flag as enabled."""
    # Set required environment variables for AppConfig
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")

    # Mock AppConfigStore to return flag as enabled
    # Flag name must be lowercase as per FeatureFlag enum values
    mock_store = MagicMock()
    original_get_config = MagicMock(return_value={flag_name.lower(): {"enabled": True}})

    # Setup tracking wrapper
    def track_calls(*args: Any, **kwargs: Any) -> Any:
        integration_context["appconfig_call_count"] += 1
        return original_get_config(*args, **kwargs)

    mock_store.get_configuration = track_calls

    integration_context["appconfig_mock"] = mock_store
    integration_context["expected_flag_name"] = flag_name


@given(parsers.parse('AppConfig returns "{flag_name}" as disabled'))
def given_appconfig_returns_flag_disabled(
    integration_context: Dict[str, Any],
    flag_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mock AppConfig to return specific flag as disabled."""
    # Set required environment variables for AppConfig
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")

    # Mock AppConfigStore to return flag as disabled
    # Flag name must be lowercase as per FeatureFlag enum values
    mock_store = MagicMock()
    original_get_config = MagicMock(
        return_value={flag_name.lower(): {"enabled": False}}
    )

    # Setup tracking wrapper
    def track_calls(*args: Any, **kwargs: Any) -> Any:
        integration_context["appconfig_call_count"] += 1
        return original_get_config(*args, **kwargs)

    mock_store.get_configuration = track_calls

    integration_context["appconfig_mock"] = mock_store
    integration_context["expected_flag_name"] = flag_name


@when("the queue populator Lambda handler is invoked with an empty event")
def when_queue_populator_invoked(
    integration_context: Dict[str, Any],
    lambda_context: LambdaContext,
    mock_dependencies: Dict[str, Any],
    capsys: pytest.CaptureFixture,
    reset_feature_flags_client: None,
) -> None:
    """Invoke the real queue_populator Lambda handler with mocked AppConfig and dependencies."""
    from common.config import DatabaseConfig  # noqa: PLC0415

    # Patch AppConfigStore and other dependencies
    with (
        patch(
            "ftrs_common.feature_flags.feature_flags_client.AppConfigStore",
            return_value=integration_context["appconfig_mock"],
        ),
        patch.object(
            DatabaseConfig,
            "from_secretsmanager",
            return_value=mock_dependencies["db_config"],
        ),
        patch(
            "queue_populator.lambda_handler.create_engine",
            return_value=mock_dependencies["engine"],
        ),
        patch("queue_populator.lambda_handler.Session"),
        patch("queue_populator.lambda_handler.SQS_CLIENT", mock_dependencies["sqs"]),
    ):
        # Import Lambda handler AFTER patching to ensure patches are applied
        from queue_populator.lambda_handler import lambda_handler  # noqa: PLC0415

        try:
            event = {"table_name": "services", "full_sync": False}
            lambda_handler(event, lambda_context)
            integration_context["lambda_exception"] = None
        except Exception as e:
            integration_context["lambda_exception"] = e

    # Capture stdout (where Lambda Powertools Logger outputs)
    captured = capsys.readouterr()
    integration_context["logs"] = captured.out + captured.err


@when("the queue populator Lambda handler is invoked again within 45 seconds")
def when_queue_populator_invoked_again(
    integration_context: Dict[str, Any],
    lambda_context: LambdaContext,
    mock_dependencies: Dict[str, Any],
    capsys: pytest.CaptureFixture,
) -> None:
    """Invoke the Lambda handler again (reuses same mocks as first invocation)."""
    # Reuse the same invocation logic as the first call
    # This simulates multiple Lambda invocations with consistent configuration
    when_queue_populator_invoked(
        integration_context, lambda_context, mock_dependencies, capsys, None
    )


@then("the Lambda handler should execute successfully")
def then_lambda_executes_successfully(integration_context: Dict[str, Any]) -> None:
    """Verify Lambda handler executed without exceptions."""
    if integration_context["lambda_exception"]:
        raise integration_context["lambda_exception"]


@then(parsers.parse('the Lambda logs should contain "{expected_message}"'))
def then_logs_contain_message(
    integration_context: Dict[str, Any],
    expected_message: str,
) -> None:
    """Verify Lambda logs contain expected message."""
    log_output = integration_context.get("logs", "")
    assert expected_message in log_output, (
        f"Expected log message not found.\n"
        f"Expected: '{expected_message}'\n"
        f"Logs:\n{log_output[:500]}"  # Show first 500 chars for readability
    )
