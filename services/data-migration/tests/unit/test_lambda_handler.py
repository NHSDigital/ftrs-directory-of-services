from pytest_mock import MockerFixture

from pipeline.application import DataMigrationApplication
from pipeline.lambda_handler import lambda_handler
from pipeline.utils.config import DataMigrationConfig


def test_lambda_handler(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)
    app.handle_event = mocker.MagicMock()

    mocker.patch("pipeline.lambda_handler.DataMigrationApplication", return_value=app)

    event = {"type": "test_event"}
    context = {}

    lambda_handler(event, context)

    app.handle_event.assert_called_once_with(event)
