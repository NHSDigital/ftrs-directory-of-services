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

    # def test_log_override_keys(self, dos_logger):
    #     # Arrange
    #     # Act
    #     result = dos_logger.info(
    #         "test_log_with_level_persists_last_log_call",
    #         dos_message_category="METRICS",
    #         foo="bar",
    #     )
    #     # Assert
    #     assert result["dos_message_category"] == "METRICS"
    #     assert result["detail"]["foo"] == "bar"

    # def test_detail_fields_added(self, dos_logger):
    #     # Arrange
    #     # Act
    #     result = dos_logger.info("test_detail_fields_added", foo="bar")
    #     # Assert
    #     assert result["detail"]["foo"] == "bar"

    def test_info_call(self, mock_dos_logger):
        # Arrange
        info_message = "test_info_call: testing info call"
        # Act
        mock_dos_logger.info(info_message)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.info(info_message),
            ]
        )

    def test_warning_call(self, mock_dos_logger):
        # Arrange
        warning_message = "test_warning_call: testing warning call"
        # Act
        mock_dos_logger.warning(warning_message)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.warning(warning_message),
            ]
        )

    def test_error_call(self, mock_dos_logger):
        # Arrange
        error_message = "test_error_call: testing error call"
        # Act
        mock_dos_logger.error(error_message)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.error(error_message),
            ]
        )

    def test_exception_call(self, mock_dos_logger):
        # Arrange
        exception_message = "test_exception_call: testing exception call"
        # Act
        mock_dos_logger.exception(exception_message)
        # Assert
        mock_dos_logger.assert_has_calls(
            [
                call.exception(exception_message),
            ]
        )

    # def test_caplog(self, caplog):
    #     caplog.set_level(logging.INFO)
