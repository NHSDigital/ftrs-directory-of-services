from typing import Generator
from unittest.mock import MagicMock

import pytest
from aws_lambda_powertools.utilities.feature_flags.exceptions import (
    ConfigurationStoreError,
)
from ftrs_common.feature_flags.feature_flags_client import (
    CACHE_TTL_SECONDS,
    FeatureFlagError,
    FeatureFlagsClient,
    LocalFlagsClient,
    _get_client,
    is_enabled,
)
from ftrs_common.logbase import FeatureFlagLogBase
from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def reset_singleton() -> Generator[None, None, None]:
    """Reset the singleton instance before each test."""
    FeatureFlagsClient._instance = None
    FeatureFlagsClient._feature_flags = None
    _get_client.cache_clear()
    yield
    FeatureFlagsClient._instance = None
    FeatureFlagsClient._feature_flags = None
    _get_client.cache_clear()


@pytest.fixture
def mock_settings(mocker: MockerFixture) -> MagicMock:
    """Mock Settings with valid AppConfig configuration."""
    mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
    mock.return_value.appconfig_application_id = "test-app-id"
    mock.return_value.appconfig_environment_id = "test-env-id"
    mock.return_value.appconfig_configuration_profile_id = "test-profile-id"
    return mock


@pytest.fixture
def mock_appconfig_store(mocker: MockerFixture) -> MagicMock:
    """Mock AppConfigStore."""
    return mocker.patch("ftrs_common.feature_flags.feature_flags_client.AppConfigStore")


@pytest.fixture
def mock_feature_flags_class(mocker: MockerFixture) -> MagicMock:
    """Mock FeatureFlags class."""
    return mocker.patch("ftrs_common.feature_flags.feature_flags_client.FeatureFlags")


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mock the logger."""
    return mocker.patch("ftrs_common.feature_flags.feature_flags_client.logger")


class TestLocalFlagsClient:
    def test_init_sets_default_flags(self, mocker: MockerFixture) -> None:
        mocker.patch.dict("os.environ", {}, clear=False)
        client = LocalFlagsClient()
        assert "data_migration_search_triage_code_enabled" in client.flags
        assert client.flags["data_migration_search_triage_code_enabled"] is True

    def test_is_enabled_returns_false_when_env_var_is_false(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict(
            "os.environ", {"DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED": "FALSE"}
        )
        client = LocalFlagsClient()
        assert client.is_enabled("data_migration_search_triage_code_enabled") is False

    def test_is_enabled_returns_default_for_missing_flag(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict("os.environ", {}, clear=False)
        client = LocalFlagsClient()
        assert client.is_enabled("nonexistent_flag", default=True) is True
        assert client.is_enabled("nonexistent_flag", default=False) is False


class TestFeatureFlagError:
    def test_error_contains_flag_name_and_message(self) -> None:
        error = FeatureFlagError(
            flag_name="test_flag",
            message="Test error message",
        )
        assert error.flag_name == "test_flag"
        assert "test_flag" in str(error)
        assert "Test error message" in str(error)

    def test_error_includes_original_exception(self) -> None:
        original = ValueError("Original error")
        error = FeatureFlagError(
            flag_name="test_flag",
            message="Wrapper message",
            original_exception=original,
        )
        assert error.original_exception is original

    def test_error_formats_message_correctly(self) -> None:
        error = FeatureFlagError(
            flag_name="my_feature",
            message="Something went wrong",
        )
        assert (
            str(error)
            == "Feature flag 'my_feature' evaluation failed: Something went wrong"
        )


class TestFeatureFlagsClient:
    def test_singleton_returns_same_instance(self, mock_settings: MagicMock) -> None:
        client1 = FeatureFlagsClient()
        client2 = FeatureFlagsClient()
        assert client1 is client2

    def test_init_only_runs_once(self, mock_settings: MagicMock) -> None:
        client = FeatureFlagsClient()
        assert client._initialized is True
        mock_settings.assert_called_once()

        # Create another instance - Settings should not be called again
        FeatureFlagsClient()
        mock_settings.assert_called_once()

    def test_get_appconfig_store_raises_error_when_application_id_missing(
        self, mocker: MockerFixture, mock_logger: MagicMock
    ) -> None:
        mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
        mock.return_value.appconfig_application_id = None
        mock.return_value.appconfig_environment_id = "test-env-id"
        mock.return_value.appconfig_configuration_profile_id = "test-profile-id"

        with pytest.raises(FeatureFlagError) as exc_info:
            FeatureFlagsClient()

        assert "APPCONFIG_APPLICATION_ID" in str(exc_info.value)

    def test_get_appconfig_store_raises_error_when_environment_id_missing(
        self, mocker: MockerFixture, mock_logger: MagicMock
    ) -> None:
        mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
        mock.return_value.appconfig_application_id = "test-app-id"
        mock.return_value.appconfig_environment_id = None
        mock.return_value.appconfig_configuration_profile_id = "test-profile-id"

        with pytest.raises(FeatureFlagError) as exc_info:
            FeatureFlagsClient()

        assert "APPCONFIG_ENVIRONMENT_ID" in str(exc_info.value)

    def test_get_appconfig_store_raises_error_when_configuration_profile_id_missing(
        self, mocker: MockerFixture, mock_logger: MagicMock
    ) -> None:
        mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
        mock.return_value.appconfig_application_id = "test-app-id"
        mock.return_value.appconfig_environment_id = "test-env-id"
        mock.return_value.appconfig_configuration_profile_id = None

        with pytest.raises(FeatureFlagError) as exc_info:
            FeatureFlagsClient()

        assert "APPCONFIG_CONFIGURATION_PROFILE_ID" in str(exc_info.value)

    def test_get_appconfig_store_creates_store_with_correct_config(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        FeatureFlagsClient()

        # AppConfigStore is already called once in __init__
        mock_appconfig_store.assert_called_with(
            application="test-app-id",
            environment="test-env-id",
            name="test-profile-id",
            max_age=CACHE_TTL_SECONDS,
        )

    def test_init_creates_feature_flags_instance(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        FeatureFlagsClient()

        mock_feature_flags_class.assert_called_once()
        assert (
            FeatureFlagsClient._feature_flags is mock_feature_flags_class.return_value
        )

    def test_init_calls_appconfig_store_once(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        FeatureFlagsClient()

        mock_appconfig_store.assert_called_once()
        mock_feature_flags_class.assert_called_once()


class TestIsEnabled:
    def test_returns_true_when_flag_is_enabled(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"my_feature": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("my_feature")

        assert result is True

    def test_returns_false_when_flag_is_disabled(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"my_feature": {"enabled": False}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("my_feature")

        assert result is False

    def test_returns_default_false_when_flag_not_found(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"other_flag": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("nonexistent_flag", default=False)

        assert result is False

    def test_returns_default_true_when_flag_not_found(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"other_flag": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("nonexistent_flag", default=True)

        assert result is True

    def test_returns_default_when_configuration_is_empty(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = None
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("any_flag", default=True)

        assert result is True

    def test_returns_default_when_configuration_is_empty_dict(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("any_flag", default=False)

        assert result is False

    def test_raises_error_on_configuration_store_error(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.side_effect = ConfigurationStoreError(
            "Store error"
        )
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()

        with pytest.raises(FeatureFlagError) as exc_info:
            client.is_enabled("my_feature")

        assert exc_info.value.flag_name == "my_feature"
        assert "Configuration store error" in str(exc_info.value)

    def test_raises_error_on_unexpected_exception(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.side_effect = RuntimeError("Unexpected error")
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()

        with pytest.raises(FeatureFlagError) as exc_info:
            client.is_enabled("my_feature")

        assert exc_info.value.flag_name == "my_feature"
        assert "Unexpected error" in str(exc_info.value)

    def test_logs_flag_evaluation(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"my_feature": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        client.is_enabled("my_feature")

        mock_logger.log.assert_called()

    def test_logs_warning_when_flag_not_found(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"other_flag": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        client.is_enabled("nonexistent_flag")

        log_calls = [call[0][0] for call in mock_logger.log.call_args_list]
        assert FeatureFlagLogBase.FF_005 in log_calls


class TestModuleFunctions:
    def test_get_client_returns_local_client_for_local_env(
        self, mocker: MockerFixture
    ) -> None:
        mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
        mock.return_value.env = "local"
        mock.return_value.workspace = None
        _get_client.cache_clear()

        client = _get_client()
        assert isinstance(client, LocalFlagsClient)

    def test_get_client_returns_feature_flags_client_for_dev_with_workspace(
        self, mocker: MockerFixture
    ) -> None:
        mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
        mock.return_value.env = "dev"
        mock.return_value.workspace = "test-workspace"
        mock.return_value.appconfig_application_id = "test-app"
        mock.return_value.appconfig_environment_id = "test-env"
        mock.return_value.appconfig_configuration_profile_id = "test-profile"
        _get_client.cache_clear()

        client = _get_client()
        assert isinstance(client, FeatureFlagsClient)

    def test_get_client_returns_feature_flags_client_for_dev_without_workspace(
        self, mocker: MockerFixture
    ) -> None:
        mock = mocker.patch("ftrs_common.feature_flags.feature_flags_client.Settings")
        mock.return_value.env = "dev"
        mock.return_value.workspace = None
        mock.return_value.appconfig_application_id = "test-app"
        mock.return_value.appconfig_environment_id = "test-env"
        mock.return_value.appconfig_configuration_profile_id = "test-profile"
        _get_client.cache_clear()

        client = _get_client()
        assert isinstance(client, FeatureFlagsClient)

    def test_get_client_returns_cached_instance(self, mock_settings: MagicMock) -> None:
        client1 = _get_client()
        client2 = _get_client()
        assert client1 is client2

    def test_is_enabled_function_checks_flag(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"test_flag": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        result = is_enabled("test_flag")
        assert result is True

    def test_is_enabled_function_uses_default_value_false(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {}
        mock_feature_flags_class.return_value.store = mock_store

        result = is_enabled("missing_flag", default=False)
        assert result is False

    def test_is_enabled_function_uses_default_value_true(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {}
        mock_feature_flags_class.return_value.store = mock_store

        result = is_enabled("missing_flag", default=True)
        assert result is True


class TestIsEnabledLogging:
    def test_logs_configuration_store_error(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.side_effect = ConfigurationStoreError(
            "Store error"
        )
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()

        with pytest.raises(FeatureFlagError):
            client.is_enabled("my_feature")

        log_calls = [call[0][0] for call in mock_logger.log.call_args_list]
        assert FeatureFlagLogBase.FF_003 in log_calls

    def test_logs_unexpected_error(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.side_effect = RuntimeError("Unexpected error")
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()

        with pytest.raises(FeatureFlagError):
            client.is_enabled("my_feature")

        log_calls = [call[0][0] for call in mock_logger.log.call_args_list]
        assert FeatureFlagLogBase.FF_004 in log_calls

    def test_logs_successful_flag_evaluation_with_ff_002(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {"my_feature": {"enabled": True}}
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        client.is_enabled("my_feature")

        log_calls = [call[0][0] for call in mock_logger.log.call_args_list]
        assert FeatureFlagLogBase.FF_002 in log_calls

    def test_logs_appconfig_store_initialization_with_ff_001(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        client = FeatureFlagsClient()
        client._get_appconfig_store()

        log_calls = [call[0][0] for call in mock_logger.log.call_args_list]
        assert FeatureFlagLogBase.FF_001 in log_calls


class TestFeatureFlagErrorOriginalException:
    def test_error_with_none_original_exception(self) -> None:
        error = FeatureFlagError(
            flag_name="test_flag",
            message="Test error message",
            original_exception=None,
        )
        assert error.original_exception is None

    def test_error_can_be_raised_and_caught(self) -> None:
        with pytest.raises(FeatureFlagError) as exc_info:
            raise FeatureFlagError(
                flag_name="test_flag",
                message="Test error message",
            )
        assert exc_info.value.flag_name == "test_flag"


class TestIsEnabledFlagConfigEdgeCases:
    def test_returns_default_when_flag_has_no_enabled_key(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {
            "my_feature": {"some_other_key": "value"}
        }
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("my_feature", default=True)

        assert result is True

    def test_returns_enabled_value_from_flag_config(
        self,
        mock_settings: MagicMock,
        mock_appconfig_store: MagicMock,
        mock_feature_flags_class: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        mock_store = MagicMock()
        mock_store.get_configuration.return_value = {
            "my_feature": {"enabled": True, "some_other_key": "value"}
        }
        mock_feature_flags_class.return_value.store = mock_store

        client = FeatureFlagsClient()
        result = client.is_enabled("my_feature", default=False)

        assert result is True
