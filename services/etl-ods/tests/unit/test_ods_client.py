import os
from http import HTTPStatus
from unittest.mock import patch

import pytest
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from producer.ods_client import get_base_ods_terminology_api_url, make_ods_request


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "dev",
        "ODS_URL": "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
    },
)
def test_get_base_ods_terminology_api_url_non_local() -> None:
    """Test get_base_ods_terminology_api_url returns ODS_URL from environment."""
    get_base_ods_terminology_api_url.cache_clear()
    result = get_base_ods_terminology_api_url()
    assert (
        result
        == "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )


@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "LOCAL_ODS_URL": "http://localhost:8080/ods-api",
    },
)
def test_get_base_ods_terminology_api_url_local() -> None:
    """Test get_base_ods_terminology_api_url returns LOCAL_ODS_URL for local environment."""
    get_base_ods_terminology_api_url.cache_clear()
    result = get_base_ods_terminology_api_url()
    assert result == "http://localhost:8080/ods-api"


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "local"},
    clear=True,
)
def test_get_base_ods_terminology_api_url_local_fallback() -> None:
    """Test get_base_ods_terminology_api_url falls back to int URL when LOCAL_ODS_URL is not set."""
    get_base_ods_terminology_api_url.cache_clear()
    result = get_base_ods_terminology_api_url()
    assert (
        result
        == "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization"
    )


@patch.dict(
    os.environ,
    {"ENVIRONMENT": "dev"},
    clear=True,
)
def test_get_base_ods_terminology_api_url_missing_env_var() -> None:
    """Test get_base_ods_terminology_api_url raises KeyError when ODS_URL is not set."""
    get_base_ods_terminology_api_url.cache_clear()
    with pytest.raises(KeyError, match="ODS_URL environment variable is not set"):
        get_base_ods_terminology_api_url()


def test_make_ods_request_success(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_ods_request for a successful request."""
    mocker.patch(
        "producer.ods_client.get_ods_terminology_api_key", return_value="ods-api-key"
    )

    mock_call = requests_mock.get(
        "https://api.example.com/Organization",
        json={"resourceType": "Bundle", "total": 0},
        status_code=HTTPStatus.OK,
    )

    result = make_ods_request("https://api.example.com/Organization")

    assert result == {
        "resourceType": "Bundle",
        "total": 0,
        "status_code": HTTPStatus.OK,
    }
    assert mock_call.last_request.headers["apikey"] == "ods-api-key"
    assert mock_call.last_request.headers["Accept"] == "application/fhir+json"


def test_make_ods_request_with_params(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_ods_request with query parameters."""
    mocker.patch(
        "producer.ods_client.get_ods_terminology_api_key", return_value="ods-api-key"
    )

    expected_total = 5
    mock_call = requests_mock.get(
        "https://api.example.com/Organization",
        json={"resourceType": "Bundle", "total": expected_total},
        status_code=HTTPStatus.OK,
    )

    result = make_ods_request(
        "https://api.example.com/Organization",
        params={"_lastUpdated": "2025-01-01", "_count": "100"},
    )

    assert result["total"] == expected_total
    assert mock_call.last_request.qs == {
        "_lastupdated": ["2025-01-01"],
        "_count": ["100"],
    }


def test_make_ods_request_with_json_data(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    """Test make_ods_request with JSON body."""
    mocker.patch(
        "producer.ods_client.get_ods_terminology_api_key", return_value="ods-api-key"
    )

    mock_call = requests_mock.post(
        "https://api.example.com/Organization",
        json={"id": "123"},
        status_code=HTTPStatus.CREATED,
    )

    result = make_ods_request(
        "https://api.example.com/Organization",
        method="POST",
        json={"name": "Test Org"},
    )

    assert result == {"id": "123", "status_code": HTTPStatus.CREATED}
    assert mock_call.last_request.headers["Content-Type"] == "application/fhir+json"
    assert mock_call.last_request.json() == {"name": "Test Org"}
