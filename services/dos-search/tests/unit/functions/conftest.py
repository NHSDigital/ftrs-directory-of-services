from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle

from functions.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)


# Fixtures extracted from functions/test_dos_search_ods_code_function.py to support functions/test_dos_logger.py
@pytest.fixture
def bundle():
    return Bundle.model_construct(id="bundle-id")


@pytest.fixture
def mock_logger(log_data, details, bundle):
    with patch("functions.dos_search_ods_code_function.dos_logger") as mock:
        mock.extract.return_value = log_data
        mock.extract_one_time.return_value = details
        # get_response_size_and_duration setup
        response_size = len(bundle.model_dump_json().encode("utf-8"))
        response_time = 1
        mock.get_response_size_and_duration.return_value = (
            response_size,
            response_time,
        )
        yield mock


@pytest.fixture
def ods_code():
    return "ABC123"


@pytest.fixture
def event(ods_code):
    return {
        "headers": {
            # Mandatory log field headers
            "NHSD-Correlation-ID": "request_id.correlation_id.message_id",
            "NHSD-Request-ID": "request_id",
            # One-time log field headers
            "version": 1,
            "end-user-role": "Clinician",
            "application-id": "application_id",
            "application-name": "dos_unit_tests",
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
        "logger": "dos_logger",
        "dos_nhsd_correlation_id": "correlation_id",
        "dos_nhsd_request_id": "request_id",
        "dos_message_id": "message_id",
        "dos_message_category": "LOGGING",
    }


@pytest.fixture
def details(event):
    return {
        "dos_environment": "Development",
        "dos_search_api_version": 1,
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
