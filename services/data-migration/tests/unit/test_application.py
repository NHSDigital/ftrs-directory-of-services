import pytest
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from ftrs_common.mocks.mock_logger import MockLogger
from pytest_mock import MockerFixture

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.processor import DataMigrationProcessor
from pipeline.triagecode_processor import TriageCodeProcessor
from pipeline.utils.config import DataMigrationConfig


def test_application_init(
    mock_logger: MockLogger, mock_config: DataMigrationConfig
) -> None:
    app = DataMigrationApplication(config=mock_config)

    assert app.logger == mock_logger
    assert app.config == mock_config
    assert isinstance(app.processor, DataMigrationProcessor)
    assert isinstance(app.triage_code_processor, TriageCodeProcessor)


def test_handle_sqs_record_invalid_method(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_event = DMSEvent(
        type="dms_event",
        record_id=123,
        table_name="test_table",
        method="delete",  # Unsupported method
    )
    mock_record = SQSRecord(
        data={
            "messageId": 123,
            "body": mock_event.model_dump_json(),
        }
    )

    app.processor.sync_service = mocker.MagicMock()

    app.handle_sqs_record(mock_record)

    # Ensure no processing occurs for unsupported methods
    assert not app.processor.sync_service.called

    assert mock_logger.get_log("DM_ETL_010") == [
        {
            "detail": {
                "method": "delete",
                "event": {
                    "type": "dms_event",
                    "record_id": 123,
                    "table_name": "test_table",
                    "method": "delete",
                },
            },
            "msg": "Unsupported event method: delete",
            "reference": "DM_ETL_010",
        }
    ]


def test_handle_sqs_record_invalid_table(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_event = DMSEvent(
        type="dms_event",
        record_id=123,
        table_name="invalid_table",  # Unsupported table
        method="insert",
    )
    mock_record = SQSRecord(
        data={
            "messageId": 123,
            "body": mock_event.model_dump_json(),
        }
    )
    app.processor.sync_service = mocker.MagicMock()

    app.handle_sqs_record(mock_record)

    # Ensure no processing occurs for unsupported tables
    assert not app.processor.sync_service.called

    assert mock_logger.get_log("DM_ETL_011") == [
        {
            "detail": {
                "table_name": "invalid_table",
                "method": "insert",
                "event": {
                    "type": "dms_event",
                    "record_id": 123,
                    "table_name": "invalid_table",
                    "method": "insert",
                },
            },
            "msg": "Table invalid_table not supported for event method: insert",
            "reference": "DM_ETL_011",
        }
    ]


def test_handle_sqs_record_supported_event(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_event = DMSEvent(
        type="dms_event",
        record_id=123,
        table_name="services",
        method="insert",
    )
    mock_record = SQSRecord(
        data={
            "messageId": 123,
            "body": mock_event.model_dump_json(),
        }
    )

    app.processor.sync_service = mocker.MagicMock()

    app.handle_sqs_record(mock_record)

    app.processor.sync_service.assert_called_once_with(123, "insert")

    assert mock_logger.was_logged("DM_ETL_010") is False
    assert mock_logger.was_logged("DM_ETL_011") is False


def test_handle_sqs_record_case_insensitive_method(
    mocker: MockerFixture,
    mock_logger: MockLogger,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_event = DMSEvent(
        type="dms_event",
        record_id=123,
        table_name="services",
        method="InSeRt",  # Mixed case method
    )
    mock_record = SQSRecord(
        data={
            "messageId": 123,
            "body": mock_event.model_dump_json(),
        }
    )

    app.processor.sync_service = mocker.MagicMock()

    app.handle_sqs_record(mock_record)

    app.processor.sync_service.assert_called_once_with(123, "InSeRt")

    assert mock_logger.was_logged("DM_ETL_010") is False
    assert mock_logger.was_logged("DM_ETL_011") is False


def test_handle_full_sync_event(
    mocker: MockerFixture,
    mock_config: DataMigrationConfig,
) -> None:
    app = DataMigrationApplication(config=mock_config)
    app.processor.sync_all_services = mocker.MagicMock()
    app.triage_code_processor.sync_all_triage_codes = mocker.MagicMock()

    app.handle_full_sync_event()
    app.processor.sync_all_services.assert_called_once()
    app.triage_code_processor.sync_all_triage_codes.assert_called_once()


def test_parse_event_dms_event(mock_config: DataMigrationConfig) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_record_id = 123
    mock_event = {
        "type": "dms_event",
        "record_id": mock_record_id,
        "table_name": "test_table",
        "method": "insert",
    }

    parsed_event = app.parse_event(mock_event)

    assert isinstance(parsed_event, DMSEvent)
    assert parsed_event.record_id == mock_record_id
    assert parsed_event.table_name == "test_table"
    assert parsed_event.method == "insert"
    assert parsed_event.type == "dms_event"


def test_parse_event_invalid_type(
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_event = {"type": "invalid_event"}

    with pytest.raises(ValueError, match="Invalid event format"):
        app.parse_event(mock_event)

    assert mock_logger.get_log("DM_ETL_009") == [
        {
            "reference": "DM_ETL_009",
            "detail": {
                "error": "4 validation errors for DMSEvent\n"
                "type\n"
                "  Input should be 'dms_event' [type=literal_error, "
                "input_value='invalid_event', input_type=str]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.12/v/literal_error\n"
                "record_id\n"
                "  Field required [type=missing, input_value={'type': "
                "'invalid_event'}, input_type=dict]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.12/v/missing\n"
                "table_name\n"
                "  Field required [type=missing, input_value={'type': "
                "'invalid_event'}, input_type=dict]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.12/v/missing\n"
                "method\n"
                "  Field required [type=missing, input_value={'type': "
                "'invalid_event'}, input_type=dict]\n"
                "    For further information visit "
                "https://errors.pydantic.dev/2.12/v/missing",
                "event": {
                    "type": "invalid_event",
                },
            },
            "msg": "Error parsing event: 4 validation errors for DMSEvent\n"
            "type\n"
            "  Input should be 'dms_event' [type=literal_error, "
            "input_value='invalid_event', input_type=str]\n"
            "    For further information visit "
            "https://errors.pydantic.dev/2.12/v/literal_error\n"
            "record_id\n"
            "  Field required [type=missing, input_value={'type': "
            "'invalid_event'}, input_type=dict]\n"
            "    For further information visit "
            "https://errors.pydantic.dev/2.12/v/missing\n"
            "table_name\n"
            "  Field required [type=missing, input_value={'type': "
            "'invalid_event'}, input_type=dict]\n"
            "    For further information visit "
            "https://errors.pydantic.dev/2.12/v/missing\n"
            "method\n"
            "  Field required [type=missing, input_value={'type': "
            "'invalid_event'}, input_type=dict]\n"
            "    For further information visit "
            "https://errors.pydantic.dev/2.12/v/missing",
        }
    ]


def test_create_logger(
    mock_config: DataMigrationConfig,
    mock_logger: MockLogger,
    mocker: MockerFixture,
) -> None:
    app = DataMigrationApplication(config=mock_config)

    mock_logger.append_keys = mocker.MagicMock()
    mocker.patch("pipeline.application.uuid4", return_value="test-uuid")

    logger = app.create_logger()

    assert logger == mock_logger
    assert mock_logger.append_keys.call_count == 1
    mock_logger.append_keys.assert_called_with(
        run_id="test-uuid",
        env="test",
        workspace="test_workspace",
    )
