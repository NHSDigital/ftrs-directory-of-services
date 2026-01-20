from unittest.mock import MagicMock, patch

import pytest

from consumer.consumer_handler import consumer_lambda_handler


@patch("consumer.consumer_handler.setup_request_context")
@patch("consumer.consumer_handler.extract_correlation_id_from_sqs_records")
@patch("consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_success(
    mock_process_message: MagicMock,
    mock_extract_correlation_id: MagicMock,
    mock_setup_context: MagicMock,
) -> None:
    """Test successful processing of SQS records."""
    mock_extract_correlation_id.return_value = "test-correlation-id"
    mock_context = MagicMock()
    event = {
        "Records": [
            {"messageId": "msg-1"},
            {"messageId": "msg-2"},
        ]
    }

    response = consumer_lambda_handler(event, mock_context)

    mock_extract_correlation_id.assert_called_once_with(event["Records"])
    mock_setup_context.assert_called_once_with(
        "test-correlation-id", mock_context, mock_setup_context.call_args[0][2]
    )

    assert str(mock_process_message.call_count) == "2"
    mock_process_message.assert_any_call({"messageId": "msg-1"})
    mock_process_message.assert_any_call({"messageId": "msg-2"})

    assert response == {"batchItemFailures": []}


@pytest.mark.parametrize(
    ("event", "expected_result"),
    [
        (None, None),
        ({}, None),  # Empty dict is falsy, so returns None
        ({"Records": []}, {"batchItemFailures": []}),  # Has Records key, so processes
    ],
)
@patch("consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_no_event_data(
    mock_process_message: MagicMock, event: dict | None, expected_result: dict | None
) -> None:
    """Test handler when no event data or empty records are provided."""
    result = consumer_lambda_handler(event, {})
    assert result == expected_result
    assert str(mock_process_message.call_count) == "0"


@patch("consumer.consumer_handler.setup_request_context")
@patch("consumer.consumer_handler.extract_correlation_id_from_sqs_records")
@patch("consumer.consumer_handler.process_message_and_send_request")
def test_consumer_lambda_handler_partial_failure(
    mock_process_message: MagicMock,
    mock_extract_correlation_id: MagicMock,
    mock_setup_context: MagicMock,
) -> None:
    """Test handling of partial batch failures."""
    mock_extract_correlation_id.return_value = "test-correlation-id"
    event = {
        "Records": [
            {"messageId": "msg-1"},
            {"messageId": "msg-2"},
            {"messageId": "msg-3"},
        ]
    }

    # First and third messages fail, second succeeds
    mock_process_message.side_effect = [
        Exception("First failure"),
        None,
        Exception("Third failure"),
    ]

    response = consumer_lambda_handler(event, {})

    assert str(mock_process_message.call_count) == "3"

    # Test that failed items are correctly identified
    assert response == {
        "batchItemFailures": [{"itemIdentifier": "msg-1"}, {"itemIdentifier": "msg-3"}]
    }


def test_consumer_lambda_handler_empty_records() -> None:
    """Test handler with empty Records list."""
    event = {"Records": []}

    result = consumer_lambda_handler(event, {})

    assert result == {"batchItemFailures": []}
