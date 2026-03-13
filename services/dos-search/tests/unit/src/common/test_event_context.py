import os
import time
from copy import deepcopy
from unittest.mock import ANY, MagicMock, patch

import pytest

from src.common.event_context import (
    PLACEHOLDER,
    get_response_size_and_duration,
    setup_request,
)
from src.common.logbase import DosSearchLogBase


@pytest.fixture(autouse=True)
def setup_env_vars():
    prev_environment = os.environ.get("ENVIRONMENT")
    prev_lambda_version = os.environ.get("AWS_LAMBDA_FUNCTION_VERSION")
    os.environ["ENVIRONMENT"] = "Development"
    os.environ["AWS_LAMBDA_FUNCTION_VERSION"] = "0.0.1"
    yield
    if prev_environment is None:
        os.environ.pop("ENVIRONMENT", None)
    else:
        os.environ["ENVIRONMENT"] = prev_environment
    if prev_lambda_version is None:
        os.environ.pop("AWS_LAMBDA_FUNCTION_VERSION", None)
    else:
        os.environ["AWS_LAMBDA_FUNCTION_VERSION"] = prev_lambda_version


class TestSetupRequest:
    def test_appends_mandatory_fields(self, event, log_data):
        mock_logger = MagicMock()
        setup_request(event, mock_logger)
        mock_logger.thread_safe_append_keys.assert_called_once_with(**log_data)

    def test_appends_mandatory_fields_with_missing_headers(self, event, log_data):
        modified_event = deepcopy(event)
        modified_event["headers"].pop("NHSD-Correlation-ID")

        expected = dict(log_data)
        expected["dos_message_id"] = PLACEHOLDER

        mock_logger = MagicMock()
        setup_request(modified_event, mock_logger)
        mock_logger.thread_safe_append_keys.assert_called_once_with(**expected)

    def test_logs_one_time_fields(self, event, details):
        mock_logger = MagicMock()
        setup_request(event, mock_logger)
        mock_logger.log.assert_called_once_with(
            DosSearchLogBase.DOS_SEARCH_001,
            **details,
            dos_message_category="REQUEST",
        )

    def test_logs_one_time_fields_with_missing_headers(self, event, details):
        modified_event = deepcopy(event)
        modified_event["headers"].pop("Version")
        modified_event["headers"].pop("End-User-Role")
        modified_event["headers"].pop("Application-ID")
        modified_event["headers"].pop("Application-Name")
        modified_event["queryStringParameters"] = {}
        modified_event["pathParameters"] = None
        modified_event["requestContext"] = {}

        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("AWS_LAMBDA_FUNCTION_VERSION", None)

        expected = dict(details)
        expected["dos_search_api_version"] = PLACEHOLDER
        expected["connecting_party_end_user_role"] = PLACEHOLDER
        expected["connecting_party_application_id"] = PLACEHOLDER
        expected["connecting_party_application_name"] = PLACEHOLDER
        for key in expected["request_params"]:
            expected["request_params"][key] = {}
        expected["dos_environment"] = PLACEHOLDER
        expected["lambda_version"] = PLACEHOLDER

        mock_logger = MagicMock()
        setup_request(modified_event, mock_logger)
        mock_logger.log.assert_called_once_with(
            DosSearchLogBase.DOS_SEARCH_001,
            **expected,
            dos_message_category="REQUEST",
        )

    def test_calls_fetch_or_set_ids(self, event):
        mock_logger = MagicMock()
        with (
            patch("src.common.event_context.fetch_or_set_request_id") as mock_req,
            patch("src.common.event_context.fetch_or_set_correlation_id") as mock_corr,
        ):
            setup_request(event, mock_logger)
            mock_req.assert_called_once_with(header_id="request_id")
            mock_corr.assert_called_once_with(
                existing="request_id.correlation_id.message_id"
            )


class TestGetResponseSizeAndDuration:
    def test_returns_size_and_duration(self, bundle):
        start_time = time.time()
        mock_logger = MagicMock()

        response_size, duration_ms = get_response_size_and_duration(
            bundle, start_time, mock_logger
        )

        assert response_size == len(bundle.model_dump_json().encode("utf-8"))
        assert duration_ms >= 0

    def test_with_exception_returns_zero_and_logs(self):
        start_time = time.time()
        mock_logger = MagicMock()

        response_size, duration_ms = get_response_size_and_duration(
            None, start_time, mock_logger
        )

        assert response_size == 0
        assert duration_ms >= 0
        mock_logger.log.assert_called_once_with(
            DosSearchLogBase.DOS_SEARCH_010,
            dos_response_time=ANY,
            dos_response_size=0,
        )
