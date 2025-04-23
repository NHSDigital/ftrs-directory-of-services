import pytest
from pytest_mock import MockerFixture
from typer import BadParameter

from pipeline.validators import validate_paths


@pytest.mark.parametrize(
    "function_args",
    [
        (
            # Using dictionary to meet linting requirements
            {"local_path": None, "s3_uri": None}
        ),
        ({"local_path": "abc", "s3_uri": "s3://bucket-name/path/to/object"}),
        ({"local_path": "abc", "s3_uri": None}),
        ({"local_path": None, "s3_uri": "s3://bucket-name/path/to/object"}),
    ],
)
def test_validate_paths(function_args: dict, mocker: MockerFixture) -> None:
    """
    Test that the paths, pass or fail according to our expectations
    """
    mocker.patch("pipeline.validators.validate_s3_uri", return_value=True)

    try:
        validate_paths(
            function_args["local_path"],
            function_args["s3_uri"],
        )
        assert True
    except BadParameter as error:
        assert "Either a local_path or s3_uri must be provided." == error.args[0]


def test_validate_paths_invalid_s3_uri(mocker: MockerFixture) -> None:
    mocker.patch("pipeline.validators.validate_s3_uri", return_value=None)

    with pytest.raises(BadParameter) as excinfo:
        validate_paths(None, "invalid_s3_uri")

    assert (
        str(excinfo.value)
        == "Invalid S3 URI: invalid_s3_uri. Please provide a valid S3 URI and confirm you have access to the S3 bucket."
    )
