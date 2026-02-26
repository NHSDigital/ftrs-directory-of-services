import json
import os
import time
from copy import deepcopy
from dataclasses import dataclass
from unittest.mock import ANY, call, patch

import pytest
from aws_lambda_powertools.event_handler import Response

from functions.logbase import DosSearchLogBase
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

        modified_event["headers"].pop("Version")
        modified_event["headers"].pop("End-User-Role")
        modified_event["headers"].pop("Application-ID")
        modified_event["headers"].pop("Application-Name")
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
        with (
            patch("functions.logger.dos_logger.fetch_or_set_request_id") as mock_req,
            patch(
                "functions.logger.dos_logger.fetch_or_set_correlation_id"
            ) as mock_corr,
        ):
            lambda_handler(event, lambda_context, call_init)

            # Assert fetch_or_set called with values from event headers
            mock_req.assert_called_once_with(header_id="request_id")
            mock_corr.assert_called_once_with(
                existing="request_id.correlation_id.message_id"
            )

        # Assert append_keys called with mandatory dos fields
        mock_base_powertools_logger.assert_has_calls(
            [
                call.append_keys(**log_data),
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
        # Error logged out to mark failure via common logger (DOS_SEARCH_010 is ERROR level)
        mock_base_powertools_logger.log.assert_called_once_with(
            DosSearchLogBase.DOS_SEARCH_010,
            dos_response_time=ANY,
            dos_response_size=0,
        )
