from unittest.mock import patch

import pytest


# Fixtures extracted from functions/test_dos_search_ods_code_function.py to support functions/test_dos_logger.py
@pytest.fixture
def mock_logger(log_data, details):
    with patch("functions.dos_search_ods_code_function.dos_logger") as mock:
        mock.extract.return_value = log_data
        mock.extract_one_time.return_value = details
        yield mock


@pytest.fixture
def ods_code():
    return "ABC123"


@pytest.fixture
def event(ods_code):
    return {
        "headers": {"NHSD-Correlation-ID": "correlation_id"},
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{ods_code}",
            "_revinclude": "Endpoint:organization",
        },
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
        "dos_nhsd_request_id": "DOS_LOG_PLACEHOLDER",
        "dos_message_id": "DOS_LOG_PLACEHOLDER",
        "dos_message_category": "LOGGING",
        "details": {},
    }


@pytest.fixture
def details(event):
    return {
        "opt_dos_environment": "DOS_LOG_PLACEHOLDER",
        "opt_dos_api_version": "DOS_LOG_PLACEHOLDER",
        "opt_dos_lambda_version": "DOS_LOG_PLACEHOLDER",
        "opt_dos_response_time": "DOS_LOG_PLACEHOLDER",
        "opt_dos_response_size": "DOS_LOG_PLACEHOLDER",
        "opt_dos_end_user_role": "DOS_LOG_PLACEHOLDER",
        "opt_dos_client_id": "DOS_LOG_PLACEHOLDER",
        "opt_dos_application_name": "DOS_LOG_PLACEHOLDER",
        "opt_dos_request_params": {
            "query_params": event.get("queryStringParameters") or {},
            "path_params": event.get("pathParams") or {},
            "request_context": event.get("requestContext") or {},
        },
    }
