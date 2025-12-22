from unittest.mock import MagicMock, patch

import pytest
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.consumer.consumer_handler import consumer_lambda_handler


@patch("pipeline.consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_success(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "test2", "body": {"key": "value2"}},
        ]
    }

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == []
    assert str(mock_process_message.call_count) == "2"

    expected_processing_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="1", total_records=2
        )
    )
    expected_success_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_004.value.message.format(message_id="1")
    )
    expected_processing_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="2", total_records=2
        )
    )
    expected_success_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_004.value.message.format(message_id="2")
    )
    assert expected_processing_log_1 in caplog.text
    assert expected_success_log_1 in caplog.text
    assert expected_processing_log_2 in caplog.text
    assert expected_success_log_2 in caplog.text

    expected_batch_complete_log = (
        OdsETLPipelineLogBase.ETL_CONSUMER_BATCH_COMPLETE.value.message
    )
    expected_pipeline_end_log = OdsETLPipelineLogBase.ETL_PIPELINE_END.value.message
    assert expected_batch_complete_log in caplog.text
    assert expected_pipeline_end_log in caplog.text


@patch("pipeline.consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_no_event_data(mock_process_message: MagicMock) -> None:
    consumer_lambda_handler({}, {})

    assert str(mock_process_message.call_count) == "0"


@patch("pipeline.consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_failure(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "test2", "body": {"key": "value2"}},
        ]
    }

    mock_process_message.side_effect = [Exception("Test exception"), None]

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == [{"itemIdentifier": "1"}]
    assert str(mock_process_message.call_count) == "2"

    expected_processing_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="1", total_records=2
        )
    )
    expected_failure_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_005.value.message.format(message_id="1")
    )
    expected_processing_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="2", total_records=2
        )
    )
    expected_success_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_004.value.message.format(message_id="2")
    )

    assert expected_processing_log_1 in caplog.text
    assert expected_failure_log_1 in caplog.text
    assert expected_processing_log_2 in caplog.text
    assert expected_success_log_2 in caplog.text

    expected_batch_complete_log = (
        OdsETLPipelineLogBase.ETL_CONSUMER_BATCH_COMPLETE.value.message
    )
    expected_pipeline_end_log = OdsETLPipelineLogBase.ETL_PIPELINE_END.value.message
    assert expected_batch_complete_log in caplog.text
    assert expected_pipeline_end_log in caplog.text


@patch("pipeline.consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_logs_start_events(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "test1", "body": {"key": "value1"}},
        ]
    }

    consumer_lambda_handler(event, {})

    expected_consumer_start_log = OdsETLPipelineLogBase.ETL_CONSUMER_001.value.message
    assert expected_consumer_start_log in caplog.text


@patch("pipeline.consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_logs_batch_statistics(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "test2", "body": {"key": "value2"}},
            {"messageId": "3", "path": "test3", "body": {"key": "value3"}},
        ]
    }

    mock_process_message.side_effect = [None, Exception("Test exception"), None]

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == [{"itemIdentifier": "2"}]

    expected_batch_complete_log = (
        OdsETLPipelineLogBase.ETL_CONSUMER_BATCH_COMPLETE.value.message
    )
    expected_pipeline_end_log = OdsETLPipelineLogBase.ETL_PIPELINE_END.value.message
    assert expected_batch_complete_log in caplog.text
    assert expected_pipeline_end_log in caplog.text


@pytest.mark.parametrize(
    ("path", "body"),
    [
        (None, {"name": "Organization Name"}),
        ("uuid", None),
        ("", {"name": "Organization Name"}),
        ("uuid", {}),
    ],
)
def test_consumer_lambda_handler_handle_missing_message_parameters(
    path: str,
    body: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {
                "messageId": "1",
                "path": path,
                "body": body,
            }
        ]
    }

    consumer_lambda_handler(event, {})

    assert any(
        record.levelname == "WARNING"
        and "Message id: 1 is missing 'path' or 'body' fields." in record.message
        for record in caplog.records
    )
    assert any(
        record.levelname == "ERROR"
        and "Failed to process message id: 1." in record.message
        for record in caplog.records
    )
