from ftrs_common.feature_flags import FeatureFlag, FeatureFlagsClient
from pytest_mock import MockerFixture

from common.events import ReferenceDataLoadEvent
from reference_data_load.application import ReferenceDataLoadApplication
from reference_data_load.config import ReferenceDataLoadConfig


def test_application_init_with_config(
    mocker: MockerFixture, mock_reference_data_config: ReferenceDataLoadConfig
) -> None:
    """Test that application can be initialized with a config object."""
    mock_create_engine = mocker.patch(
        "reference_data_load.application.create_engine", return_value=mocker.Mock()
    )

    app = ReferenceDataLoadApplication(config=mock_reference_data_config)

    assert app.config == mock_reference_data_config
    assert app.logger is not None
    mock_create_engine.assert_called_once_with(
        mock_reference_data_config.db_config.connection_string, echo=False
    )


def test_application_init_without_config(mocker: MockerFixture) -> None:
    """Test that the application can be initialized without passing a config (uses defaults from env)."""
    # Create a mock db_config first
    mock_db_config = mocker.Mock()
    mock_db_config.connection_string = "postgresql://test"

    # Create the config instance mock with the db_config
    mock_config_instance = mocker.Mock(spec=ReferenceDataLoadConfig)
    mock_config_instance.db_config = mock_db_config

    mock_config_class = mocker.patch(
        "reference_data_load.application.ReferenceDataLoadConfig",
        return_value=mock_config_instance,
    )
    mock_create_engine = mocker.patch(
        "reference_data_load.application.create_engine", return_value=mocker.Mock()
    )
    mocker.patch(
        "reference_data_load.application.FeatureFlagsClient",
        return_value=mocker.Mock(spec=FeatureFlagsClient),
    )

    app = ReferenceDataLoadApplication()

    assert app.config == mock_config_instance
    assert app.logger is not None
    mock_config_class.assert_called_once()
    mock_create_engine.assert_called_once_with("postgresql://test", echo=False)


def test_handle_triagecode_skips_when_feature_flag_disabled(
    mocker: MockerFixture,
    mock_reference_data_config: ReferenceDataLoadConfig,
) -> None:
    """Test that triage code loading is skipped when feature flag is disabled."""
    mocker.patch(
        "reference_data_load.application.create_engine", return_value=mocker.Mock()
    )
    mock_feature_flags_client = mocker.Mock(spec=FeatureFlagsClient)
    mock_feature_flags_client.is_enabled.return_value = False

    mock_load_triage_codes = mocker.patch.object(
        ReferenceDataLoadApplication, "_load_triage_codes"
    )

    app = ReferenceDataLoadApplication(
        config=mock_reference_data_config,
        feature_flags_client=mock_feature_flags_client,
    )
    event = ReferenceDataLoadEvent(type="triagecode")

    result = app.handle(event)

    assert result is None
    mock_feature_flags_client.is_enabled.assert_called_once_with(
        FeatureFlag.DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED
    )
    mock_load_triage_codes.assert_not_called()


def test_handle_triagecode_processes_when_feature_flag_enabled(
    mocker: MockerFixture,
    mock_reference_data_config: ReferenceDataLoadConfig,
) -> None:
    """Test that triage code loading is processed when feature flag is enabled."""
    mocker.patch(
        "reference_data_load.application.create_engine", return_value=mocker.Mock()
    )
    mock_feature_flags_client = mocker.Mock(spec=FeatureFlagsClient)
    mock_feature_flags_client.is_enabled.return_value = True

    mock_load_triage_codes = mocker.patch.object(
        ReferenceDataLoadApplication, "_load_triage_codes"
    )

    app = ReferenceDataLoadApplication(
        config=mock_reference_data_config,
        feature_flags_client=mock_feature_flags_client,
    )
    event = ReferenceDataLoadEvent(type="triagecode")

    app.handle(event)

    mock_feature_flags_client.is_enabled.assert_called_once_with(
        FeatureFlag.DATA_MIGRATION_SEARCH_TRIAGE_CODE_ENABLED
    )
    mock_load_triage_codes.assert_called_once()
