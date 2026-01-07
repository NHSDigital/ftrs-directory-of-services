import pytest
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from ftrs_common.mocks.mock_logger import MockLogger
from pytest_mock import MockerFixture

from service_migration.application import DMSEvent, ServiceMigrationApplication
from service_migration.config import ServiceMigrationConfig
from service_migration.exceptions import ServiceMigrationException
from service_migration.processor import ServiceMigrationProcessor


def test_application_init(
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    assert app.logger == mock_logger
    assert app.config == mock_config
    assert isinstance(app.processor, ServiceMigrationProcessor)

    assert mock_logger.get_log("SM_APP_001", level="DEBUG") == [
        {
            "msg": "Starting Service Migration Lambda Application",
            "detail": {
                "config": {
                    "db_config": {
                        "host": "localhost",
                        "port": 5432,
                        "username": "user",
                        "password": "**********",
                        "dbname": "testdb",
                    },
                    "env": "local",
                    "workspace": "test-workspace",
                    "dynamodb_endpoint": "http://localhost:8000",
                }
            },
        }
    ]
    assert mock_logger.was_logged("SM_APP_002", level="INFO") is True


def test_handle_sqs_event(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_event = {
        "Records": [
            {
                "body": '{"record_id": 123, "service_id": 456, "table_name": "services", "method": "insert"}'
            }
        ]
    }
    mock_context = mocker.MagicMock()

    app.handle_sqs_record = mocker.MagicMock()
    result = app.handle_sqs_event(mock_event, mock_context)

    app.handle_sqs_record.assert_called_once()

    assert mock_logger.get_log("SM_APP_003") == [
        {
            "msg": "Handling incoming SQS event",
            "detail": {"event": mock_event},
        }
    ]

    assert mock_logger.was_logged("SM_APP_004") is True
    assert mock_logger.was_logged("SM_APP_005") is False
    assert result == {"batchItemFailures": []}


def test_handle_sqs_event_whole_batch_failure(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_event = {
        "Records": [
            {
                "body": '{"record_id": 123, "service_id": 456, "table_name": "services", "method": "insert"}'
            }
        ]
    }
    mock_context = mocker.MagicMock()

    app.handle_sqs_record = mocker.MagicMock(side_effect=Exception("Test exception"))

    with pytest.raises(
        ServiceMigrationException,
        match="Fatal error during batch processing",
    ):
        app.handle_sqs_event(mock_event, mock_context)

    app.handle_sqs_record.assert_called_once()

    assert mock_logger.get_log("SM_APP_003") == [
        {
            "msg": "Handling incoming SQS event",
            "detail": {"event": mock_event},
        }
    ]

    assert mock_logger.was_logged("SM_APP_004") is False
    assert mock_logger.was_logged("SM_APP_005") is False
    assert mock_logger.was_logged("SM_APP_010", level="ERROR") is True


def test_handle_sqs_event_partial_batch_failure(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_event = {
        "Records": [
            {
                "messageId": "1",
                "body": '{"record_id": 123, "service_id": 456, "table_name": "services", "method": "insert"}',
            },
            {
                "messageId": "2",
                "body": '{"record_id": 124, "service_id": 457, "table_name": "services", "method": "insert"}',
            },
        ]
    }
    mock_context = mocker.MagicMock()

    app.handle_sqs_record = mocker.MagicMock(
        side_effect=[None, Exception("Test exception")]
    )

    app.handle_sqs_event(mock_event, mock_context)

    assert mock_logger.get_log("SM_APP_003") == [
        {
            "msg": "Handling incoming SQS event",
            "detail": {"event": mock_event},
        }
    ]

    assert mock_logger.was_logged("SM_APP_004") is True
    assert mock_logger.was_logged("SM_APP_005") is True
    assert mock_logger.was_logged("SM_APP_010") is False

    assert mock_logger.get_log("SM_APP_005") == [
        {
            "msg": "Some records could not be processed - reporting failures to SQS",
            "detail": {
                "failures": [{"itemIdentifier": "2"}],
            },
        }
    ]


def test_handle_sqs_record_service_event(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 123, "service_id": 123, "table_name": "services", "method": "insert"}',
        }
    )

    app.processor.sync_service = mocker.MagicMock(return_value=None)
    assert app.handle_sqs_record(mock_sqs_record) is None

    assert mock_logger.get_log("SM_APP_006") == [
        {
            "msg": "Starting to process DMS event",
            "detail": {
                "event": {
                    "record_id": 123,
                    "service_id": 123,
                    "table_name": "services",
                    "method": "insert",
                }
            },
        }
    ]

    app.processor.sync_service.assert_called_once_with(123, "insert")

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_handle_sqs_record_endpoint_update(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 456, "service_id": 123, "table_name": "serviceendpoints", "method": "insert"}',
        }
    )

    app.processor.sync_service = mocker.MagicMock(return_value=None)
    assert app.handle_sqs_record(mock_sqs_record) is None

    assert mock_logger.get_log("SM_APP_006") == [
        {
            "msg": "Starting to process DMS event",
            "detail": {
                "event": {
                    "record_id": 456,
                    "service_id": 123,
                    "table_name": "serviceendpoints",
                    "method": "insert",
                }
            },
        }
    ]

    app.processor.sync_service.assert_called_once_with(123, "update")

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_handle_sqs_record_unsupported_table(
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 789, "service_id": 123, "table_name": "unsupported_table", "method": "insert"}',
        }
    )

    # Should not requeue - no exception expected
    assert app.handle_sqs_record(mock_sqs_record) is None
    assert mock_logger.get_log("SM_APP_008b") == [
        {
            "msg": "A non-recoverable service migration exception occurred during processing: Unsupported table for migration: unsupported_table",
            "detail": {"error": "Unsupported table for migration: unsupported_table"},
        }
    ]

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_handle_sqs_record_invalid_event(
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"service_id": 123, "table_name": "unsupported_table", "method": "insert"}',
        }
    )

    # Should not requeue - no exception expected
    assert app.handle_sqs_record(mock_sqs_record) is None

    assert mock_logger.was_logged("SM_APP_011") is True
    assert mock_logger.get_log("SM_APP_008b") == [
        {
            "msg": "A non-recoverable service migration exception occurred during processing: Failed to parse SQS record body into DMSEvent",
            "detail": {"error": "Failed to parse SQS record body into DMSEvent"},
        }
    ]

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_handle_sqs_record_recoverable_error(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 123, "service_id": 123, "table_name": "services", "method": "insert"}',
        }
    )

    app.handle_service_event = mocker.MagicMock(
        side_effect=ServiceMigrationException(
            message="Temporary error",
            should_requeue=True,
        )
    )

    with pytest.raises(ServiceMigrationException, match="Temporary error"):
        app.handle_sqs_record(mock_sqs_record)

    assert mock_logger.get_log("SM_APP_008a") == [
        {
            "msg": "A recoverable service migration exception occurred during processing: Temporary error",
            "detail": {"error": "Temporary error"},
        }
    ]

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_handle_sqs_record_unrecoverable_error(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 123, "service_id": 123, "table_name": "services", "method": "insert"}',
        }
    )

    app.handle_service_event = mocker.MagicMock(
        side_effect=ServiceMigrationException(
            message="Permanent error",
            should_requeue=False,
        )
    )

    assert app.handle_sqs_record(mock_sqs_record) is None

    assert mock_logger.get_log("SM_APP_008b") == [
        {
            "msg": "A non-recoverable service migration exception occurred during processing: Permanent error",
            "detail": {"error": "Permanent error"},
        }
    ]

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_handle_sqs_record_unexpected_error(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 123, "service_id": 123, "table_name": "services", "method": "insert"}',
        }
    )

    app.handle_service_event = mocker.MagicMock(
        side_effect=Exception("Unexpected error")
    )

    with pytest.raises(Exception, match="Unexpected error"):
        app.handle_sqs_record(mock_sqs_record)

    assert mock_logger.get_log("SM_APP_009") == [
        {
            "msg": "An unexpected exception occurred during processing: Unexpected error",
            "detail": {"error": "Unexpected error"},
        }
    ]

    # Duration always logged
    assert mock_logger.was_logged("SM_APP_007", level="INFO") is True


def test_parse_sqs_record_valid_record(
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"record_id": 123, "service_id": 456, "table_name": "services", "method": "insert"}',
        }
    )

    event = app.parse_sqs_record(mock_sqs_record)

    assert event == DMSEvent(
        record_id=123,
        service_id=456,
        table_name="services",
        method="insert",
    )


def test_parse_sqs_record_invalid_record(
    mock_logger: MockLogger,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_sqs_record = SQSRecord(
        data={
            "messageId": "1",
            "body": '{"invalid_json"}',
        }
    )

    with pytest.raises(
        ServiceMigrationException,
        match="Failed to parse SQS record body into DMSEvent",
    ):
        app.parse_sqs_record(mock_sqs_record)

    assert mock_logger.get_log("SM_APP_011") == [
        {
            "msg": (
                "Failed to parse SQS record: 1 validation error for DMSEvent\n"
                "  Invalid JSON: expected `:` at line 1 column 16 [type=json_invalid, "
                "input_value='{\"invalid_json\"}', input_type=str]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.12/v/json_invalid"
            ),
            "detail": {
                "error": (
                    "1 validation error for DMSEvent\n"
                    "  Invalid JSON: expected `:` at line 1 column 16 "
                    "[type=json_invalid, input_value='{\"invalid_json\"}', "
                    "input_type=str]\n"
                    "    For further information visit "
                    "https://errors.pydantic.dev/2.12/v/json_invalid"
                ),
                "record_body": '{"invalid_json"}',
            },
        }
    ]


def test_create_dependencies(
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)
    app.create_db_engine = lambda _: "mock_engine"

    deps = app.create_dependencies(mock_config)

    assert deps.logger == app.logger
    assert deps.config == mock_config
    assert deps.ddb_client.meta.service_model.service_name == "dynamodb"
    assert deps.ddb_client.meta.endpoint_url == mock_config.dynamodb_endpoint

    assert deps.engine == "mock_engine"


def test_create_db_engine(
    mocker: MockerFixture, mock_config: ServiceMigrationConfig
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_engine = mocker.MagicMock()
    mock_create_engine = mocker.patch(
        "service_migration.application.create_engine",
        return_value=mock_engine,
    )

    app.create_db_engine(mock_config)

    mock_create_engine.assert_called_once_with(
        mock_config.db_config.connection_string,
        echo=False,
    )

    mock_engine.execution_options.assert_called_once_with(postgresql_readonly=True)


def test_create_logger(
    mocker: MockerFixture,
    mock_config: ServiceMigrationConfig,
) -> None:
    app = ServiceMigrationApplication(config=mock_config)

    mock_logger_instance = mocker.MagicMock()
    mock_get_logger = mocker.patch(
        "service_migration.application.Logger.get",
        return_value=mock_logger_instance,
    )

    logger = app.create_logger(mock_config)

    mock_get_logger.assert_called_once_with(service="data-migration")
    mock_logger_instance.append_keys.assert_called_once()
    assert "run_id" in mock_logger_instance.append_keys.call_args[1]
    assert mock_logger_instance.append_keys.call_args[1]["env"] == "local"
    assert (
        mock_logger_instance.append_keys.call_args[1]["workspace"] == "test-workspace"
    )
    assert logger == mock_logger_instance
