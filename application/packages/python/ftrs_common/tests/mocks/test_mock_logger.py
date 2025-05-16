from ftrs_common.logger import LogBase, Logger, LogReference
from ftrs_common.mocks.mock_logger import MockLogger


class ExampleLogBase(LogBase):
    """
    Example log base for testing.
    """

    EXAMPLE_LOG = LogReference(level=10, message="Example log message")
    WARNING_LOG = LogReference(level=30, message="Warning log message")


def test_mock_logger_fixture(mock_logger: MockLogger) -> None:
    """
    Test the mock logger fixture.
    """

    assert mock_logger is not None
    assert isinstance(mock_logger, MockLogger)
    assert mock_logger.service == "mock_logger"
    assert mock_logger.get_log_count() == 0

    logger_instance = Logger.get(service="something")
    assert logger_instance is mock_logger

    logger_instance.log(ExampleLogBase.EXAMPLE_LOG)
    assert mock_logger.get_log_count() == 1
    assert mock_logger.get_log_count(level="DEBUG") == 1
    assert mock_logger.get_log_count(level="INFO") == 0

    assert mock_logger.was_logged("EXAMPLE_LOG")
    assert len(mock_logger.logs["DEBUG"]) == 1
    assert mock_logger.logs["DEBUG"][0]["reference"] == "EXAMPLE_LOG"

    logger_instance.log(ExampleLogBase.WARNING_LOG)
    assert mock_logger.was_logged("WARNING_LOG")
    assert len(mock_logger.logs["WARNING"]) == 1
    assert mock_logger.logs["WARNING"][0]["reference"] == "WARNING_LOG"

    assert mock_logger.was_logged("EXAMPLE_LOG", level="DEBUG")
    assert not mock_logger.was_logged("EXAMPLE_LOG", level="INFO")
    assert not mock_logger.was_logged("EXAMPLE_LOG", level="WARNING")
    assert not mock_logger.was_logged("EXAMPLE_LOG", level="ERROR")

    assert not mock_logger.was_logged("WARNING_LOG", level="DEBUG")
    assert not mock_logger.was_logged("WARNING_LOG", level="INFO")
    assert mock_logger.was_logged("WARNING_LOG", level="WARNING")
    assert not mock_logger.was_logged("WARNING_LOG", level="ERROR")

    total_log_count = 2
    assert mock_logger.get_log_count() == total_log_count

    assert mock_logger.get_logs(level="DEBUG") == [
        {
            "reference": "EXAMPLE_LOG",
            "msg": "Example log message",
        }
    ]
    assert mock_logger.get_logs(level="WARNING") == [
        {
            "reference": "WARNING_LOG",
            "msg": "Warning log message",
        }
    ]
    assert mock_logger.get_logs() == [
        {
            "reference": "EXAMPLE_LOG",
            "msg": "Example log message",
        },
        {
            "reference": "WARNING_LOG",
            "msg": "Warning log message",
        },
    ]

    mock_logger.clear_logs()
    assert mock_logger.get_log_count() == 0
