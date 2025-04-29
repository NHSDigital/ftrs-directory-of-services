from pathlib import Path
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture
from typer import BadParameter

from pipeline.utils.file_io import PathType
from pipeline.utils.validators import (
    check_bucket_access,
    check_object_exists,
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


def test_check_object_exists_success(mocker: MockerFixture) -> None:
    """
    Test that check_object_exists returns True when the object exists in the bucket.
    """
    mock_s3_client = mocker.patch("boto3.client")
    mock_s3_client.return_value.head_object.return_value = None

    assert check_object_exists("test-bucket", "test-object") is True
    mock_s3_client.return_value.head_object.assert_called_once_with(
        Bucket="test-bucket", Key="test-object"
    )


def test_check_object_exists_failure(mocker: MockerFixture) -> None:
    """
    Test that check_object_exists returns False when the object does not exist in the bucket.
    """
    mock_s3_client = mocker.patch("boto3.client")
    mock_s3_client.return_value.head_object.side_effect = ClientError(
        error_response={"Error": {"Code": "404", "Message": "Not Found"}},
        operation_name="HeadObject",
    )

    assert check_object_exists("test-bucket", "nonexistent-object") is False
    mock_s3_client.return_value.head_object.assert_called_once_with(
        Bucket="test-bucket", Key="nonexistent-object"
    )


@pytest.mark.parametrize(
    "s3_uri, bucket_accessible, object_exists, should_file_exist, expected_result, expected_error_text",
    [
        # Valid S3 URI with bucket and object accessible - file presence agnostic
        (
            "s3://valid-bucket/valid-key",
            True,
            True,
            None,
            "s3://valid-bucket/valid-key",
            None,
        ),
        # Valid S3 URI with bucket accessible but object not found - file presence agnostic
        (
            "s3://valid-bucket/valid-key",
            True,
            False,
            None,
            "s3://valid-bucket/valid-key",
            None,
        ),
        # Valid S3 URI with bucket and object accessible - file presence required
        (
            "s3://valid-bucket/valid-key",
            True,
            True,
            True,
            "s3://valid-bucket/valid-key",
            None,
        ),
        # Valid S3 URI with bucket accessible but object not found - file presence required
        (
            "s3://valid-bucket/valid-key",
            True,
            False,
            True,
            BadParameter,
            "File does not exist in S3: s3://valid-bucket/valid-key. Please provide a valid S3 URI to an existing file.",
        ),
        #
        # Invalid S3 URI (wrong scheme)
        (
            "http://invalid-bucket/valid-key",
            None,
            None,
            None,
            False,
            None,
        ),
        # Invalid S3 URI (missing bucket)
        (
            "s3://",
            None,
            None,
            None,
            BadParameter,
            "Invalid S3 URI: s3://. Please provide a valid S3 URI and confirm you have access to the S3 bucket.",
        ),
        # Invalid S3 URI (bucket not accessible)
        (
            "s3://invalid-bucket/valid-key",
            False,
            None,
            None,
            BadParameter,
            "Invalid S3 URI: s3://invalid-bucket/valid-key. Please provide a valid S3 URI and confirm you have access to the S3 bucket.",
        ),
        # Valid S3 URI (bucket accessible but object not found) - file presence required
        (
            "s3://valid-bucket/invalid-key",
            True,
            False,
            True,
            BadParameter,
            "File does not exist in S3: s3://valid-bucket/invalid-key. Please provide a valid S3 URI to an existing file.",
        ),
        # Valid S3 URI (bucket accessible but object found) - no file present required
        (
            "s3://valid-bucket/valid-key",
            True,
            True,
            False,
            BadParameter,
            "File already exists in S3: s3://valid-bucket/valid-key. Please provide a different S3 URI.",
        ),
    ],
)
def test_validate_s3_uri(  # noqa: PLR0913
    mocker: MockerFixture,
    s3_uri: str,
    bucket_accessible: bool | None,
    object_exists: bool | None,
    should_file_exist: bool | None,
    expected_result: str | BadParameter | bool,
    expected_error_text: str | None,
) -> None:
    """
    Test validate_s3_uri with various scenarios.
    """
    mock_check_bucket_access = mocker.patch(
        "pipeline.utils.validators.check_bucket_access",
        return_value=bucket_accessible,
    )
    mocker.patch(
        "pipeline.utils.validators.check_object_exists",
        return_value=object_exists,
    )

    if expected_result == BadParameter:
        with pytest.raises(expected_result, match=expected_error_text):
            validate_s3_uri(s3_uri, should_file_exist=should_file_exist)
    else:
        assert (
            validate_s3_uri(s3_uri, should_file_exist=should_file_exist)
            == expected_result
        )

    if bucket_accessible is not None:
        bucket_name = s3_uri.split("/")[2] if "s3://" in s3_uri else None
        if bucket_name:
            mock_check_bucket_access.assert_called_once_with(bucket_name)
        else:
            mock_check_bucket_access.assert_not_called()


@pytest.mark.parametrize(
    "path, parent_exists, file_exists, should_file_exist, expected_error_text",
    [
        # Valid path with file presence agnostic
        (
            "/valid/path/file.txt",
            True,
            True,
            None,
            None,
        ),
        # Valid path with file presence required
        (
            "/valid/path/file.txt",
            True,
            True,
            True,
            None,
        ),
        # Valid path with file not found - file presence agnostic
        (
            "/valid/path/file.txt",
            True,
            False,
            None,
            None,
        ),
        # Valid path with file not found - file presence required
        (
            "/valid/path/file.txt",
            True,
            False,
            True,
            "File does not exist: /valid/path/file.txt. Please provide a valid path to a file.",
        ),
        # Valid path with file found - no file presence required
        (
            "/valid/path/file.txt",
            True,
            True,
            False,
            "File already exists: /valid/path/file.txt. Please provide a different path.",
        ),
        # Valid path with parent directory not found
        (
            "/invalid/path/file.txt",
            False,
            False,
            None,
            "Parent directory does not exist: /invalid/path. Please provide a valid path to a file.",
        ),
        # Valid path with parent directory not found - file presence required
        (
            "/invalid/path/file.txt",
            False,
            False,
            True,
            "Parent directory does not exist: /invalid/path. Please provide a valid path to a file.",
        ),
        # Valid path with parent directory not found - no file presence required
        (
            "/invalid/path/file.txt",
            False,
            False,
            False,
            "Parent directory does not exist: /invalid/path. Please provide a valid path to a file.",
        ),
    ],
)
def test_validate_local_path(  # noqa: PLR0913
    mocker: MockerFixture,
    path: str,
    parent_exists: bool,
    file_exists: bool,
    should_file_exist: bool | None,
    expected_error_text: str | None,
) -> None:
    """
    Test validate_local_path with various scenarios.
    """
    mock_path = MagicMock(spec=Path)
    mock_path.__str__ = lambda *_: path
    mock_path.exists.return_value = file_exists
    mock_path.is_file.return_value = file_exists
    mock_path.parent.exists.return_value = parent_exists
    mock_path.parent.__str__ = lambda *_: str(Path(path).parent)

    mocker.patch("pipeline.utils.validators.Path", return_value=mock_path)

    if expected_error_text is not None:
        with pytest.raises(BadParameter, match=expected_error_text):
            validate_local_path(path, should_file_exist=should_file_exist)

    else:
        assert (
            validate_local_path(path, should_file_exist=should_file_exist) == mock_path
        )


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
