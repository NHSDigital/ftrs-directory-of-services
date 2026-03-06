import json
import time
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from unittest.mock import MagicMock, patch

import pytest
from ftrs_common.logger import LogBase, Logger, LogReference, SplunkHECFormatter


def test_logger_create() -> None:
    """
    Test the creation of a logger instance.
    """
    logger = Logger.get(service="test_service")
    assert isinstance(logger, Logger)
    assert logger.service == "test_service"
    assert logger.level == INFO
    assert logger.child is False

    other_logger = Logger.get(service="test_service")
    assert logger is other_logger


def test_logger_log() -> None:
    class CustomLogBase(LogBase):
        DEBUG_LOG = LogReference(level=DEBUG, message="Debug log message")
        INFO_LOG = LogReference(level=INFO, message="Info log message")
        WARNING_LOG = LogReference(level=WARNING, message="Warning log message")
        ERROR_LOG = LogReference(level=ERROR, message="Error log message")
        CRITICAL_LOG = LogReference(level=CRITICAL, message="Critical log message")
        INVALID_LOG = LogReference(level=999, message="Invalid log message")

    logger = Logger.get(service="test_service")

    # Mock the logger methods to test logging
    logger.debug = MagicMock()
    logger.info = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()

    logger.log(CustomLogBase.DEBUG_LOG, some_detail="test detail")
    logger.debug.assert_called_once_with(
        reference="DEBUG_LOG",
        msg="Debug log message",
        detail={"some_detail": "test detail"},
        stacklevel=3,
    )

    logger.log(CustomLogBase.INFO_LOG, another_detail="another test detail")
    logger.info.assert_called_once_with(
        reference="INFO_LOG",
        msg="Info log message",
        detail={"another_detail": "another test detail"},
        stacklevel=3,
    )

    logger.log(CustomLogBase.WARNING_LOG, yet_another_detail="yet another test detail")
    logger.warning.assert_called_once_with(
        reference="WARNING_LOG",
        msg="Warning log message",
        detail={"yet_another_detail": "yet another test detail"},
        stacklevel=3,
    )

    logger.log(CustomLogBase.ERROR_LOG, error_detail="error test detail")
    logger.error.assert_called_once_with(
        reference="ERROR_LOG",
        msg="Error log message",
        detail={"error_detail": "error test detail"},
        stacklevel=3,
    )

    logger.log(CustomLogBase.CRITICAL_LOG, critical_detail="critical test detail")
    logger.critical.assert_called_once_with(
        reference="CRITICAL_LOG",
        msg="Critical log message",
        detail={"critical_detail": "critical test detail"},
        stacklevel=3,
    )


def test_logger_log_invalid_level() -> None:
    class CustomLogBase(LogBase):
        INVALID_LOG = LogReference(level=999, message="Invalid log message")

    logger = Logger.get(service="test_service")

    with pytest.raises(ValueError) as excinfo:
        logger.log(CustomLogBase.INVALID_LOG)
    assert str(excinfo.value) == (
        "Invalid log level: 999. Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL from the Python logging module."
    )


def test_logbase() -> None:
    class CustomLogBase(LogBase):
        CUSTOM_LOG = LogReference(level=DEBUG, message="Custom log message")
        ANOTHER_LOG = LogReference(level=INFO, message="Another log message")

    assert CustomLogBase.CUSTOM_LOG.name == "CUSTOM_LOG"
    assert CustomLogBase.CUSTOM_LOG.value.level == DEBUG
    assert CustomLogBase.CUSTOM_LOG.value.message == "Custom log message"

    assert CustomLogBase.ANOTHER_LOG.name == "ANOTHER_LOG"
    assert CustomLogBase.ANOTHER_LOG.value.level == INFO
    assert CustomLogBase.ANOTHER_LOG.value.message == "Another log message"


def test_format_message() -> None:
    class CustomLogBase(LogBase):
        CUSTOM_LOG = LogReference(level=DEBUG, message="Custom log with {param}")

    logger = Logger.get(service="test_service")
    formatted_message = logger.format_message(CustomLogBase.CUSTOM_LOG, param="value")
    assert formatted_message == "Custom log with value"


def test_format_message_no_params() -> None:
    class CustomLogBase(LogBase):
        CUSTOM_LOG = LogReference(level=DEBUG, message="Custom log without params")

    logger = Logger.get(service="test_service")
    formatted_message = logger.format_message(CustomLogBase.CUSTOM_LOG)
    assert formatted_message == "Custom log without params"


def test_format_message_missing_params() -> None:
    class CustomLogBase(LogBase):
        CUSTOM_LOG = LogReference(level=DEBUG, message="Custom log with {param}")

    logger = Logger.get(service="test_service")

    with pytest.raises(
        KeyError, match="Missing key in log message \\(CUSTOM_LOG\\): 'param'"
    ):
        logger.format_message(CustomLogBase.CUSTOM_LOG, missing_param="value")


def test_splunk_hec_formatter_serialize_structure() -> None:
    """serialize() returns valid JSON wrapping the log dict in a HEC envelope."""
    formatter = SplunkHECFormatter()
    log_dict = {"service": "my_service", "level": "INFO", "message": "hello"}

    with patch(
        "ftrs_common.logger.get_splunk_index",
        return_value="app_directoryofservices_prod",
    ):
        result = formatter.serialize(log_dict)

    payload = json.loads(result)
    assert isinstance(payload["time"], float)
    assert payload["source"] == "my_service"
    assert payload["index"] == "app_directoryofservices_prod"
    assert payload["event"] == log_dict


def test_splunk_hec_formatter_serialize_function_name_fallback() -> None:
    """serialize() falls back to 'function_name' when 'service' key is absent."""
    formatter = SplunkHECFormatter()
    log_dict = {
        "function_name": "my_lambda",
        "level": "INFO",
        "message": "no service key",
    }

    with patch(
        "ftrs_common.logger.get_splunk_index",
        return_value="app_directoryofservices_prod",
    ):
        result = formatter.serialize(log_dict)

    payload = json.loads(result)
    assert payload["source"] == "my_lambda"


def test_splunk_hec_formatter_serialize_default_source() -> None:
    """serialize() falls back to 'ftrs' when both 'service' and 'function_name' keys are absent."""
    formatter = SplunkHECFormatter()
    log_dict = {"level": "INFO", "message": "no service key"}

    with patch(
        "ftrs_common.logger.get_splunk_index",
        return_value="app_directoryofservices_prod",
    ):
        result = formatter.serialize(log_dict)

    payload = json.loads(result)
    assert payload["source"] == "ftrs"


def test_splunk_hec_formatter_time_is_current_epoch() -> None:
    """serialize() sets 'time' to a current Unix epoch float."""
    formatter = SplunkHECFormatter()
    log_dict = {"service": "svc", "message": "msg"}

    with patch(
        "ftrs_common.logger.get_splunk_index",
        return_value="app_directoryofservices_prod",
    ):
        before = time.time()
        result = formatter.serialize(log_dict)
        after = time.time()

    payload = json.loads(result)
    assert before <= payload["time"] <= after


def test_logger_get_uses_splunk_hec_formatter() -> None:
    """Logger.get() creates an instance whose handler uses SplunkHECFormatter."""
    logger = Logger.get(service="hec_formatter_check")
    formatter_types = [type(h.formatter) for h in logger.handlers]
    assert SplunkHECFormatter in formatter_types
