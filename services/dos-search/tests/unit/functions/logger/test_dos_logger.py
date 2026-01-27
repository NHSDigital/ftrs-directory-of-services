import json
import os
import time
from copy import deepcopy
from dataclasses import dataclass
from unittest.mock import call, patch

import pytest
from aws_lambda_powertools.event_handler import Response

from functions.logger.dos_logger import PLACEHOLDER, DosLogger
from tests.unit.functions.logger.setup_dummy_lambda import lambda_handler


@dataclass
class LambdaContext:
    function_name: str = "test"
    memory_limit_in_mb: int = 128
    invoked_function_arn: str = "arn:aws:lambda:eu-west-1:809313241:function:test"
    aws_request_id: str = "52fdfc07-2182-154f-163f-5f0f9a621d72"


@pytest.fixture
def lambda_context() -> LambdaContext:
    return LambdaContext()


@pytest.fixture
def assert_mandatory_fields_present(log_data):
    def assert_mandatory_fields_are_present(current_keys) -> None:
        for key in log_data.keys():
            assert key in current_keys, f"Missing mandatory log field: {key}"

    return assert_mandatory_fields_are_present


service = "test_logger"


@pytest.fixture
def dos_logger():
    return DosLogger.get(service=service)


@pytest.fixture
def mock_base_powertools_logger():
    with patch(
        "tests.unit.functions.logger.setup_dummy_lambda.dos_logger.logger"
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def setup_env_vars():
    # Arrange
    os.environ["ENVIRONMENT"] = "Development"
    os.environ["AWS_LAMBDA_FUNCTION_VERSION"] = "0.0.1"

    # Act & Assert
    yield
    # Cleanup environment variables
    os.environ.pop("ENVIRONMENT", None)
    os.environ.pop("AWS_LAMBDA_FUNCTION_VERSION", None)


class TestDosLogger:
    # Extract method tests
    def test_extract(self, dos_logger, event, log_data):
        # Arrange
        extract = dict(log_data)
        # Act
        result = dos_logger.extract(event)
        # Assert
        assert result == extract

    def test_extract_with_missing_headers(self, dos_logger, event, log_data):
        # Arrange
        modified_event = deepcopy(event)
        modified_event["headers"].pop("NHSD-Correlation-ID")
        modified_event["headers"].pop("NHSD-Request-ID")

        extract = dict(log_data)
        extract["dos_nhsd_correlation_id"] = PLACEHOLDER
        extract["dos_nhsd_request_id"] = PLACEHOLDER
        extract["dos_message_id"] = PLACEHOLDER

        # Act
        result = dos_logger.extract(modified_event)

        # Assert
        assert result == extract

    def test_extract_one_time(self, dos_logger, event, details):
        # Arrange

        # Act
        result = dos_logger.extract_one_time(event)

        # Assert
        assert result == details

    def test_extract_one_time_with_missing_headers(self, dos_logger, event, details):
        # Arrange

        modified_event = deepcopy(event)

        modified_event["headers"].pop("version")
        modified_event["headers"].pop("end-user-role")
        modified_event["headers"].pop("application-id")
        modified_event["headers"].pop("application-name")
        modified_event["queryStringParameters"] = {}
        modified_event["pathParameters"] = None
        modified_event["requestContext"] = {}

        placeholder_details = dict(details)

        os.environ.pop(
            "ENVIRONMENT", None
        )  # Remove env_vars populated by autouse fixture setup_env_vars
        os.environ.pop("AWS_LAMBDA_FUNCTION_VERSION", None)

        placeholder_details["dos_search_api_version"] = PLACEHOLDER
        placeholder_details["connecting_party_end_user_role"] = PLACEHOLDER
        placeholder_details["connecting_party_application_id"] = PLACEHOLDER
        placeholder_details["connecting_party_application_name"] = PLACEHOLDER
        for key in placeholder_details["request_params"]:
            placeholder_details["request_params"][key] = {}
        placeholder_details["dos_environment"] = PLACEHOLDER
        placeholder_details["lambda_version"] = PLACEHOLDER
        # Act
        result = dos_logger.extract_one_time(modified_event)

        # Assert
        assert result == placeholder_details

    # Utility method tests
    def test_get_header_with_valid_header(self, dos_logger, event):
        # Arrange
        dos_logger.headers = event.get("headers")

        # Act
        result = dos_logger._get_header("NHSD-Request-ID")

        # Assert
        assert result == "request_id"

    def test_get_header_with_invalid_header(self, dos_logger, event):
        # Arrange
        dos_logger.headers = event.get("headers")

        # Act
        result = dos_logger._get_header("Bogus-ID")

        # Assert
        assert result is None

    # Logging method tests
    def test_init(
        self,
        event,
        log_data,
        details,
        lambda_context,
        mock_base_powertools_logger,
    ):
        # Arrange
        def call_init() -> Response:
            # lambda_handler automatically calls init unless run_init=False is set
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_init)

        # Assert
        mock_base_powertools_logger.assert_has_calls(
            [
                call.append_keys(**log_data),
                call.info(
                    "Logging one-time fields from Request",
                    extra={"detail": details, "dos_message_category": "REQUEST"},
                ),
            ]
        )

    def test_debug_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        assert_mandatory_fields_present,
    ):
        caplog.set_level(10)  # DEBUG
        dos_logger.logger.setLevel(10)  # DEBUG
        # Arrange
        debug_message = "test_debug_call: testing debug call"

        def call_debug() -> Response:
            dos_logger.debug(debug_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_debug)
        capture = dos_logger.get_keys()

        # Assert
        assert_mandatory_fields_present(capture)
        assert "test_debug_call: testing debug call" in caplog.messages

    def test_info_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        assert_mandatory_fields_present,
    ):
        # Arrange
        info_message = "test_info_call: testing info call"

        def call_info() -> Response:
            dos_logger.info(info_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_info)
        capture = dos_logger.get_keys()

        # Assert
        assert_mandatory_fields_present(capture)
        assert "test_info_call: testing info call" in caplog.messages

    def test_warning_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        assert_mandatory_fields_present,
    ):
        # Arrange
        warning_message = "test_warning_call: testing warning call"

        def call_warning() -> Response:
            dos_logger.warning(warning_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_warning)
        capture = dos_logger.get_keys()

        # Assert
        assert_mandatory_fields_present(capture)
        assert "test_warning_call: testing warning call" in caplog.messages

    def test_error_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        assert_mandatory_fields_present,
    ):
        # Arrange
        error_message = "test_error_call: testing error call"

        def call_error() -> Response:
            dos_logger.error(error_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_error)
        capture = dos_logger.get_keys()

        # Assert
        assert_mandatory_fields_present(capture)
        assert "test_error_call: testing error call" in caplog.messages

    def test_exception_call(
        self,
        caplog,
        event,
        dos_logger,
        lambda_context,
        assert_mandatory_fields_present,
    ):
        # Arrange
        exception_message = "test_exception_call: testing exception call"

        def call_exception() -> Response:
            dos_logger.exception(exception_message)
            return Response(
                status_code=123,
                content_type="application/fhir+json",
                body=json.dumps(dict()),
            )

        # Act
        lambda_handler(event, lambda_context, call_exception)
        capture = dos_logger.get_keys()

        # Assert
        assert_mandatory_fields_present(capture)
        assert "test_exception_call: testing exception call" in caplog.messages

    def test_powertools_log_calls(self, dos_logger, mock_base_powertools_logger):
        # Act
        dos_logger.debug("debug message")
        dos_logger.info("info message")
        dos_logger.warning("warning message")
        dos_logger.error("error message")
        dos_logger.exception("exception message")
        dos_logger._log_with_level("bogus", "bogus level message")

        # Assert
        mock_base_powertools_logger.assert_has_calls(
            [
                call.debug("debug message", extra={}),
                call.info("info message", extra={}),
                call.warning("warning message", extra={}),
                call.error("error message", extra={}),
                call.exception("exception message", extra={}),
                call.info("bogus level message", extra={}),  # default to info
            ]
        )

    def test_powertools_append_call(self, dos_logger, mock_base_powertools_logger):
        # Arrange
        extra_keys = {
            "dos_extra_key_1": "extra_value_1",
            "dos_extra_key_2": "extra_value_2",
        }

        # Act
        dos_logger.append_keys(extra_keys)

        # Assert
        mock_base_powertools_logger.append_keys.assert_called_once_with(**extra_keys)

    def test_powertools_set_level_call(self, dos_logger, mock_base_powertools_logger):
        # Arrange
        level = 40

        # Act
        dos_logger.set_level(level)

        # Assert
        mock_base_powertools_logger.setLevel.assert_called_once_with(level)

    def test_powertools_clear_state_call(self, dos_logger, mock_base_powertools_logger):
        # Act
        dos_logger.clear_state()

        # Assert
        mock_base_powertools_logger.clear_state.assert_called_once()

    def test_get_response_size_and_duration(
        self,
        dos_logger,
        bundle,
    ):
        # Arrange
        start_time = time.time()

        # Act
        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            bundle, start_time
        )

        # Assert
        expected_size = len(bundle.model_dump_json().encode("utf-8"))
        assert response_size == expected_size
        assert duration_ms >= 0  # Duration should be non-negative

    def test_get_response_size_and_duration_with_exception(
        self, dos_logger, mock_base_powertools_logger
    ):
        # Arrange
        start_time = time.time()

        # Act
        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            None, start_time
        )

        # Assert
        # Function still returns
        assert response_size == 0
        assert duration_ms >= 0
        # Error logged out to mark failure
        mock_base_powertools_logger.exception.assert_called_with(
            "Failed to calculate response size",
            extra={
                "detail": {
                    "dos_response_time": f"{duration_ms}ms",
                    "dos_response_size": 0,
                }
            },
        )
