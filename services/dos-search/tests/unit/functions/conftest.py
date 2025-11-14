from unittest.mock import patch

import pytest


# Fixtures extracted from functions/test_dos_search_ods_code_function.py to support functions/test_ftrs_logger.py
@pytest.fixture
def mock_logger():
    with patch("functions.dos_search_ods_code_function.ftrs_logger") as mock:
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
        "logger": "ftrs_logger",
        "ftrs_nhsd_correlation_id": "correlation_id",
        "ftrs_nhsd_request_id": "FTRS_LOG_PLACEHOLDER",
        "ftrs_message_id": "FTRS_LOG_PLACEHOLDER",
        "ftrs_message_category": "LOGGING",
    }


@pytest.fixture
def details(event):
    return {
        "opt_ftrs_environment": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_api_version": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_lambda_version": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_response_time": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_response_size": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_end_user_role": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_client_id": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_application_name": "FTRS_LOG_PLACEHOLDER",
        "opt_ftrs_request_params": {
            "query_params": event.get("queryStringParameters") or {},
            "path_params": event.get("pathParams") or {},
            "request_context": event.get("requestContext") or {},
        },
    }
