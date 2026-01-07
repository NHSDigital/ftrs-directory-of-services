import logging
from dataclasses import dataclass
from enum import Enum
from functools import cache

from aws_lambda_powertools.logging import Logger as PowertoolsLogger
from ftrs_common.utils.correlation_id import get_correlation_id
from ftrs_common.utils.request_id import get_request_id
from pydantic import BaseModel


@dataclass(frozen=True)
class LogReference:
    """
    A class to represent a log reference.
    """

    message: str
    level: int = logging.NOTSET
    capture_exception: bool = False

    def format(self, **kwargs: dict) -> str:
        return self.message.format(**kwargs)


class LogBase(Enum):
    """
    A wrapper class for storing log references.
    The log reference will be the name of the enum member.
    The details of the log are held in the value of the enum member.
    """


class LogEntry(BaseModel):
    msg: str
    reference: str
    stacklevel: int
    detail: dict | None = None


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

        log_details = log_reference.value
        log_entry = LogEntry(
            msg=self.format_message(log_reference, **detail),
            reference=log_reference.name,
            stacklevel=3,
            detail=detail if detail else None,
        )
        log_dict = log_entry.model_dump(mode="json", fallback=str)

        if log_details.capture_exception:
            log_dict["exc_info"] = True
            log_dict["stack_info"] = True

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

        return log_entry.msg

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
        return cls(service=service)
