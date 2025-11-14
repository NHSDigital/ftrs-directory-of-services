from unittest.mock import call, patch

import pytest

from functions.ftrs_logger import FtrsLogger


@pytest.fixture
def mock_ftrs_logger():
    with patch("functions.ftrs_logger.ftrs_logger") as mock:
        yield mock


@pytest.fixture
def ftrs_logger():
    return FtrsLogger(service="dos-search")


class TestFtrsLogger:
    def test_clear_log_data(self, ftrs_logger):
        # Arrange
        ftrs_logger.info("test_message", log_data={"key": "value"})
        # Act
        ftrs_logger.clear_log_data()
        # Assert
        assert ftrs_logger._last_log_data == dict()

    def test_extract(self, ftrs_logger, event, log_data, details):
        # Arrange
        extract = log_data
        extract["details"] = details
        # Act
        result = ftrs_logger.extract(event)
        # Assert
        assert result == extract

    def test_extract_with_lower_case_headers(
        self, ftrs_logger, event, log_data, details
    ):
        # Arrange
        test_headers = {
            "nhsd-request-id": "value"  # Lower case
        }
        formatted_event = event
        formatted_event["headers"].update(test_headers)
        extract = log_data
        extract["ftrs_nhsd_request_id"] = test_headers["nhsd-request-id"]
        extract["details"] = details
        # Act
        result = ftrs_logger.extract(formatted_event)
        # Assert
        assert result == extract

    def test_log_with_level_persists_last_log_call(self, ftrs_logger, log_data):
        # Arrange
        # Act
        ftrs_logger.info(
            "test_log_with_level_persists_last_log_call", log_data=log_data
        )
        # Assert
        assert ftrs_logger._last_log_data == log_data

    def test_log_override_keys(self, ftrs_logger, log_data):
        # Arrange
        # Act
        result = ftrs_logger.info(
            "test_log_with_level_persists_last_log_call",
            log_data=log_data,
            ftrs_message_category="METRICS",
        )
        # Assert
        assert result["ftrs_message_category"] == "METRICS"

    def test_log_with_no_log_data(self, ftrs_logger, log_data):
        # Arrange
        ftrs_logger.info("initial call to set log_data", log_data=log_data)
        # Act
        result = ftrs_logger.info("test_log_with_no_log_data")
        # Assert
        assert result == log_data

    def test_info_call(self, mock_ftrs_logger, log_data):
        # Arrange
        info_message = "test_info_call: testing info call"
        # Act
        mock_ftrs_logger.info(info_message, log_data=log_data)
        # Assert
        mock_ftrs_logger.assert_has_calls(
            [
                call.info(info_message, log_data=log_data),
            ]
        )

    def test_warning_call(self, mock_ftrs_logger, log_data):
        # Arrange
        warning_message = "test_warning_call: testing warning call"
        # Act
        mock_ftrs_logger.warning(warning_message, log_data=log_data)
        # Assert
        mock_ftrs_logger.assert_has_calls(
            [
                call.warning(warning_message, log_data=log_data),
            ]
        )

    def test_error_call(self, mock_ftrs_logger, log_data):
        # Arrange
        error_message = "test_error_call: testing error call"
        # Act
        mock_ftrs_logger.error(error_message, log_data=log_data)
        # Assert
        mock_ftrs_logger.assert_has_calls(
            [
                call.error(error_message, log_data=log_data),
            ]
        )

    def test_exception_call(self, mock_ftrs_logger, log_data):
        # Arrange
        exception_message = "test_exception_call: testing exception call"
        # Act
        mock_ftrs_logger.exception(exception_message, log_data=log_data)
        # Assert
        mock_ftrs_logger.assert_has_calls(
            [
                call.exception(exception_message, log_data=log_data),
            ]
        )
