from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_mock import MockerFixture

from pipeline.application import DataMigrationApplication
from pipeline.lambda_handler import lambda_handler
from pipeline.utils.config import DataMigrationConfig


def test_lambda_handler(
    mocker: MockerFixture,
    mock_lambda_context: LambdaContext,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)
    app.handle_sqs_event = mocker.MagicMock(return_value={"batchItemFailures": []})

    mocker.patch("pipeline.lambda_handler.DataMigrationApplication", return_value=app)

    mock_records = [
        {
            "messageId": "1",
            "body": '{"type": "dms_event", "record_id": 1, "table_name": "test_table", "method": "insert"}',
        },
        {
            "messageId": "2",
            "body": '{"type": "dms_event", "record_id": 2, "table_name": "test_table", "method": "update"}',
        },
    ]

    event = SQSEvent(data={"Records": mock_records})

    response = lambda_handler(event, mock_lambda_context)
    assert response == {"batchItemFailures": []}

    assert app.handle_sqs_event.call_count == 1

    assert app.handle_sqs_event.call_args[0][0] == event
    assert app.handle_sqs_event.call_args[0][1] == mock_lambda_context


def test_lambda_handler_no_app(
    mocker: MockerFixture,
    mock_lambda_context: LambdaContext,
) -> None:
    """
    Test that the lambda_handler initializes the DataMigrationApplication if it is None.
    """
    mock_app = mocker.patch("pipeline.lambda_handler.DataMigrationApplication")
    mocker.patch("pipeline.lambda_handler.APP", None)
    mock_app.return_value.handle_sqs_event = mocker.Mock(
        return_value={"batchItemFailures": []}
    )

    event = {
        "Records": [
            {
                "body": '{"type": "dms_event", "record_id": 12345, "table_name": "services", "method": "insert"}'
            }
        ]
    }

    response = lambda_handler(event, mock_lambda_context)
    assert response == {"batchItemFailures": []}

    mock_app.assert_called_once()  # Should create a new instance
    mock_app.return_value.handle_sqs_event.assert_called_once_with(
        event,
        mock_lambda_context,
    )


def test_lambda_handler_existing_app(
    mocker: MockerFixture,
    mock_lambda_context: LambdaContext,
) -> None:
    """
    Test that the lambda_handler uses the existing DataMigrationApplication if it is already initialized.
    """
    mock_app = mocker.patch("pipeline.lambda_handler.DataMigrationApplication")
    mocker.patch("pipeline.lambda_handler.APP", mock_app.return_value)
    mock_app.return_value.handle_sqs_event = mocker.Mock(
        return_value={"batchItemFailures": []}
    )

    event = {
        "Records": [
            {
                "body": '{"type": "dms_event", "record_id": 12345, "table_name": "services", "method": "insert"}'
            }
        ]
    }

    response = lambda_handler(event, mock_lambda_context)
    assert response == {"batchItemFailures": []}

    mock_app.assert_not_called()  # Should not create a new instance
    mock_app.return_value.handle_sqs_event.assert_called_once_with(
        event, mock_lambda_context
    )
