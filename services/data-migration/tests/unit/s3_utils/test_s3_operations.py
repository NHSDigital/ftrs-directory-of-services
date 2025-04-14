import pytest
from pytest_mock import MockerFixture

from pipeline.exceptions import InvalidS3URI
from pipeline.s3_utils.s3_operations import validate_s3_uri


def test_valid_s3_uri(mocker: MockerFixture) -> None:
    mock_bucket_wrapper = mocker.patch("pipeline.s3_utils.s3_operations.BucketWrapper")
    mock_bucket_wrapper.return_value.s3_bucket_exists.return_value = True
    uri = "s3://valid-bucket/path/to/object"
    result = validate_s3_uri(uri)
    assert result == uri


def test_invalid_s3_uri_prefix() -> None:
    uri = "http://invalid-bucket/path/to/object"
    with pytest.raises(InvalidS3URI):
        validate_s3_uri(uri)


def test_bucket_does_not_exist(mocker: MockerFixture) -> None:
    mock_bucket_wrapper = mocker.patch("pipeline.s3_utils.s3_operations.BucketWrapper")
    mock_bucket_wrapper.return_value.s3_bucket_exists.return_value = False
    uri = "s3://nonexistent-bucket/path/to/object"
    result = validate_s3_uri(uri)
    assert result is None
