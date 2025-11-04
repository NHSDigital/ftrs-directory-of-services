import pytest

from functions.ftrs_logger import FtrsLogger


@pytest.fixture
def ftrs_logger():
    return FtrsLogger()


class TestFtrsLogger:
    def test_normalise_headers(self, ftrs_logger):
        # Arrange
        headers = {
            "header": "foo",
            "CapitalHeader": "bar",
        }

        # Act
        result = ftrs_logger._normalize_headers(headers)
        # Assert
        assert result["header"] == "foo"
        assert result["capitalheader"] == "bar"

    def test_normalise_no_headers(self, ftrs_logger):
        # Arrange
        headers = {}

        # Act
        result = ftrs_logger._normalize_headers(headers)
        # Assert
        assert isinstance(result, dict)

    def test_get_powertools_metadata(self, ftrs_logger):
        # Arrange
        metadata = {
            "function_name": "FTRS_LOG_PLACEHOLDER",
            "function_memory_size": "FTRS_LOG_PLACEHOLDER",
            "function_arn": "FTRS_LOG_PLACEHOLDER",
            "function_request_id": "FTRS_LOG_PLACEHOLDER",
            "correlation_id": "FTRS_LOG_PLACEHOLDER",
            "xray_trace_id": "FTRS_LOG_PLACEHOLDER",
            "level": "TBC",
        }
        # Act
        result = ftrs_logger.get_powertools_metadata()
        # Assert
        print(result)
        for key, value in metadata.items():
            assert result[key] == value
        assert isinstance(result["timestamp"], str)
        assert isinstance(result["location"], str)
