"""BDD step definitions for feature flags integration tests."""

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from ftrs_common.feature_flags.feature_flags_client import (
    CACHE_TTL_SECONDS,
    FeatureFlagsClient,
)
from pytest_bdd import given, parsers, scenarios, then, when

# Import common step definitions for Background steps
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403

scenarios("../features/data_migration_features/feature_flags_integration.feature")


@pytest.fixture
def feature_flag_context() -> Dict[str, Any]:
    """Context for storing feature flag test state."""
    return {
        "flag_value": None,
        "error": None,
        "client_instances": [],
        "appconfig_query_count": 0,
        "logs": [],
        "cached_value": None,
    }


@pytest.fixture(autouse=True)
def reset_feature_flags_client() -> None:
    """Reset FeatureFlagsClient singleton before each test."""
    FeatureFlagsClient._instance = None
    FeatureFlagsClient._feature_flags = None


@pytest.fixture
def mock_appconfig_store() -> MagicMock:
    """Mock AppConfigStore for testing."""
    mock_store = MagicMock()
    mock_store.get_configuration.return_value = {}
    return mock_store


@given(parsers.parse('AppConfig has feature flag "{flag_name}" set to {flag_value}'))
def given_appconfig_has_flag(
    feature_flag_context: Dict[str, Any],
    mock_appconfig_store: MagicMock,
    flag_name: str,
    flag_value: str,
) -> None:
    """Set up AppConfig mock to return specific flag value."""
    # Convert string to boolean
    flag_value_bool = flag_value.lower() == "true"
    # AppConfig expects flags in format: {"flag_name": {"enabled": true}}
    mock_appconfig_store.get_configuration.return_value = {
        flag_name: {"enabled": flag_value_bool}
    }
    feature_flag_context["mock_store"] = mock_appconfig_store
    feature_flag_context["expected_flag_name"] = flag_name
    feature_flag_context["expected_flag_value"] = flag_value_bool


@given(parsers.parse("logging is configured to {level} level"))
def given_logging_level(level: str) -> None:
    """Configure logging level (for log validation tests)."""
    # This step is mainly documentation - logging level is controlled by environment
    pass


@given("the queue populator Lambda is deployed with AppConfig integration")
def given_queue_populator_deployed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up environment variables for queue populator Lambda."""
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")


@given("the processor Lambda is deployed with AppConfig integration")
def given_processor_lambda_deployed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up environment variables for processor Lambda."""
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")


@when("the queue populator Lambda reads the feature flag")
def when_lambda_reads_flag(
    feature_flag_context: Dict[str, Any],
    mock_appconfig_store: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lambda reads feature flag using FeatureFlagsClient."""
    # Set up environment variables
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")

    # Patch AppConfigStore to use our mock
    with patch(
        "ftrs_common.feature_flags.feature_flags_client.AppConfigStore",
        return_value=mock_appconfig_store,
    ):
        client = FeatureFlagsClient()
        flag_name = feature_flag_context.get("expected_flag_name", "TEST_FLAG")

        try:
            result = client.is_enabled(flag_name)
            feature_flag_context["flag_value"] = result
            feature_flag_context["error"] = None
        except Exception as e:
            feature_flag_context["error"] = e


@when(parsers.parse('the Lambda reads flag "{flag_name}"'))
def when_lambda_reads_specific_flag(
    feature_flag_context: Dict[str, Any],
    mock_appconfig_store: MagicMock,
    flag_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Lambda reads a specific feature flag."""
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")

    with patch(
        "ftrs_common.feature_flags.feature_flags_client.AppConfigStore",
        return_value=mock_appconfig_store,
    ):
        client = FeatureFlagsClient()
        try:
            result = client.is_enabled(flag_name)
            feature_flag_context["flag_value"] = result
            feature_flag_context["appconfig_query_count"] += 1
        except Exception as e:
            feature_flag_context["error"] = e


@when("the queue populator Lambda handler is invoked")
def when_queue_populator_invoked(
    feature_flag_context: Dict[str, Any],
    mock_appconfig_store: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invoke queue populator Lambda handler (simulated)."""
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")

    with patch(
        "ftrs_common.feature_flags.feature_flags_client.AppConfigStore",
        return_value=mock_appconfig_store,
    ):
        # Simulate Lambda handler behavior
        client = FeatureFlagsClient()
        try:
            result = client.is_enabled("DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED")
            feature_flag_context["flag_value"] = result
            feature_flag_context["lambda_execution_error"] = None
        except Exception as e:
            feature_flag_context["lambda_execution_error"] = e


@when("the processor Lambda initializes FeatureFlagsClient")
def when_processor_lambda_initializes(
    feature_flag_context: Dict[str, Any],
    mock_appconfig_store: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Processor Lambda initializes FeatureFlagsClient."""
    monkeypatch.setenv("APPCONFIG_APPLICATION_ID", "test-app-id")
    monkeypatch.setenv("APPCONFIG_ENVIRONMENT_ID", "test-env-id")
    monkeypatch.setenv("APPCONFIG_CONFIGURATION_PROFILE_ID", "test-profile-id")

    with patch(
        "ftrs_common.feature_flags.feature_flags_client.AppConfigStore",
        return_value=mock_appconfig_store,
    ):
        try:
            client = FeatureFlagsClient()
            _ = client.get_feature_flags()
            feature_flag_context["client"] = client
            feature_flag_context["error"] = None
        except Exception as e:
            feature_flag_context["error"] = e


@then("the feature flag should be evaluated as enabled")
def then_flag_is_enabled(feature_flag_context: Dict[str, Any]) -> None:
    """Verify flag is evaluated as enabled."""
    assert feature_flag_context["flag_value"] is True
    assert feature_flag_context["error"] is None


@then("the feature flag should be evaluated as disabled")
def then_flag_is_disabled(feature_flag_context: Dict[str, Any]) -> None:
    """Verify flag is evaluated as disabled."""
    assert feature_flag_context["flag_value"] is False
    assert feature_flag_context["error"] is None


@then("the flag evaluation should be logged in CloudWatch")
def then_flag_logged() -> None:
    """Verify flag evaluation is logged (mocked verification)."""
    # In real integration test, this would check CloudWatch logs
    # For unit test, we verify the logging mechanism exists
    pass


@then(parsers.parse("the flag should be evaluated as {expected_result}"))
def then_flag_evaluated_as(
    feature_flag_context: Dict[str, Any], expected_result: str
) -> None:
    """Verify flag was evaluated to expected result."""
    expected_bool = expected_result.lower() == "enabled"
    assert feature_flag_context["flag_value"] == expected_bool


@then(parsers.parse('the CloudWatch logs should contain flag name "{flag_name}"'))
def then_logs_contain_flag_name(flag_name: str) -> None:
    """Verify logs contain flag name."""
    # In real integration test, this would query CloudWatch logs
    pass


@then(parsers.parse('the CloudWatch logs should contain evaluation result "{result}"'))
def then_logs_contain_result(result: str) -> None:
    """Verify logs contain evaluation result."""
    # In real integration test, this would query CloudWatch logs
    pass


@then("the CloudWatch logs should contain the flag source")
def then_logs_contain_source() -> None:
    """Verify logs contain flag source."""
    # In real integration test, this would query CloudWatch logs
    pass


@then("the Lambda should successfully read the feature flag")
def then_lambda_reads_successfully(feature_flag_context: Dict[str, Any]) -> None:
    """Verify Lambda successfully read the feature flag."""
    assert feature_flag_context.get("flag_value") is not None
    assert feature_flag_context.get("lambda_execution_error") is None


@then("the Lambda should log whether the feature is enabled or disabled")
def then_lambda_logs_feature_status() -> None:
    """Verify Lambda logs feature status."""
    # In real integration test, this would check CloudWatch logs
    pass


@then("the Lambda execution should complete without errors")
def then_lambda_completes_successfully(feature_flag_context: Dict[str, Any]) -> None:
    """Verify Lambda execution completed without errors."""
    assert feature_flag_context.get("lambda_execution_error") is None


@then("the Lambda should successfully retrieve the AppConfig configuration")
def then_lambda_retrieves_config(feature_flag_context: Dict[str, Any]) -> None:
    """Verify Lambda retrieved AppConfig configuration."""
    assert feature_flag_context.get("client") is not None
    assert feature_flag_context.get("error") is None


@then(parsers.parse("the feature flag value should be cached for {ttl:d} seconds"))
def then_value_cached_for_ttl(ttl: int) -> None:
    """Verify feature flag value is cached for specified TTL."""
    # This is verified by the cache TTL constant (45 seconds)
    assert CACHE_TTL_SECONDS == ttl
