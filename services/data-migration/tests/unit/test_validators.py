import pytest
from pytest_mock import MockerFixture

from pipeline.exceptions import ExtractArgsError
from pipeline.validators import validate_paths


@pytest.mark.parametrize(
    "function_args, expected_error_msg",
    [
        (
            # Using dictionary to meet linting requirements
            {
                "local_path": None,
                "s3_uri": None,
                "local_path_name": None,
                "s3_uri_name": None,
            },
            f"Either {None} or {None} must be provided.",
        ),
        (
            {
                "local_path": "abc",
                "s3_uri": "s3://bucket-name/path/to/object",
                "local_path_name": "local_path",
                "s3_uri_name": "s3_path",
            },
            "Either local_path or s3_path must be provided.",
        ),
        (
            {
                "local_path": "abc",
                "s3_uri": None,
                "local_path_name": "local_path",
                "s3_uri_name": "s3_path",
            },
            None,
        ),
        (
            {
                "local_path": None,
                "s3_uri": "s3://bucket-name/path/to/object",
                "local_path_name": "local_path",
                "s3_uri_name": "s3_path",
            },
            None,
        ),
    ],
)
def test_validate_paths(
    function_args: dict, expected_error_msg: bool, mocker: MockerFixture
) -> None:
    """
    Test that the paths, pass or fail according to our expectations
    """
    mocker.patch("pipeline.validators.validate_s3_uri", return_value=True)

    try:
        validate_paths(
            function_args["local_path"],
            function_args["s3_uri"],
            function_args["local_path_name"],
            function_args["s3_uri_name"],
        )
        assert expected_error_msg is None
    except ExtractArgsError as error:
        assert expected_error_msg == error.args[0]
    else:
        assert False


def test_validate_paths_invalid_s3_uri(mocker: MockerFixture) -> None:
    mocker.patch("pipeline.validators.validate_s3_uri", return_value=None)

    with pytest.raises(ExtractArgsError) as excinfo:
        validate_paths(None, "invalid_s3_uri", None, None)

    assert (
        str(excinfo.value)
        == "Invalid S3 URI: invalid_s3_uri. Please provide a valid S3 URI and confirm you have access to the S3 bucket."
    )
