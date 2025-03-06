from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pipeline.transform import main, transform


def test_load(mocker: MockerFixture) -> None:
    """
    Test that transform logs the input path and an error message
    """
    mock_logging_info = mocker.patch("pipeline.transform.logging.info")
    mock_logging_error = mocker.patch("pipeline.transform.logging.error")

    transform(Path("test_input_path"), Path("test_output_path"))

    mock_logging_info.assert_called_once_with(
        "Transforming data from test_input_path to test_output_path"
    )
    mock_logging_error.assert_called_once_with("Not implemented yet")


def test_main_parses_args(mocker: MockerFixture) -> None:
    """
    Test that main parses command line arguments and calls transform with the correct arguments
    """
    transform_mock = mocker.patch("pipeline.transform.transform")
    args = ["--input-path", "test_input_path", "--output-path", "test_output_path"]

    main(args)

    assert transform_mock.called is True
    assert transform_mock.call_args[0][0] == Path("test_input_path")
    assert transform_mock.call_args[0][1] == Path("test_output_path")


def test_main_throws_error_on_no_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when no arguments are provided
    """
    expected_exit_code = 2

    transform_mock = mocker.patch("pipeline.transform.transform")
    args = [""]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert transform_mock.called is False


def test_main_throws_error_on_missing_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when required arguments are missing
    """
    expected_exit_code = 2

    transform_mock = mocker.patch("pipeline.transform.transform")
    args = ["--output-path", "test_output_path"]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert transform_mock.called is False


def test_main_throws_error_on_invalid_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when invalid arguments are
    """
    expected_exit_code = 2

    transform_mock = mocker.patch("pipeline.transform.transform")
    args = [
        "--input-path",
        "test_input_path",
        "--output-path",
        "test_output_path",
        "--invalid-arg",
    ]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert transform_mock.called is False
