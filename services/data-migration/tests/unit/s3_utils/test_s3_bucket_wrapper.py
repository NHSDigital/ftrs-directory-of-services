from io import BytesIO
from unittest.mock import MagicMock, Mock

from botocore.exceptions import ClientError

from pipeline.s3_utils.s3_bucket_wrapper import BucketWrapper


def test_bucket_wrapper_init() -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    assert bucket_wrapper.bucket_name == "bucket-name"
    assert bucket_wrapper.bucket_key == "path/to/object"
    assert bucket_wrapper.s3_client is not None


def test_s3_bucket_exists() -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the head_bucket method to simulate a successful response
    bucket_wrapper.s3_client.head_bucket = MagicMock()

    assert bucket_wrapper.s3_bucket_exists() is True
    bucket_wrapper.s3_client.head_bucket.assert_called_once_with(Bucket="bucket-name")


def test_s3_bucket_exists_not_exists() -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the head_bucket method to simulate a failure
    bucket_wrapper.s3_client.head_bucket = lambda Bucket: (_ for _ in ()).throw(
        ClientError(
            {
                "Error": {
                    "Code": "NoSuchBucket",
                    "Message": "The specified bucket does not exist",
                }
            },
            "HeadBucket",
        )
    )

    assert bucket_wrapper.s3_bucket_exists() is False


def test_s3_put_object() -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the put_object method to simulate a successful response
    bucket_wrapper.s3_client.put_object = MagicMock()

    data_buffer = b"test data"
    bucket_wrapper.s3_put_object(data_buffer)

    bucket_wrapper.s3_client.put_object.assert_called_once_with(
        Bucket="bucket-name",
        Key="path/to/object",
        Body=data_buffer,
    )


def test_s3_put_object_failure(mock_logging: Mock) -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the put_object method to simulate a failure
    bucket_wrapper.s3_client.put_object = lambda **kwargs: (_ for _ in ()).throw(
        ClientError(
            {
                "Error": {
                    "Code": "InternalError",
                    "Message": "An internal error occurred",
                }
            },
            "PutObject",
        )
    )

    data_buffer = b"test data"
    bucket_wrapper.s3_put_object(data_buffer)

    mock_logging.exception.assert_called_once_with(
        "Failed to put object %s to bucket %s",
        "path/to/object",
        "bucket-name",
    )


def test_s3_get_object() -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the get_object method to simulate a successful response
    bucket_wrapper.s3_client.get_object = MagicMock(
        return_value={"Body": Mock(read=Mock(return_value=b"test data"))}
    )

    result = bucket_wrapper.s3_get_object()

    assert result == b"test data"
    bucket_wrapper.s3_client.get_object.assert_called_once_with(
        Bucket="bucket-name", Key="path/to/object"
    )


def test_s3_get_object_failure(mock_logging: Mock) -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the get_object method to simulate a failure
    bucket_wrapper.s3_client.get_object = lambda **kwargs: (_ for _ in ()).throw(
        ClientError(
            {
                "Error": {
                    "Code": "InternalError",
                    "Message": "An internal error occurred",
                }
            },
            "GetObject",
        )
    )

    result = bucket_wrapper.s3_get_object()

    assert result is None
    mock_logging.exception.assert_called_once_with(
        "Failed to get object %s from bucket %s",
        "path/to/object",
        "bucket-name",
    )


def test_s3_delete_object() -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the delete_object method to simulate a successful response
    bucket_wrapper.s3_client.delete_object = MagicMock()

    bucket_wrapper.s3_delete_object()

    bucket_wrapper.s3_client.delete_object.assert_called_once_with(
        Bucket="bucket-name", Key="path/to/object"
    )


def test_s3_delete_object_failure(mock_logging: Mock) -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the delete_object method to simulate a failure
    bucket_wrapper.s3_client.delete_object = lambda **kwargs: (_ for _ in ()).throw(
        ClientError(
            {
                "Error": {
                    "Code": "InternalError",
                    "Message": "An internal error occurred",
                }
            },
            "DeleteObject",
        )
    )

    bucket_wrapper.s3_delete_object()

    mock_logging.exception.assert_called_once_with(
        "Failed to delete object %s from bucket %s",
        "path/to/object",
        "bucket-name",
    )


def test_s3_upload_file(mock_logging: Mock) -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the upload_file method to simulate a successful response
    bucket_wrapper.s3_client = MagicMock(upload_fileobj=MagicMock())

    file_bytes = BytesIO(b"local_file.txt")
    bucket_wrapper.s3_upload_file(file_bytes, "s3_object_key")

    bucket_wrapper.s3_client.upload_fileobj.assert_called_once_with(
        file_bytes,
        Bucket="bucket-name",
        Key="path/to/object/s3_object_key",
    )


def test_s3_upload_file_failure(mock_logging: Mock) -> None:
    s3_uri = "s3://bucket-name/path/to/object"
    bucket_wrapper = BucketWrapper(s3_uri)

    # Mock the upload_file method to simulate a failure
    bucket_wrapper.s3_client = MagicMock(
        upload_fileobj=MagicMock(
            side_effect=ClientError(
                {
                    "Error": {
                        "Code": "InternalError",
                        "Message": "An internal error occurred",
                    }
                },
                "UploadFile",
            )
        )
    )

    file_bytes = BytesIO(b"local_file.txt")
    bucket_wrapper.s3_upload_file(file_bytes, "s3_object_key")

    mock_logging.exception.assert_called_once_with(
        "Failed to upload file %s to bucket %s",
        "s3_object_key",
        "bucket-name",
    )
