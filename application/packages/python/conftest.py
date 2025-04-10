from typing import Generator
from unittest.mock import patch

from ftrs_common.mocks.mock_logger import MockLogger
from pytest import fixture


@fixture()
def mock_logger() -> Generator[MockLogger, None, None]:
    """
    Fixture to provide a mock logger instance for testing.
    """
    with patch("ftrs_common.logger.Logger.get") as mock_get:
        mock_logger_instance = MockLogger(service="mock_logger")
        mock_get.return_value = mock_logger_instance
        yield mock_logger_instance
