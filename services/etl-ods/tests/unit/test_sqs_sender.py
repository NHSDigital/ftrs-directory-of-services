import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture

from common.sqs_sender import (
    _send_batch_to_sqs,
    get_queue_name,
    get_queue_url,
    send_messages_to_queue,
)


@pytest.fixture(scope="module")
def test_environment() -> dict:
    """File-scoped fixture for standard test environment variables."""
    return {
        "ENVIRONMENT": "test",
        "AWS_REGION": "local",
        "WORKSPACE": "local",
    }


@pytest.fixture(scope="module")
def mock_sqs_client() -> MagicMock:
    """File-scoped fixture for mock SQS client."""
    mock_client = MagicMock()
    mock_client.get_queue_url.return_value = {"QueueUrl": "https://sqs.test.queue.url"}
    mock_client.send_message_batch.return_value = {
        "Successful": [{"Id": "1"}],
        "Failed": [],
    }
    return mock_client


@pytest.fixture(scope="module")
def sample_sqs_record() -> dict:
    """File-scoped fixture for a sample SQS record."""
    return {
        "messageId": "test-msg-123",
        "body": json.dumps({"test": "data"}),
        "messageAttributes": {
            "testAttribute": {
                "stringValue": "testValue",
                "dataType": "String",
            }
        },
    }


class TestGetQueueName:
    """Test get_queue_name function."""

    @pytest.mark.parametrize(
        "env,workspace,suffix,expected",
        [
            ("test", None, "queue", "ftrs-dos-test-etl-ods-queue"),
            ("test", "branch", "queue", "ftrs-dos-test-etl-ods-queue-branch"),
            ("test", "branch", "transform", "ftrs-dos-test-etl-ods-transform-branch"),
            ("prod", "", "queue", "ftrs-dos-prod-etl-ods-queue"),
            ("dev", None, "extraction", "ftrs-dos-dev-etl-ods-extraction"),
            (
                "prod",
                "feature",
                "transform-dlq",
                "ftrs-dos-prod-etl-ods-transform-dlq-feature",
            ),
        ],
    )
    def test_queue_name_generation(
        self, env: str, workspace: str, suffix: str, expected: str
    ) -> None:
        """Test queue name generation with various environment configurations."""
        result = get_queue_name(env, workspace, suffix)
        assert result == expected

    def test_queue_name_with_empty_string_workspace(self) -> None:
        """Test that empty string workspace is treated as None."""
        result = get_queue_name("test", "", "queue")
        assert result == "ftrs-dos-test-etl-ods-queue"

    def test_queue_name_with_dlq_suffix(self) -> None:
        """Test queue name generation with DLQ suffix."""
        result = get_queue_name("prod", "main", "extraction-dlq")
        assert result == "ftrs-dos-prod-etl-ods-extraction-dlq-main"


class TestGetQueueUrl:
    """Test get_queue_url function."""

    def test_successful_queue_url_retrieval(self) -> None:
        """Test successful retrieval of queue URL."""
        mock_sqs = MagicMock()
        expected_url = "https://sqs.region.amazonaws.com/123456789/test-queue"
        mock_sqs.get_queue_url.return_value = {"QueueUrl": expected_url}

        result = get_queue_url("test-queue", mock_sqs)

        assert result["QueueUrl"] == expected_url
        mock_sqs.get_queue_url.assert_called_once_with(QueueName="test-queue")

    def test_queue_url_client_error(self, mocker: MockerFixture) -> None:
        """Test get_queue_url handles ClientError and logs."""
        mock_sqs = MagicMock()
        mock_sqs.get_queue_url.side_effect = ClientError(
            {"Error": {"Code": "QueueDoesNotExist", "Message": "Queue not found"}},
            "GetQueueUrl",
        )

        mock_logger = MagicMock()
        mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

        with pytest.raises(ClientError):
            get_queue_url("nonexistent-queue", mock_sqs)

        # Verify error was logged
        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_015,
            queue_name="nonexistent-queue",
            error_message="An error occurred (QueueDoesNotExist) when calling the GetQueueUrl operation: Queue not found",
        )

    def test_queue_url_generic_exception(self, mocker: MockerFixture) -> None:
        """Test get_queue_url handles generic exceptions."""
        mock_sqs = MagicMock()
        mock_sqs.get_queue_url.side_effect = Exception("Network error")

        mock_logger = MagicMock()
        mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

        with pytest.raises(Exception, match="Network error"):
            get_queue_url("test-queue", mock_sqs)

        mock_logger.log.assert_called_once()


class TestSendMessagesToQueue:
    """Test send_messages_to_queue function."""

    def test_empty_messages_returns_early(self) -> None:
        """Test that function returns early when no messages are provided."""
        # No mocking needed - function should return early without errors
        send_messages_to_queue([])

    def test_successful_message_sending(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test successful message sending to SQS queue."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            mocker.patch("boto3.client", return_value=mock_sqs)
            mocker.patch(
                "common.sqs_sender.get_correlation_id", return_value="corr-123"
            )

            test_messages = [{"test": "message1"}]
            send_messages_to_queue(test_messages)

            mock_sqs.get_queue_url.assert_called_once_with(
                QueueName="ftrs-dos-test-etl-ods-queue-local"
            )
            expected_batch = [
                {"Id": "1", "MessageBody": json.dumps({"test": "message1"})},
            ]
            mock_sqs.send_message_batch.assert_called_once_with(
                QueueUrl="https://sqs.region.amazonaws.com/test-queue",
                Entries=expected_batch,
            )

    def test_sending_string_messages(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test sending string messages (not dicts) to queue."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            mocker.patch("boto3.client", return_value=mock_sqs)

            test_messages = ["string_message1"]
            send_messages_to_queue(test_messages)

            expected_batch = [
                {"Id": "1", "MessageBody": "string_message1"},
            ]
            mock_sqs.send_message_batch.assert_called_once_with(
                QueueUrl="https://sqs.region.amazonaws.com/test-queue",
                Entries=expected_batch,
            )

    def test_message_batching(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test that messages are sent in batches of specified size."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": str(i)} for i in range(1, 11)],
                "Failed": [],
            }

            mocker.patch("boto3.client", return_value=mock_sqs)

            test_messages = [{"test": f"message{i}"} for i in range(25)]
            send_messages_to_queue(test_messages, batch_size=10)

            # 25 messages with batch size 10 = 3 batches
            assert str(mock_sqs.send_message_batch.call_count) == "3"

    def test_with_failed_messages(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test handling of failed messages in batch."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [{"Id": "2", "Code": "Error", "Message": "Failed to send"}],
            }

            mock_logger = MagicMock()
            mocker.patch("boto3.client", return_value=mock_sqs)
            mocker.patch(
                "common.sqs_sender.get_correlation_id", return_value="corr-123"
            )
            mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

            test_messages = [{"test": "message1"}, {"test": "message2"}]
            send_messages_to_queue(test_messages)

            mock_logger.log.assert_any_call(
                OdsETLPipelineLogBase.ETL_COMMON_017,
                failed=1,
                batch_range="1-2",
            )
            mock_logger.log.assert_any_call(
                OdsETLPipelineLogBase.ETL_COMMON_018,
                id="2",
                message="Failed to send",
                code="Error",
            )

    def test_without_correlation_id(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test message sending when correlation_id is None."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            mock_logger = MagicMock()
            mocker.patch("boto3.client", return_value=mock_sqs)
            mocker.patch("common.sqs_sender.get_correlation_id", return_value=None)
            mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

            test_messages = [{"test": "message1"}]
            send_messages_to_queue(test_messages)

            # Should not call append_keys when correlation_id is None
            mock_logger.append_keys.assert_not_called()
            # But should still process messages
            mock_sqs.send_message_batch.assert_called_once()

    def test_without_workspace_environment(self, mocker: MockerFixture) -> None:
        """Test queue name generation when WORKSPACE env var is not set."""
        env_without_workspace = {
            "ENVIRONMENT": "test",
            "AWS_REGION": "local",
        }

        with patch.dict("os.environ", env_without_workspace, clear=True):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/test-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            mocker.patch("boto3.client", return_value=mock_sqs)

            send_messages_to_queue([{"test": "message1"}])

            mock_sqs.get_queue_url.assert_called_once_with(
                QueueName="ftrs-dos-test-etl-ods-queue"
            )

    def test_exception_handling(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test exception handling and logging."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.side_effect = Exception("SQS connection failed")

            mock_logger = MagicMock()
            mocker.patch("boto3.client", return_value=mock_sqs)
            mocker.patch(
                "common.sqs_sender.get_correlation_id", return_value="corr-123"
            )
            mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

            test_messages = [{"test": "message1"}]

            with pytest.raises(Exception, match="SQS connection failed"):
                send_messages_to_queue(test_messages)

            mock_logger.log.assert_called_with(
                OdsETLPipelineLogBase.ETL_COMMON_020,
                error_message="SQS connection failed",
            )

    def test_custom_queue_suffix(
        self, mocker: MockerFixture, test_environment: dict
    ) -> None:
        """Test sending messages with custom queue suffix."""
        with patch.dict("os.environ", test_environment):
            mock_sqs = MagicMock()
            mock_sqs.get_queue_url.return_value = {
                "QueueUrl": "https://sqs.region.amazonaws.com/custom-queue"
            }
            mock_sqs.send_message_batch.return_value = {
                "Successful": [{"Id": "1"}],
                "Failed": [],
            }

            mocker.patch("boto3.client", return_value=mock_sqs)

            test_messages = [{"test": "message1"}]
            send_messages_to_queue(test_messages, queue_suffix="extraction")

            mock_sqs.get_queue_url.assert_called_once_with(
                QueueName="ftrs-dos-test-etl-ods-extraction-local"
            )


class TestSendBatchToSqs:
    """Test _send_batch_to_sqs function."""

    def test_successful_batch_send_with_logging(self, mocker: MockerFixture) -> None:
        """Test _send_batch_to_sqs logs correctly for successful sends."""
        mock_sqs = MagicMock()
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": "1"}, {"Id": "2"}],
            "Failed": [],
        }

        mock_logger = MagicMock()
        mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

        batch = [{"test": "message1"}, {"test": "message2"}]
        _send_batch_to_sqs(mock_sqs, "test-queue-url", batch, (1, 2, 10))

        # Check sending log
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_016,
            number=2,
            batch_range="1-2",
            remaining=8,
        )

        # Check success log
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_019,
            successful=2,
            batch_range="1-2",
            remaining=8,
        )

    def test_batch_with_failures(self, mocker: MockerFixture) -> None:
        """Test _send_batch_to_sqs handles failed messages."""
        mock_sqs = MagicMock()
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": "1"}],
            "Failed": [
                {
                    "Id": "2",
                    "Code": "InvalidMessageContents",
                    "Message": "Invalid message",
                },
                {
                    "Id": "3",
                    "Code": "ServiceUnavailable",
                    "Message": "Service unavailable",
                },
            ],
        }

        mock_logger = MagicMock()
        mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

        batch = [{"test": f"message{i}"} for i in range(1, 4)]
        _send_batch_to_sqs(mock_sqs, "test-queue-url", batch, (1, 3, 3))

        # Check failure log
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_017,
            failed=2,
            batch_range="1-3",
        )

        # Check individual failure logs
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_018,
            id="2",
            message="Invalid message",
            code="InvalidMessageContents",
        )
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_018,
            id="3",
            message="Service unavailable",
            code="ServiceUnavailable",
        )

    def test_batch_formats_string_messages_correctly(
        self, mocker: MockerFixture
    ) -> None:
        """Test that string messages are not JSON-encoded again."""
        mock_sqs = MagicMock()
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": "1"}],
            "Failed": [],
        }

        mocker.patch("common.sqs_sender.ods_extractor_logger", MagicMock())

        batch = ["raw_string_message"]
        _send_batch_to_sqs(mock_sqs, "test-queue-url", batch, (1, 1, 1))

        # Verify the call
        call_args = mock_sqs.send_message_batch.call_args
        entries = call_args[1]["Entries"]
        assert entries[0]["MessageBody"] == "raw_string_message"

    def test_batch_formats_dict_messages_as_json(self, mocker: MockerFixture) -> None:
        """Test that dict messages are JSON-encoded."""
        mock_sqs = MagicMock()
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": "1"}],
            "Failed": [],
        }

        mocker.patch("common.sqs_sender.ods_extractor_logger", MagicMock())

        batch = [{"key": "value"}]
        _send_batch_to_sqs(mock_sqs, "test-queue-url", batch, (1, 1, 1))

        # Verify the call
        call_args = mock_sqs.send_message_batch.call_args
        entries = call_args[1]["Entries"]
        assert entries[0]["MessageBody"] == json.dumps({"key": "value"})

    def test_batch_info_calculations(self, mocker: MockerFixture) -> None:
        """Test that batch info (start, end, remaining) is calculated correctly."""
        mock_sqs = MagicMock()
        mock_sqs.send_message_batch.return_value = {
            "Successful": [{"Id": str(i)} for i in range(11, 21)],
            "Failed": [],
        }

        mock_logger = MagicMock()
        mocker.patch("common.sqs_sender.ods_extractor_logger", mock_logger)

        batch = [{"test": f"message{i}"} for i in range(11, 21)]
        # Second batch: messages 11-20 out of 50 total
        _send_batch_to_sqs(mock_sqs, "test-queue-url", batch, (11, 20, 50))

        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_016,
            number=10,
            batch_range="11-20",
            remaining=30,
        )
