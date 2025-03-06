from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pipeline.load import load, main


def test_load(mocker: MockerFixture) -> None:
    """
    Test that load logs the input path and an error message
    """
    mock_logging_info = mocker.patch("pipeline.load.logging.info")
    mock_logging_error = mocker.patch("pipeline.load.logging.error")

    load("test_db_uri", Path("test_input_path"))

    mock_logging_info.assert_called_once_with("Loading data from test_input_path")
    mock_logging_error.assert_called_once_with("Not implemented yet")


def test_main_parses_args(mocker: MockerFixture) -> None:
    """
    Test that main parses command line arguments and calls load with the correct arguments
    """
    load_mock = mocker.patch("pipeline.load.load")
    args = ["--input-path", "test_input_path", "--db-uri", "test_db_uri"]

    main(args)

    assert load_mock.called is True
    assert load_mock.call_args[0][0] == "test_db_uri"
    assert load_mock.call_args[0][1] == Path("test_input_path")


def test_main_throws_error_on_no_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when no arguments are provided
    """
    expected_exit_code = 2

    load_mock = mocker.patch("pipeline.load.load")
    args = [""]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert load_mock.called is False


def test_main_throws_error_on_missing_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when required arguments are missing
    """
    expected_exit_code = 2

    load_mock = mocker.patch("pipeline.load.load")
    args = ["--db-uri", "test_db_uri"]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert load_mock.called is False


def test_main_throws_error_on_invalid_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when invalid arguments are provided
    """
    expected_exit_code = 2

    load_mock = mocker.patch("pipeline.load.load")
    args = [
        "--input-path",
        "test_input_path",
        "--db-uri",
        "test_db_uri",
        "--invalid-arg",
    ]
    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert load_mock.called is False
