from typing import Generator
from unittest.mock import Mock, patch

from ftrs_common.logger import Logger
from pytest import fixture


class MockLogger(Logger):
    """
    A mock logger class for testing purposes.
    """

    def __init__(self, service: str = "test_service") -> None:
        super().__init__(service=service)
        self.logs = {
            "DEBUG": [],
            "INFO": [],
            "WARNING": [],
            "ERROR": [],
            "CRITICAL": [],
        }

        self.debug = Mock(side_effect=self._log("DEBUG"))
        self.info = Mock(side_effect=self._log("INFO"))
        self.warning = Mock(side_effect=self._log("WARNING"))
        self.error = Mock(side_effect=self._log("ERROR"))
        self.critical = Mock(side_effect=self._log("CRITICAL"))

    def _log(self, level: str) -> None:
        """
        Store logs in a list instead of logging them.
        """
        return lambda **kwargs: self.logs[level].append(kwargs)

    def get_logs(self, level: str | None = None) -> list[dict]:
        """
        Get logs for a specific level or all logs if no level is specified.
        """
        if level:
            assert level in self.logs, f"Invalid log level: {level}"
            return self.logs.get(level, [])
        return [log for level_logs in self.logs.values() for log in level_logs]

    def get_log_count(self, level: str | None = None) -> int:
        """
        Get the count of logs for a specific level or all logs if no level is specified.
        """
        if level:
            return len(self.logs.get(level, []))
        return sum(len(level_logs) for level_logs in self.logs.values())

    def clear_logs(self) -> None:
        """
        Clear the stored logs.
        """
        self.logs.clear()

    def get_log(self, log_reference: str, level: str | None = None) -> list[dict]:
        """
        Get logs for a specific log reference.
        """
        if level:
            assert level in self.logs, f"Invalid log level: {level}"
            return [
                log for log in self.logs[level] if log["reference"] == log_reference
            ]

        return [
            log
            for level_logs in self.logs.values()
            for log in level_logs
            if log["reference"] == log_reference
        ]

    def was_logged(self, log_reference: str, level: str | None = None) -> bool:
        """
        Check if a specific log reference was logged.
        """
        return bool(self.get_log(log_reference, level))


@fixture
def mock_logger() -> Generator[MockLogger, None, None]:
    """
    Fixture to provide a mock logger instance for testing.
    """
    with patch("ftrs_common.logger.Logger.get") as mock_get:
        mock_logger_instance = MockLogger(service="mock_logger")
        mock_get.return_value = mock_logger_instance
        yield mock_logger_instance
