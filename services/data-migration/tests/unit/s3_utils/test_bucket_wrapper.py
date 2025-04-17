import io
import logging
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from pytest import LogCaptureFixture

from pipeline.s3_utils.s3_bucket_wrapper import BucketWrapper


@pytest.fixture
def bucket_wrapper() -> BucketWrapper:
    with patch("boto3.client") as mock_s3_client:
        mock_client = MagicMock()
        mock_s3_client.return_value = mock_client
        return BucketWrapper("s3://test-bucket/test-key")


def test_s3_put_object_logs_exception_on_failure(
    bucket_wrapper: BucketWrapper, caplog: LogCaptureFixture
) -> None:
    bucket_wrapper.s3_client.put_object.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="PutObject",
    )
    bucket_wrapper.s3_put_object(b"test data")
    assert "Failed to put object test-key to bucket test-bucket" in caplog.text


def test_s3_get_object_returns_none_on_failure(
    bucket_wrapper: BucketWrapper, caplog: LogCaptureFixture
) -> None:
    bucket_wrapper.s3_client.get_object.side_effect = ClientError(
        error_response={"Error": {"Code": "404", "Message": "Not Found"}},
        operation_name="GetObject",
    )
    result = bucket_wrapper.s3_get_object()
    assert result is None
    assert "Failed to get object test-key from bucket test-bucket" in caplog.text


def test_s3_delete_object_logs_success_on_deletion(
    bucket_wrapper: BucketWrapper, caplog: LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    bucket_wrapper.s3_client.delete_object.return_value = None
    bucket_wrapper.s3_delete_object()
    assert "Deleted object test-key from bucket test-bucket" in caplog.text


def test_s3_delete_object_logs_exception_on_failure(
    bucket_wrapper: BucketWrapper, caplog: LogCaptureFixture
) -> None:
    bucket_wrapper.s3_client.delete_object.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="DeleteObject",
    )
    bucket_wrapper.s3_delete_object()
    assert "Failed to delete object test-key from bucket test-bucket" in caplog.text


def test_s3_upload_file_logs_success_on_upload(
    bucket_wrapper: BucketWrapper, caplog: LogCaptureFixture
) -> None:
    caplog.set_level(logging.INFO)
    buffer = io.BytesIO(b"test data")
    bucket_wrapper.s3_client.upload_fileobj.return_value = None
    bucket_wrapper.s3_upload_file(buffer, "test-file.txt")
    assert "Uploaded file test-file.txt to bucket test-bucket" in caplog.text


def test_s3_upload_file_logs_exception_on_failure(
    bucket_wrapper: BucketWrapper, caplog: LogCaptureFixture
) -> None:
    buffer = io.BytesIO(b"test data")
    bucket_wrapper.s3_client.upload_fileobj.side_effect = ClientError(
        error_response={"Error": {"Code": "500", "Message": "Internal Server Error"}},
        operation_name="UploadFile",
    )
    bucket_wrapper.s3_upload_file(buffer, "test-file.txt")
    assert "Failed to upload file test-file.txt to bucket test-bucket" in caplog.text
