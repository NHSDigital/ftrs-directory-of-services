from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle


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
            "NHSD-Correlation-ID": "correlation_id",
            "NHSD-Request-ID": "request_id",
            "NHSD-Message-Id": "message_id",
            # One-time log field headers
            "NHSD-Api-Version": "v0.0.0",
            "NHSD-End-User-Role": "Clinician",
            "NHSD-Client-Id": "client_id",
            "NHSD-Connecting-Party-App-Name": "111-online",
        },
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{ods_code}",
            "_revinclude": "Endpoint:organization",
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
        "opt_dos_environment": "Development",
        "opt_dos_api_version": "v0.0.0",
        "opt_dos_lambda_version": "0.0.1",
        "opt_dos_end_user_role": "Clinician",
        "opt_dos_client_id": "client_id",
        "opt_dos_application_name": "111-online",
        "opt_dos_request_params": {
            "query_params": event.get("queryStringParameters") or {},
            "path_params": event.get("pathParameters") or {},
            "request_context": event.get("requestContext") or {},
        },
    }
