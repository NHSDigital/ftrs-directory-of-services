import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture

from pipeline.sqs_sender import (
    get_queue_name,
    get_queue_url,
    load_data,
    send_messages_to_queue,
)

EXPECTED_BATCH_COUNT = 3


def test_get_queue_name_without_workspace() -> None:
    """Test queue name generation without workspace"""
    result = get_queue_name("test", None, "queue")
    expected = "ftrs-dos-test-etl-ods-queue"
    assert result == expected


def test_get_queue_name_with_workspace() -> None:
    """Test queue name generation with workspace"""
    result = get_queue_name("test", "branch", "queue")
    expected = "ftrs-dos-test-etl-ods-queue-branch"
    assert result == expected


def test_get_queue_name_with_custom_suffix() -> None:
    """Test queue name generation with custom suffix"""
    result = get_queue_name("test", "branch", "transform")
    expected = "ftrs-dos-test-etl-ods-transform-branch"
    assert result == expected


def test_send_messages_to_queue_successful(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful message sending to SQS with custom suffix"""
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "local"},
    ):
        with patch("boto3.client") as mock_boto_client:
            mock_sqs = MagicMock()
            mock_boto_client.return_value = mock_sqs
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-transform-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            test_messages = [{"test": "message1"}]

            with patch(
                "pipeline.sqs_sender.get_correlation_id", return_value="corr-123"
            ):
                send_messages_to_queue(test_messages, queue_suffix="transform")

            mock_boto_client.assert_called_once_with("sqs", region_name="local")
            mock_sqs.get_queue_url.assert_called_once_with(
                QueueName="ftrs-dos-test-etl-ods-transform-local"
            )

            expected_batch = [
                {"Id": "1", "MessageBody": json.dumps({"test": "message1"})},
            ]
            mock_sqs.send_message_batch.assert_called_once_with(
                QueueUrl="https://sqs.region.amazonaws.com/test-transform-queue",
                Entries=expected_batch,
            )


def test_send_messages_to_queue_with_failed_messages(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test message sending with some failed messages"""
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "local"},
    ):
        mock_sqs = MagicMock()
        mock_sqs.get_queue_url.return_value = {
            "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
        }
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": "1"}],
            "Failed": [{"Id": "2", "Code": "Error", "Message": "Failed to send"}],
        }

        mocker.patch("boto3.client", return_value=mock_sqs)
        mocker.patch("pipeline.sqs_sender.get_correlation_id", return_value="corr-123")

        test_messages = [{"test": "message1"}, {"test": "message2"}]

        send_messages_to_queue(test_messages, queue_suffix="queue")


def test_send_messages_to_queue_batching(mocker: MockerFixture) -> None:
    """Test message sending handles batching correctly"""
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "local"},
    ):
        mock_sqs = MagicMock()
        mock_sqs.get_queue_url.return_value = {
            "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
        }
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": str(i)} for i in range(1, 11)],
            "Failed": [],
        }

        mocker.patch("boto3.client", return_value=mock_sqs)
        mocker.patch("pipeline.sqs_sender.get_correlation_id", return_value="corr-123")

        # Send 25 messages to test batching (should result in 3 batches: 10, 10, 5)
        test_messages = [{"test": f"message{i}"} for i in range(25)]

        send_messages_to_queue(test_messages, queue_suffix="queue", batch_size=10)

        # Should be called 3 times for batching
        assert mock_sqs.send_message_batch.call_count == EXPECTED_BATCH_COUNT


def test_send_messages_to_queue_string_messages(mocker: MockerFixture) -> None:
    """Test sending string messages to queue"""
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "local"},
    ):
        mock_sqs = MagicMock()
        mock_sqs.get_queue_url.return_value = {
            "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
        }
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": "1"}],
            "Failed": [],
        }

        mocker.patch("boto3.client", return_value=mock_sqs)
        mocker.patch("pipeline.sqs_sender.get_correlation_id", return_value="corr-123")

        test_messages = ["string_message1"]
        send_messages_to_queue(test_messages, queue_suffix="queue")

        expected_batch = [
            {"Id": "1", "MessageBody": "string_message1"},
        ]
        mock_sqs.send_message_batch.assert_called_once_with(
            QueueUrl="https://sqs.region.amazonaws.com/test-queue",
            Entries=expected_batch,
        )


def test_load_data_successful(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful data loading to SQS"""
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "local"},
    ):
        with patch("boto3.client") as mock_boto_client:
            mock_sqs = MagicMock()
            mock_boto_client.return_value = mock_sqs
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            test_data = ["message1"]

            with patch(
                "pipeline.sqs_sender.get_correlation_id", return_value="corr-123"
            ):
                load_data(test_data)

            mock_boto_client.assert_called_once_with("sqs", region_name="local")
            mock_sqs.get_queue_url.assert_called_once_with(
                QueueName="ftrs-dos-test-etl-ods-queue-local"
            )

            expected_batch = [
                {"Id": "1", "MessageBody": "message1"},
            ]
            mock_sqs.send_message_batch.assert_called_once_with(
                QueueUrl="https://sqs.region.amazonaws.com/test-queue",
                Entries=expected_batch,
            )

            expected_try_log = (
                OdsETLPipelineLogBase.ETL_EXTRACTOR_014.value.message.format(number=1)
            )
            assert expected_try_log in caplog.text


def test_load_data_backward_compatibility(mocker: MockerFixture) -> None:
    """Test that load_data still works for backward compatibility"""
    mock_send = mocker.patch("pipeline.sqs_sender.send_messages_to_queue")

    test_data = ["message1", "message2"]
    load_data(test_data)

    mock_send.assert_called_once_with(test_data, queue_suffix="queue")


def test_get_queue_url_exception(mocker: MockerFixture) -> None:
    """Test get_queue_url handles exceptions"""
    mock_sqs = MagicMock()
    mock_sqs.get_queue_url.side_effect = ClientError(
        {"Error": {"Code": "QueueDoesNotExist", "Message": "Queue not found"}},
        "GetQueueUrl",
    )

    with pytest.raises(ClientError):
        get_queue_url("nonexistent-queue", mock_sqs)


# def test_send_messages_to_queue_empty_list() -> None:
#     """Test send_messages_to_queue with empty message list"""
#     # Mock all the AWS dependencies to avoid real calls
#     with patch.dict(
#         "os.environ",
#         {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "test-workspace"},
#     ):
#         with patch("pipeline.sqs_sender.get_correlation_id", return_value="test-correlation"):
#             with patch("boto3.client") as mock_boto_client:
#                 mock_sqs = MagicMock()
#                 mock_boto_client.return_value = mock_sqs

#                 # Empty list should return early without making any AWS calls
#                 result = send_messages_to_queue([])
#                 assert result is None

#                 # Verify no AWS calls were made
#                 mock_boto_client.assert_not_called()
#                 mock_sqs.get_queue_url.assert_not_called()
#                 mock_sqs.send_message_batch.assert_not_called()


def test_get_queue_name_edge_cases() -> None:
    """Test queue name generation edge cases"""
    # Test with None workspace
    result = get_queue_name("prod", None, "queue")
    expected = "ftrs-dos-prod-etl-ods-queue"
    assert result == expected

    # Test with empty string workspace
    result = get_queue_name("prod", "", "queue")
    expected = "ftrs-dos-prod-etl-ods-queue"
    assert result == expected
