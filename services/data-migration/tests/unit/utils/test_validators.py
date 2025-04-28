from pathlib import Path

import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture
from typer import BadParameter

from pipeline.utils.file_io import PathType
from pipeline.utils.validators import (
    check_bucket_access,
    validate_local_path,
    validate_path,
    validate_s3_uri,
)


def test_check_bucket_access_success(mocker: MockerFixture) -> None:
    """
    Test that check_bucket_access returns True when the bucket exists and is accessible.
    """
    mock_s3_client = mocker.patch("boto3.client")
    mock_s3_client.return_value.head_bucket.return_value = None

    assert check_bucket_access("test-bucket") is True
    mock_s3_client.return_value.head_bucket.assert_called_once_with(
        Bucket="test-bucket"
    )


def test_check_bucket_access_failure(mocker: MockerFixture) -> None:
    """
    Test that check_bucket_access returns False when the bucket does not exist or is inaccessible.
    """
    mock_s3_client = mocker.patch("boto3.client")
    mock_s3_client.return_value.head_bucket.side_effect = ClientError(
        error_response={"Error": {"Code": "404", "Message": "Not Found"}},
        operation_name="HeadBucket",
    )

    assert check_bucket_access("nonexistent-bucket") is False
    mock_s3_client.return_value.head_bucket.assert_called_once_with(
        Bucket="nonexistent-bucket"
    )


@pytest.mark.parametrize(
    "s3_uri, bucket_accessible, expected",
    [
        ("s3://valid-bucket/valid-key", True, "s3://valid-bucket/valid-key"),
        ("s3://invalid-bucket/valid-key", False, BadParameter),
        ("http://invalid-scheme/valid-key", False, False),
        ("s3://", False, BadParameter),
    ],
)
def test_validate_s3_uri(
    mocker: MockerFixture,
    s3_uri: str,
    bucket_accessible: bool | None,
    expected: str | BadParameter | bool,
) -> None:
    """
    Test validate_s3_uri with various scenarios.
    """
    mock_check_bucket_access = mocker.patch(
        "pipeline.utils.validators.check_bucket_access",
        return_value=bucket_accessible,
    )

    if expected == BadParameter:
        with pytest.raises(expected):
            validate_s3_uri(s3_uri)
    else:
        assert validate_s3_uri(s3_uri) == expected

    if bucket_accessible is not None:
        bucket_name = s3_uri.split("/")[2] if "s3://" in s3_uri else None
        if bucket_name:
            mock_check_bucket_access.assert_called_once_with(bucket_name)


@pytest.mark.parametrize(
    "path, parent_exists, expected",
    [
        ("/valid/path/file.txt", True, Path("/valid/path/file.txt")),
        ("/invalid/path/file.txt", False, BadParameter),
    ],
)
def test_validate_local_path(
    mocker: MockerFixture, path: str, parent_exists: bool, expected: Path | BadParameter
) -> None:
    """
    Test validate_local_path with various scenarios.
    """
    mock_path_exists = mocker.patch("pathlib.Path.exists", return_value=parent_exists)

    if expected == BadParameter:
        with pytest.raises(expected):
            validate_local_path(path)
    else:
        assert validate_local_path(path) == expected

    mock_path_exists.assert_called_once_with()


def test_validate_path_valid_local(mocker: MockerFixture) -> None:
    """
    Test validate_path with a valid local path.
    """
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.is_file", return_value=True)

    path_type, path = validate_path("/valid/local/path.txt")

    assert path_type == PathType.FILE
    assert path == Path("/valid/local/path.txt")


def test_validate_path_invalid_path(mocker: MockerFixture) -> None:
    """
    Test validate_path with an invalid path.
    """
    mocker.patch("pathlib.Path.exists", return_value=False)

    with pytest.raises(
        BadParameter,
        match="Parent directory does not exist: /invalid. Please provide a valid path.",
    ):
        validate_path("/invalid/path.txt")


def test_validate_path_valid_s3(mocker: MockerFixture) -> None:
    """
    Test validate_path with a valid S3 path.
    """
    mocker.patch("pipeline.utils.validators.check_bucket_access", return_value=True)

    path_type, path = validate_path("s3://valid-bucket/valid-key")

    assert path_type == PathType.S3
    assert path == "s3://valid-bucket/valid-key"


def test_validate_path_invalid_s3(mocker: MockerFixture) -> None:
    """
    Test validate_path with an invalid S3 path.
    """
    mocker.patch("pipeline.utils.validators.check_bucket_access", return_value=False)

    with pytest.raises(
        BadParameter,
        match="Invalid S3 URI: s3://invalid-bucket/valid-key. Please provide a valid S3 URI and confirm you have access to the S3 bucket.",
    ):
        validate_path("s3://invalid-bucket/valid-key")
