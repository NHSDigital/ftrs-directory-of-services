from aws_lambda_powertools.utilities.data_classes import SQSEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from pytest_mock import MockerFixture

from service_migration.application import ServiceMigrationApplication
from service_migration.config import ServiceMigrationConfig
from service_migration.lambda_handler import lambda_handler


def test_lambda_handler(
    mocker: MockerFixture,
    mock_lambda_context: LambdaContext,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)
    app.handle_sqs_record = mocker.MagicMock()

    mocker.patch(
        "service_migration.lambda_handler.ServiceMigrationApplication", return_value=app
    )

    event = SQSEvent(
        data={
            "Records": [
                {
                    "body": '{"record_id": 1,"service_id":1, "table_name": "test_table", "method": "insert"}'
                },
                {
                    "body": '{"record_id": 2,"service_id":2, "table_name": "test_table", "method": "update"}'
                },
            ]
        }
    )

    result = lambda_handler(event, mock_lambda_context)

    assert result == {"batchItemFailures": []}

    expected_call_count = 2

    assert app.handle_sqs_record.call_count == expected_call_count
    first_call, second_call = app.handle_sqs_record.call_args_list

    assert first_call.kwargs["record"].json_body == {
        "record_id": 1,
        "service_id": 1,
        "table_name": "test_table",
        "method": "insert",
    }

    assert second_call.kwargs["record"].json_body == {
        "record_id": 2,
        "service_id": 2,
        "table_name": "test_table",
        "method": "update",
    }


def test_lambda_handler_no_app(
    mocker: MockerFixture,
    mock_lambda_context: LambdaContext,
    mock_config: ServiceMigrationConfig,
) -> None:
    """
    Test that the lambda_handler initializes the ServiceMigrationApplication if it is None.
    """
    mocker.patch(
        "service_migration.application.ServiceMigrationConfig",
        return_value=mock_config,
    )
    mocker.patch("service_migration.lambda_handler.APP", None)

    app_init_spy = mocker.spy(ServiceMigrationApplication, "__init__")
    mock_handle_sqs_event = mocker.patch.object(
        ServiceMigrationApplication, "handle_sqs_event"
    )
    mock_handle_sqs_event.return_value = {"batchItemFailures": []}

    event = {
        "Records": [
            {
                "body": '{"record_id": 12345,"service_id": 12345, "table_name": "services", "method": "insert"}'
            }
        ]
    }

    result = lambda_handler(event, mock_lambda_context)
    assert result == {"batchItemFailures": []}

    app_init_spy.assert_called_once()
    mock_handle_sqs_event.assert_called_once_with(event, mock_lambda_context)


def test_lambda_handler_existing_app(
    mocker: MockerFixture,
    mock_lambda_context: LambdaContext,
    mock_config: ServiceMigrationConfig,
) -> None:
    """
    Test that the lambda_handler uses the existing ServiceMigrationApplication if it is already initialized.
    """
    mocker.patch(
        "service_migration.application.ServiceMigrationConfig",
        return_value=mock_config,
    )
    mock_app = mocker.patch(
        "service_migration.lambda_handler.ServiceMigrationApplication"
    )

    mocker.patch("service_migration.lambda_handler.APP", mock_app.return_value)
    mock_app.return_value.handle_sqs_event = mocker.Mock(
        return_value={"batchItemFailures": []}
    )

    event = {
        "Records": [
            {
                "body": '{"record_id": 12345, "table_name": "services", "method": "insert"}'
            }
        ]
    }

    result = lambda_handler(event, mock_lambda_context)
    assert result == {"batchItemFailures": []}

    mock_app.assert_not_called()  # Should not create a new instance
    mock_app.return_value.handle_sqs_event.assert_called_once_with(
        event, mock_lambda_context
    )
