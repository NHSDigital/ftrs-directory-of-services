from unittest.mock import Mock

from ftrs_common.logger import Logger


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

        def _store_log(**kwargs: dict) -> None:
            assert level in self.logs, f"Invalid log level: {level}"
            log_dict = {
                "reference": kwargs.get("reference"),
                "msg": kwargs.get("msg"),
            }
            if kwargs.get("detail"):
                log_dict["detail"] = kwargs.get("detail")

            self.logs[level].append(log_dict)

        return _store_log

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
