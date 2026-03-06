import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from functools import cache

from aws_lambda_powertools.logging import Logger as PowertoolsLogger
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter
from ftrs_common.utils.correlation_id import get_correlation_id
from ftrs_common.utils.request_id import get_request_id
from ftrs_common.utils.splunk import get_splunk_index


@dataclass(frozen=True)
class LogReference:
    """
    A class to represent a log reference.
    """

    message: str
    level: int = logging.NOTSET

    def format(self, **kwargs: dict) -> str:
        return self.message.format(**kwargs)


class LogBase(Enum):
    """
    A wrapper class for storing log references.
    The log reference will be the name of the enum member.
    The details of the log are held in the value of the enum member.
    """


class SplunkHECFormatter(LambdaPowertoolsFormatter):
    """
    Formats log records as Splunk HTTP Event Collector (HEC) event payloads.

    Each log line emitted to stdout is a valid Splunk HEC JSON object with:
      - time: Unix epoch float
      - source: the logger service name
      - index: value returned by get_splunk_index(), typically "<prefix>_<env>"
      - event: the original structured log dict
    """

    def serialize(self, log: dict) -> str:  # type: ignore[override]
        hec_payload = {
            "time": time.time(),
            "source": log.get("service") or log.get("function_name") or "ftrs",
            "index": get_splunk_index(),
            "event": log,
        }
        return json.dumps(hec_payload, default=str)


class Logger(PowertoolsLogger):
    """
    Custom logger class that extends the AWS Lambda Powertools Logger.
    """

    def log(self, log_reference: LogBase, **detail: dict) -> str:
        """
        Log a message with a specific log reference.
        Returns the formatted log message.
        """
        if correlation_id := get_correlation_id():
            self.append_keys(correlation_id=correlation_id)
        if request_id := get_request_id():
            self.append_keys(request_id=request_id)
        log_key = log_reference.name
        log_details = log_reference.value
        formatted_message = self.format_message(log_reference, **detail)
        log_dict = {"msg": formatted_message, "reference": log_key, "stacklevel": 3}
        if detail:
            log_dict["detail"] = detail

        match log_details.level:
            case logging.DEBUG:
                self.debug(**log_dict)

            case logging.INFO:
                self.info(**log_dict)

            case logging.WARNING:
                self.warning(**log_dict)

            case logging.ERROR:
                self.error(**log_dict)

            case logging.CRITICAL:
                self.critical(**log_dict)

            case _:
                error_msg = (
                    f"Invalid log level: {log_details.level}. "
                    f"Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL from the Python logging module."
                )
                raise ValueError(error_msg)

        return formatted_message

    def format_message(self, log_details: LogBase, **kwargs: dict) -> str:
        """
        Format the log message with the provided keyword arguments.
        """
        try:
            return log_details.value.message.format(**kwargs)
        except KeyError as e:
            msg = f"Missing key in log message ({log_details.name}): {e}"
            raise KeyError(msg) from e

    @classmethod
    @cache
    def get(cls, service: str = "ftrs") -> "Logger":
        """
        Create a new instance of the Logger class.
        """
        return cls(service=service, logger_formatter=SplunkHECFormatter())
