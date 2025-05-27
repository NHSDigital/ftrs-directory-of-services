import json
import unittest
from unittest.mock import MagicMock, call, patch

import pytest
from botocore.exceptions import ClientError

from pipeline.load_data import get_queue_name, load_data


class TestLoad(unittest.TestCase):
    def test_get_queue_name_without_workspace(self) -> None:
        """Test queue name generation without workspace"""
        result = get_queue_name("test", None)
        expected = "ftrs-dos-test-etl-ods-queue"
        assert result == expected

    def test_get_queue_name_with_workspace(self) -> None:
        """Test queue name generation with workspace"""
        result = get_queue_name("test", "branch")
        expected = "ftrs-dos-test-etl-ods-queue-branch"
        assert result == expected

    @patch("logging.info")
    def test_load_data_successful(self, mock_info: any) -> None:
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
                load_data(test_data)

                mock_boto_client.assert_called_once_with("sqs", region_name="local")
                mock_sqs.get_queue_url.assert_called_once_with(
                    QueueName="ftrs-dos-test-etl-ods-queue-local"
                )
                expected_batch = [
                    {"Id": "1", "MessageBody": json.dumps("message1")},
                ]
                mock_sqs.send_message_batch.assert_called_once_with(
                    QueueUrl="https://sqs.region.amazonaws.com/test-queue",
                    Entries=expected_batch,
                )
                mock_info.assert_has_calls(
                    [
                        call("Trying to send 1 messages to sqs queue"),
                        call("Succeeded to send 1 messages in batch"),
                    ]
                )

    @patch("logging.info")
    @patch("logging.warning")
    def test_load_data_with_failed_messages(
        self, mock_warning: any, mock_info: any
    ) -> None:
        """Test data loading with some failed messages"""
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
                    "Failed": [
                        {
                            "Id": "2",
                            "Message": "Invalid message format",
                            "Code": "InvalidParameterValue",
                        }
                    ],
                }

                test_data = ["message1", "message2"]
                load_data(test_data)

                mock_warning.assert_has_calls(
                    [
                        call("Failed to send 1 messages in batch"),
                        call(
                            "  Message 2: Invalid message format - InvalidParameterValue"
                        ),
                    ]
                )
                mock_info.assert_any_call("Succeeded to send 1 messages in batch")

    @patch("logging.warning")
    def test_load_data_get_queue_url_exception(self, mock_warning: any) -> None:
        """Test exception handling when getting queue URL fails"""
        with patch.dict(
            "os.environ",
            {"ENVIRONMENT": "test", "AWS_REGION": "local", "WORKSPACE": "local"},
        ):
            with patch("boto3.client") as mock_boto_client:
                mock_sqs = MagicMock()
                mock_boto_client.return_value = mock_sqs

                mock_sqs.get_queue_url.side_effect = ClientError(
                    error_response={
                        "Error": {
                            "Code": "QueueDoesNotExist",
                            "Message": "Queue not found",
                        }
                    },
                    operation_name="GetQueueUrl",
                )
                test_data = ["message1"]

                with pytest.raises(Exception):
                    load_data(test_data)

                warning_call = mock_warning.call_args[0][0]
                self.assertIn(
                    "Error sending data to queue with error",
                    warning_call,
                )
