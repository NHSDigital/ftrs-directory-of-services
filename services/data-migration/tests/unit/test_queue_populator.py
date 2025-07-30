from pipeline.queue_populator import (
    get_record_ids,
    QueuePopulatorConfig,
    QueuePopulatorEvent,
    DatabaseConfig,
    get_dms_event_batches,
    send_message_batch,
    populate_sqs_queue,
    lambda_handler,
)
import pytest
from pytest_mock import MockerFixture
from unittest.mock import MagicMock
from sqlalchemy.engine import create_mock_engine
from sqlalchemy.engine.mock import MockConnection
from sqlalchemy import Engine
from sqlmodel import select
from ftrs_data_layer.domain.legacy import Service
import json
from ftrs_common.mocks.mock_logger import MockLogger
from itertools import batched


@pytest.fixture
def mock_config() -> QueuePopulatorConfig:
    return QueuePopulatorConfig(
        db_config=DatabaseConfig.from_uri(
            "postgresql://username:password@localhost:5432/dbname"
        ),
        SQS_QUEUE_URL="http://localhost:4566/000000000000/test-queue",
        type_ids=None,
        status_ids=None,
    )


@pytest.fixture
def mock_sql_executor(
    mocker: MockerFixture, mock_config: QueuePopulatorConfig
) -> MagicMock:
    executor = mocker.MagicMock()
    engine = create_mock_engine(
        url=mock_config.db_config.connection_string,
        executor=executor,
    )
    engine.begin = mocker.MagicMock()
    engine.close = mocker.MagicMock()
    engine.in_transaction = mocker.MagicMock(return_value=False)
    mocker.patch("pipeline.queue_populator.create_engine", return_value=engine)
    return executor


def test_get_record_ids(
    mock_config: QueuePopulatorConfig,
    mock_sql_executor: MagicMock,
) -> None:
    get_record_ids(mock_config)

    mock_sql_executor.assert_called_once()
    statement = mock_sql_executor.mock_calls[0][1][0]

    assert str(statement) == (
        "SELECT pathwaysdos.services.id \nFROM pathwaysdos.services"
    )


def test_get_record_ids_with_type_ids(
    mock_config: QueuePopulatorConfig,
    mock_sql_executor: MagicMock,
) -> None:
    mock_config.type_ids = [1, 2, 3]
    get_record_ids(mock_config)

    mock_sql_executor.assert_called_once()
    statement = mock_sql_executor.mock_calls[0][1][0]
    compiled_statement = statement.compile(compile_kwargs={"literal_binds": True})

    assert str(compiled_statement) == (
        "SELECT pathwaysdos.services.id \n"
        "FROM pathwaysdos.services \n"
        "WHERE pathwaysdos.services.typeid IN (1, 2, 3)"
    )


def test_get_record_ids_with_status_ids(
    mock_config: QueuePopulatorConfig,
    mock_sql_executor: MagicMock,
) -> None:
    mock_config.status_ids = [1, 2, 3]
    get_record_ids(mock_config)

    mock_sql_executor.assert_called_once()
    statement = mock_sql_executor.mock_calls[0][1][0]
    compiled_statement = statement.compile(compile_kwargs={"literal_binds": True})

    assert str(compiled_statement) == (
        "SELECT pathwaysdos.services.id \n"
        "FROM pathwaysdos.services \n"
        "WHERE pathwaysdos.services.statusid IN (1, 2, 3)"
    )


def test_get_record_ids_with_type_and_status_ids(
    mock_config: QueuePopulatorConfig,
    mock_sql_executor: MagicMock,
) -> None:
    mock_config.type_ids = [1, 2, 3]
    mock_config.status_ids = [4, 5, 6]
    get_record_ids(mock_config)

    mock_sql_executor.assert_called_once()
    statement = mock_sql_executor.mock_calls[0][1][0]
    compiled_statement = statement.compile(compile_kwargs={"literal_binds": True})

    assert str(compiled_statement) == (
        "SELECT pathwaysdos.services.id \n"
        "FROM pathwaysdos.services \n"
        "WHERE pathwaysdos.services.typeid IN (1, 2, 3) "
        "AND pathwaysdos.services.statusid IN (4, 5, 6)"
    )


def test_get_dms_event_batches(
    mocker: MockerFixture, mock_config: QueuePopulatorConfig
) -> None:
    record_ids = list(range(1, 20))
    mocker.patch("pipeline.queue_populator.get_record_ids", return_value=record_ids)

    expected_batch_count = 2

    batches = list(get_dms_event_batches(mock_config))

    assert len(batches) == expected_batch_count

    assert batches[0] == {
        "QueueUrl": mock_config.sqs_queue_url,
        "Entries": [
            {
                "Id": str(record_id),
                "MessageBody": '{"type":"dms_event","record_id":'
                + str(record_id)
                + ',"table_name":"services","method":"insert"}',
            }
            for record_id in range(1, 11)
        ],
    }
    assert batches[1] == {
        "QueueUrl": mock_config.sqs_queue_url,
        "Entries": [
            {
                "Id": str(record_id),
                "MessageBody": '{"type":"dms_event","record_id":'
                + str(record_id)
                + ',"table_name":"services","method":"insert"}',
            }
            for record_id in range(11, 20)
        ],
    }


def test_send_message_batch(mocker: MockerFixture, mock_logger: MockLogger) -> None:
    mock_sqs_client = mocker.MagicMock()
    mock_sqs_client.send_message_batch = mocker.MagicMock(
        return_value={
            "Successful": [
                {"Id": "1"},
                {"Id": "2"},
            ],
            "Failed": [],
        }
    )

    mocker.patch("pipeline.queue_populator.SQS_CLIENT", mock_sqs_client)
    mocker.patch("pipeline.queue_populator.LOGGER", mock_logger)

    batch = {
        "QueueUrl": "http://localhost:4566/000000000000/test-queue",
        "Entries": [
            {
                "Id": "1",
                "MessageBody": '{"type":"dms_event","record_id":1,"table_name":"services","method":"insert"}',
            },
            {
                "Id": "2",
                "MessageBody": '{"type":"dms_event","record_id":2,"table_name":"services","method":"insert"}',
            },
        ],
    }

    send_message_batch(batch)

    mock_sqs_client.send_message_batch.assert_called_once_with(
        QueueUrl=batch["QueueUrl"],
        Entries=batch["Entries"],
    )

    assert mock_logger.was_logged("DM_QP_002") is False
    assert mock_logger.get_log("DM_QP_003") == [
        {
            "detail": {
                "count": 2,
                "queue_url": "http://localhost:4566/000000000000/test-queue",
                "record_ids": ["1", "2"],
            },
            "msg": "Successfully sent 2 messages to SQS queue",
            "reference": "DM_QP_003",
        }
    ]


def test_send_message_batch_with_failed_messages(
    mocker: MockerFixture, mock_logger: MockLogger
) -> None:
    mock_sqs_client = mocker.MagicMock()
    mock_sqs_client.send_message_batch = mocker.MagicMock(
        return_value={
            "Successful": [],
            "Failed": [
                {"Id": "1", "Message": "Failed to send message"},
                {"Id": "2", "Message": "Failed to send message"},
            ],
        }
    )

    mocker.patch("pipeline.queue_populator.SQS_CLIENT", mock_sqs_client)
    mocker.patch("pipeline.queue_populator.LOGGER", mock_logger)

    batch = {
        "QueueUrl": "http://localhost:4566/000000000000/test-queue",
        "Entries": [
            {
                "Id": "1",
                "MessageBody": '{"type":"dms_event","record_id":1,"table_name":"services","method":"insert"}',
            },
            {
                "Id": "2",
                "MessageBody": '{"type":"dms_event","record_id":2,"table_name":"services","method":"insert"}',
            },
        ],
    }

    send_message_batch(batch)

    mock_sqs_client.send_message_batch.assert_called_once_with(
        QueueUrl=batch["QueueUrl"],
        Entries=batch["Entries"],
    )

    assert mock_logger.get_log("DM_QP_002") == [
        {
            "detail": {
                "count": 2,
                "failed": [
                    {"Id": "1", "Message": "Failed to send message"},
                    {"Id": "2", "Message": "Failed to send message"},
                ],
                "queue_url": "http://localhost:4566/000000000000/test-queue",
            },
            "msg": "Failed to send 2 messages to SQS queue",
            "reference": "DM_QP_002",
        }
    ]
    assert mock_logger.was_logged("DM_QP_003") is False


def test_send_message_batch_mixed_results(
    mocker: MockerFixture, mock_logger: MockLogger
) -> None:
    mock_sqs_client = mocker.MagicMock()
    mock_sqs_client.send_message_batch = mocker.MagicMock(
        return_value={
            "Successful": [{"Id": "1"}],
            "Failed": [
                {"Id": "2", "Message": "Failed to send message"},
                {"Id": "3", "Message": "Failed to send message"},
            ],
        }
    )

    mocker.patch("pipeline.queue_populator.SQS_CLIENT", mock_sqs_client)
    mocker.patch("pipeline.queue_populator.LOGGER", mock_logger)

    batch = {
        "QueueUrl": "http://localhost:4566/000000000000/test-queue",
        "Entries": [
            {
                "Id": "1",
                "MessageBody": '{"type":"dms_event","record_id":1,"table_name":"services","method":"insert"}',
            },
            {
                "Id": "2",
                "MessageBody": '{"type":"dms_event","record_id":2,"table_name":"services","method":"insert"}',
            },
            {
                "Id": "3",
                "MessageBody": '{"type":"dms_event","record_id":3,"table_name":"services","method":"insert"}',
            },
        ],
    }

    send_message_batch(batch)

    mock_sqs_client.send_message_batch.assert_called_once_with(
        QueueUrl=batch["QueueUrl"],
        Entries=batch["Entries"],
    )

    assert mock_logger.get_log("DM_QP_002") == [
        {
            "detail": {
                "count": 2,
                "failed": [
                    {"Id": "2", "Message": "Failed to send message"},
                    {"Id": "3", "Message": "Failed to send message"},
                ],
                "queue_url": "http://localhost:4566/000000000000/test-queue",
            },
            "msg": "Failed to send 2 messages to SQS queue",
            "reference": "DM_QP_002",
        }
    ]
    assert mock_logger.get_log("DM_QP_003") == [
        {
            "detail": {
                "count": 1,
                "queue_url": "http://localhost:4566/000000000000/test-queue",
                "record_ids": ["1"],
            },
            "msg": ("Successfully sent 1 messages to SQS queue"),
            "reference": "DM_QP_003",
        }
    ]


def test_populate_sqs_queue(
    mocker: MockerFixture, mock_config: QueuePopulatorConfig, mock_logger: MockLogger
) -> None:
    record_ids = list(range(1, 1000))
    mocker.patch("pipeline.queue_populator.get_record_ids", return_value=record_ids)
    mocker.patch("pipeline.queue_populator.LOGGER", mock_logger)

    expected_batch_count = 100  # 1000 records / 10 per batch

    mock_send_message_batch = mocker.MagicMock()
    mocker.patch("pipeline.queue_populator.send_message_batch", mock_send_message_batch)

    populate_sqs_queue(mock_config)

    assert mock_send_message_batch.call_count == expected_batch_count
    assert mock_logger.get_log("DM_QP_000") == [
        {
            "detail": {
                "type_ids": None,
                "status_ids": None,
            },
            "msg": "Starting Data Migration Queue Populator",
            "reference": "DM_QP_000",
        }
    ]
    assert mock_logger.get_log("DM_QP_999") == [
        {
            "msg": "Data Migration Queue Populator completed",
            "reference": "DM_QP_999",
        }
    ]


def test_lambda_handler(
    mocker: MockerFixture, mock_config: QueuePopulatorConfig
) -> None:
    mock_populate = mocker.patch("pipeline.queue_populator.populate_sqs_queue")
    mocker.patch.object(
        DatabaseConfig, "from_secretsmanager", return_value=mock_config.db_config
    )
    mocker.patch("os.environ", {"SQS_QUEUE_URL": mock_config.sqs_queue_url})

    event = {
        "type_ids": [1, 2, 3],
        "status_ids": [4, 5, 6],
    }
    context = {}

    lambda_handler(event, context)

    mock_populate.assert_called_once_with(
        config=QueuePopulatorConfig(
            db_config=mock_config.db_config,
            type_ids=[1, 2, 3],
            status_ids=[4, 5, 6],
        )
    )
