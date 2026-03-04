from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle

from functions.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)


@pytest.fixture
def bundle():
    return Bundle.model_construct(id="bundle-id")


@pytest.fixture
def mock_setup_request():
    """Mock for the setup_request utility function."""
    with patch("functions.request_context_middleware.setup_request") as mock:
        yield mock


@pytest.fixture
def mock_get_response_size_and_duration(bundle):
    """Mock for the get_response_size_and_duration utility function."""
    with patch(
        "functions.dos_search_ods_code_function.get_response_size_and_duration"
    ) as mock:
        response_size = len(bundle.model_dump_json().encode("utf-8"))
        mock.return_value = (response_size, 1)
        yield mock


@pytest.fixture
def mock_logger():
    """Mock for the FTRS common Logger used for all log() calls."""
    with patch("functions.dos_search_ods_code_function.logger") as mock:
        yield mock


@pytest.fixture
def ods_code():
    return "ABC123"


@pytest.fixture
def event(ods_code):
    return {
        "headers": {
            "Accept": "application/fhir+json",
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
            "Version": "1",
            "NHSD-Request-ID": "request_id",
            "NHSD-Correlation-ID": "request_id.correlation_id.message_id",
            "X-Correlation-ID": "test-x-correlation-id",
            "X-Request-ID": "request_id",
            "End-User-Role": "Clinician",
            "Application-ID": "application_id",
            "Application-Name": "dos_unit_tests",
            "Request-Start-Time": "2023-01-01T00:00:00Z",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US",
            "User-Agent": "test-user-agent",
            "Host": "test-host",
            "X-Amzn-Trace-Id": "test-trace-id",
            "X-Forwarded-For": "127.0.0.1",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https",
        },
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}",
            "_revinclude": REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
        },
        "pathParameters": None,
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "body": None,
    }


@pytest.fixture
def log_data():
    return {
        "dos_nhsd_correlation_id": "correlation_id",
        "dos_nhsd_request_id": "request_id",
        "dos_message_id": "message_id",
        "dos_message_category": "LOGGING",
    }


@pytest.fixture
def details(event):
    return {
        "dos_environment": "Development",
        "dos_search_api_version": "1",
        "lambda_version": "0.0.1",
        "connecting_party_end_user_role": "Clinician",
        "connecting_party_application_id": "application_id",
        "connecting_party_application_name": "dos_unit_tests",
        "request_params": {
            "query_params": event.get("queryStringParameters") or {},
            "path_params": event.get("pathParameters") or {},
            "request_context": event.get("requestContext") or {},
        },
    }
