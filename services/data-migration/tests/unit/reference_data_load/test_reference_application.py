from pytest_mock import MockerFixture

from reference_data_load.application import ReferenceDataLoadApplication
from reference_data_load.config import DatabaseConfig, ReferenceDataLoadConfig


def test_application_init_with_config(
    mocker: MockerFixture, mock_reference_data_config: ReferenceDataLoadConfig
) -> None:
    """Test that application can be initialized with a config object."""
    mock_create_engine = mocker.patch("reference_data_load.application.create_engine")

    app = ReferenceDataLoadApplication(config=mock_reference_data_config)

    assert app.config == mock_reference_data_config
    assert app.logger is not None
    mock_create_engine.assert_called_once_with(
        mock_reference_data_config.db_config.connection_string, echo=False
    )


def test_application_init_without_config(mocker: MockerFixture) -> None:
    """Test that the application can be initialized without passing a config (uses defaults from env)."""
    # Create a mock db_config first

    # Create the config instance mock with the db_config
    mock_config_instance = ReferenceDataLoadConfig(
        db_config=DatabaseConfig.from_uri("postgresql://user:pass@test:5432/testdb")
    )

    mock_config_class = mocker.patch(
        "reference_data_load.application.ReferenceDataLoadConfig",
        return_value=mock_config_instance,
    )
    mock_create_engine = mocker.patch(
        "reference_data_load.application.create_engine", return_value=mocker.Mock()
    )

    app = ReferenceDataLoadApplication()

    assert app.config == mock_config_instance
    assert app.logger is not None
    mock_config_class.assert_called_once()
    mock_create_engine.assert_called_once_with(
        "postgresql://user:pass@test:5432/testdb", echo=False
    )
