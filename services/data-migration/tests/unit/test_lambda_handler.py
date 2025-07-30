from aws_lambda_powertools.utilities.data_classes import SQSEvent
from pytest_mock import MockerFixture

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.lambda_handler import lambda_handler
from pipeline.utils.config import DataMigrationConfig


def test_lambda_handler(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)
    app.handle_dms_event = mocker.MagicMock()

    mocker.patch("pipeline.lambda_handler.DataMigrationApplication", return_value=app)

    event = SQSEvent(
        data={
            "Records": [
                {
                    "body": '{"type": "dms_event", "record_id": 1, "table_name": "test_table", "method": "insert"}'
                },
                {
                    "body": '{"type": "dms_event", "record_id": 2, "table_name": "test_table", "method": "update"}'
                },
            ]
        }
    )

    context = {}

    lambda_handler(event, context)

    app.handle_dms_event.assert_has_calls(
        [
            mocker.call(
                DMSEvent(
                    type="dms_event",
                    record_id=1,
                    table_name="test_table",
                    method="insert",
                )
            ),
            mocker.call(
                DMSEvent(
                    type="dms_event",
                    record_id=2,
                    table_name="test_table",
                    method="update",
                )
            ),
        ]
    )


def test_lambda_handler_no_app(mocker: MockerFixture) -> None:
    """
    Test that the lambda_handler initializes the DataMigrationApplication if it is None.
    """
    mock_app = mocker.patch("pipeline.lambda_handler.DataMigrationApplication")
    mocker.patch("pipeline.lambda_handler.APP", None)
    mock_app.return_value.handle_sqs_event = mocker.Mock()

    event = {
        "Records": [
            {
                "body": '{"type": "dms_event", "record_id": 12345, "table_name": "services", "method": "insert"}'
            }
        ]
    }

    context = {}

    lambda_handler(event, context)

    mock_app.assert_called_once()
    mock_app.return_value.handle_sqs_event.assert_called_once_with(SQSEvent(data=event))


def test_lambda_handler_existing_app(mocker: MockerFixture) -> None:
    """
    Test that the lambda_handler uses the existing DataMigrationApplication if it is already initialized.
    """
    mock_app = mocker.patch("pipeline.lambda_handler.DataMigrationApplication")
    mocker.patch("pipeline.lambda_handler.APP", mock_app.return_value)
    mock_app.return_value.handle_sqs_event = mocker.Mock()

    event = {
        "Records": [
            {
                "body": '{"type": "dms_event", "record_id": 12345, "table_name": "services", "method": "insert"}'
            }
        ]
    }

    context = {}

    lambda_handler(event, context)

    mock_app.assert_not_called()  # Should not create a new instance
    mock_app.return_value.handle_sqs_event.assert_called_once_with(SQSEvent(data=event))
