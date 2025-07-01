import json
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.load_data import get_queue_name, load_data


def test_get_queue_name_without_workspace() -> None:
    """Test queue name generation without workspace"""
    result = get_queue_name("test", None)
    expected = "ftrs-dos-test-etl-ods-queue"
    assert result == expected


def test_get_queue_name_with_workspace() -> None:
    """Test queue name generation with workspace"""
    result = get_queue_name("test", "branch")
    expected = "ftrs-dos-test-etl-ods-queue-branch"
    assert result == expected


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
            expected_try_log = (
                OdsETLPipelineLogBase.ETL_PROCESSOR_014.value.message.format(number=1)
            )
            expected_success_log = (
                OdsETLPipelineLogBase.ETL_PROCESSOR_017.value.message.format(
                    successful=1
                )
            )
            assert expected_try_log in caplog.text
            assert expected_success_log in caplog.text


def test_load_data_with_failed_messages(
    caplog: pytest.LogCaptureFixture,
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
            expected_failed_log = (
                OdsETLPipelineLogBase.ETL_PROCESSOR_015.value.message.format(failed=1)
            )
            expected_invalid_log = (
                OdsETLPipelineLogBase.ETL_PROCESSOR_016.value.message.format(
                    id=2,
                    message="Invalid message format",
                    code="InvalidParameterValue",
                )
            )
            assert expected_failed_log in caplog.text
            assert expected_invalid_log in caplog.text


def test_load_data_get_queue_url_exception(caplog: pytest.LogCaptureFixture) -> None:
    """Test exception handling when getting queue URL fails"""
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
        expected_log_template = (
            OdsETLPipelineLogBase.ETL_PROCESSOR_018.value.message.split(
                "{error_message}"
            )[0]
        )
        assert expected_log_template in caplog.text
        assert "QueueDoesNotExist" in caplog.text
        assert "Queue not found" in caplog.text
