from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pipeline.extract import extract, main


def test_extract(mocker: MockerFixture) -> None:
    """
    Test that extract logs the output path and an error message
    """
    mock_logging_info = mocker.patch("pipeline.extract.logging.info")
    mock_logging_error = mocker.patch("pipeline.extract.logging.error")

    extract("test_db_uri", Path("test_output_path"))

    mock_logging_info.assert_called_once_with("Extracting data to test_output_path")
    mock_logging_error.assert_called_once_with("Not implemented yet")


def test_main_parses_args(mocker: MockerFixture) -> None:
    """
    Test that main parses command line arguments and calls extract with the correct arguments
    """
    extract_mock = mocker.patch("pipeline.extract.extract")
    args = ["--db-uri", "test_db_uri", "--output-path", "test_output_path"]

    main(args)

    assert extract_mock.called is True
    assert extract_mock.call_args[0][0] == "test_db_uri"
    assert extract_mock.call_args[0][1] == Path("test_output_path")


def test_main_throws_error_on_no_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when no arguments are provided
    """
    expected_exit_code = 2

    extract_mock = mocker.patch("pipeline.extract.extract")
    args = [""]

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert extract_mock.called is False


def test_main_throws_error_on_missing_args(mocker: MockerFixture) -> None:
    """
    Test that main throws an error when required arguments are missing
    """
    expected_exit_code = 2

    extract_mock = mocker.patch("pipeline.extract.extract")
    args = ["--output-path", "test_output_path"]

    with pytest.raises(SystemExit) as exc:
        main(args)

    assert exc.value.code == expected_exit_code
    assert extract_mock.called is False
