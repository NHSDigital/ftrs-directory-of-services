import logging
from dataclasses import dataclass
from enum import Enum
from functools import cache

from aws_lambda_powertools.logging import Logger as PowertoolsLogger


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


class Logger(PowertoolsLogger):
    """
    Custom logger class that extends the AWS Lambda Powertools Logger.
    """

    def log(self, log_reference: LogBase, **detail: dict) -> None:
        """
        Log a message with a specific log reference.
        """
        log_key = log_reference.name
        log_details = log_reference.value
        formatted_message = log_details.format(**detail)
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

    @classmethod
    @cache
    def get(cls, service: str = "ftrs") -> "Logger":
        """
        Create a new instance of the Logger class.
        """
        return cls(service=service, level="DEBUG", child=True)
