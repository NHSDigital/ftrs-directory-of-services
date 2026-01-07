from unittest.mock import Mock

from ftrs_common.logger import Logger
from time import time_ns


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
                "_timestamp": time_ns(),
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
            logs = sorted(self.logs.get(level, []), key=lambda x: x["_timestamp"])
        else:
            logs = sorted(
                [log for level_logs in self.logs.values() for log in level_logs],
                key=lambda x: x["_timestamp"],
            )

        return [self._format_log_for_checks(log) for log in logs]

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
        self.logs = {
            "DEBUG": [],
            "INFO": [],
            "WARNING": [],
            "ERROR": [],
            "CRITICAL": [],
        }

    def get_log(self, log_reference: str, level: str | None = None) -> list[dict]:
        """
        Get logs for a specific log reference.
        """
        if level:
            assert level in self.logs, f"Invalid log level: {level}"
            logs = sorted(self.logs[level], key=lambda x: x["_timestamp"])
            logs = [log for log in logs if log["reference"] == log_reference]

        else:
            logs = sorted(
                [
                    log
                    for level_logs in self.logs.values()
                    for log in level_logs
                    if log["reference"] == log_reference
                ],
                key=lambda x: x["_timestamp"],
            )

        return [self._format_log_for_checks(log) for log in logs]

    def was_logged(self, log_reference: str, level: str | None = None) -> bool:
        """
        Check if a specific log reference was logged.
        """
        return bool(self.get_log(log_reference, level))

    def format_logs_for_print(self) -> str:
        """
        Format logs for printing.
        """
        formatted_logs = []
        for level, level_logs in self.logs.items():
            for log in level_logs:
                detail_str = f" | Detail: {log['detail']}" if log.get("detail") else ""
                formatted_logs.append(
                    f"[{level}] Reference: {log['reference']} | Msg: {log['msg']}{detail_str}"
                )
        return "\n".join(formatted_logs)

    def _format_log_for_checks(self, log: dict) -> dict:
        """
        Format a specific log for checks.
        """
        formatted_log = {"msg": log["msg"]}
        if log.get("detail"):
            formatted_log["detail"] = log["detail"]

        return formatted_log
