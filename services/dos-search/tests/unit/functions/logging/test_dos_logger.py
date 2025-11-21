from unittest.mock import call, patch

import pytest

from functions.logging.dos_logger import DosLogger


@pytest.fixture
def mock_dos_logger():
    with patch("functions.logging.dos_logger.dos_logger") as mock:
        yield mock


@pytest.fixture
def dos_logger():
    return DosLogger(service="dos-search")


class TestDosLogger:
    def test_clear_log_data(self, dos_logger):
        # Arrange
        dos_logger.info("test_message", log_data={"key": "value"})
        # Act
        dos_logger.clear_log_data()
        # Assert
        assert dos_logger._last_log_data == dict()

    def test_extract(self, dos_logger, event, log_data):
        # Arrange
        extract = dict(log_data)
        # Act
        result = dos_logger.extract(event)
        # Assert
        assert result == extract

    def test_extract_with_lower_case_headers(self, dos_logger, event, log_data):
        # Arrange
        test_headers = {
            "nhsd-request-id": "value"  # Lower case
        }
        formatted_event = event
        formatted_event["headers"].update(test_headers)

        extract = dict(log_data)
        extract["dos_nhsd_request_id"] = test_headers["nhsd-request-id"]
        # Act
        result = dos_logger.extract(formatted_event)
        # Assert
        assert result == extract

    def test_extract_one_time(self, dos_logger, event, details):
        # Arrange
        extract = dict(details)
        # Act
        result = dos_logger.extract_one_time(event)
        # Assert
        assert result == extract

    def test_log_with_level_persists_last_log_call(self, dos_logger, log_data):
        # Arrange
        # Act
        dos_logger.info("test_log_with_level_persists_last_log_call", log_data=log_data)
        # Assert
        assert dos_logger._last_log_data == log_data

    def test_log_override_keys(self, dos_logger, log_data):
        # Arrange
        # Act
        result = dos_logger.info(
            "test_log_with_level_persists_last_log_call",
            log_data=log_data,
            dos_message_category="METRICS",
        )
        # Assert
        assert result["dos_message_category"] == "METRICS"

    def test_log_with_no_log_data(self, dos_logger, log_data):
        # Arrange
        dos_logger.info("initial call to set log_data", log_data=log_data)
        # Act
        result = dos_logger.info("test_log_with_no_log_data")
        # Assert
        assert result == log_data

    def test_info_call(self, mock_dos_logger, log_data):
        # Arrange
        info_message = "test_info_call: testing info call"
        # Act
        mock_dos_logger.info(info_message, log_data=log_data)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.info(info_message, log_data=log_data),
            ]
        )

    def test_warning_call(self, mock_dos_logger, log_data):
        # Arrange
        warning_message = "test_warning_call: testing warning call"
        # Act
        mock_dos_logger.warning(warning_message, log_data=log_data)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.warning(warning_message, log_data=log_data),
            ]
        )

    def test_error_call(self, mock_dos_logger, log_data):
        # Arrange
        error_message = "test_error_call: testing error call"
        # Act
        mock_dos_logger.error(error_message, log_data=log_data)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.error(error_message, log_data=log_data),
            ]
        )

    def test_exception_call(self, mock_dos_logger, log_data):
        # Arrange
        exception_message = "test_exception_call: testing exception call"
        # Act
        mock_dos_logger.exception(exception_message, log_data=log_data)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.exception(exception_message, log_data=log_data),
            ]
        )
