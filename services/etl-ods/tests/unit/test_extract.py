from unittest.mock import MagicMock, patch

import pytest
import requests

from pipeline.extract import (
    extract_contact,
    extract_display_name,
    extract_ods_code,
    extract_organisation_data,
    fetch_organisation_data,
    fetch_organisation_role,
    fetch_organisation_uuid,
    fetch_sync_data,
    make_request,
)
from pipeline.validators import RoleItem


@pytest.fixture
def mock_response() -> MagicMock:
    """Fixture to create a mock response object."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "Organisations": [{"OrgLink": "https://example.com/organisations/ABC123"}]
    }
    return response


@patch("pipeline.extract.requests.get")
def test_make_request_success(mock_get: MagicMock, mock_response: MagicMock) -> None:
    mock_get.return_value = mock_response
    url = "https://example.com/api"
    result = make_request(url)
    assert result == mock_response.json.return_value
    mock_get.assert_called_once_with(url, params=None, timeout=20)


@patch("pipeline.extract.requests.get")
@patch.dict("os.environ", {"ORGANISATION_API_URL": "https://localhost:8001"})
def test_make_request_organisation_api_404_error(mock_get: MagicMock) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error"
    )
    mock_get.return_value = mock_response

    url = "https://localhost:8001/ods_code/ABC123"
    with pytest.raises(ValueError, match="Organisation not found in dos database"):
        make_request(url)

    mock_get.assert_called_once_with(url, params=None, timeout=20)


@patch("pipeline.extract.make_request")
def test_fetch_sync_data(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {
        "Organisations": [{"OrgLink": "https://example.com/organisations/ABC123"}]
    }
    date = "2025-05-14"
    result = fetch_sync_data(date)
    assert result == [{"OrgLink": "https://example.com/organisations/ABC123"}]
    mock_make_request.assert_called_once_with(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?",
        params={"LastChangeDate": date},
    )


@patch("pipeline.extract.make_request")
def test_fetch_organisation_data(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {"Organisation": {"Name": "Test Organisation"}}
    ods_code = "ABC123"
    result = fetch_organisation_data(ods_code)
    assert result == {"Name": "Test Organisation"}
    mock_make_request.assert_called_once_with(
        f"https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{ods_code}"
    )


@patch("pipeline.extract.make_request")
def test_fetch_organisation_role(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {"displayName": "Test Role"}
    roles = [
        RoleItem(id="123", primaryRole=True),
    ]

    result = fetch_organisation_role(roles)
    assert result == {"displayName": "Test Role"}
    mock_make_request.assert_called_once_with(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/123"
    )


@patch("pipeline.extract.make_request")
@patch.dict("os.environ", {"ORGANISATION_API_URL": "https://localhost:8001"})
def test_fetch_organisation_uuid(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {"id": "UUID123"}
    ods_code = "ABC123"
    result = fetch_organisation_uuid(ods_code)
    assert result == "UUID123"
    mock_make_request.assert_called_once_with(
        f"https://localhost:8001/ods_code/{ods_code}"
    )


def test_extract_organisation_data() -> None:
    payload = {
        "Name": "Test Organisation",
        "Status": "Active",
        "Roles": [{"id": "RO123"}],
        "Contacts": [{"type": "tel", "value": "123456789"}],
        "Other": "Data",
    }
    result = extract_organisation_data(payload)
    assert result == {
        "Name": "Test Organisation",
        "Status": "Active",
        "Roles": [{"id": "RO123"}],
        "Contacts": [{"type": "tel", "value": "123456789"}],
    }


def test_extract_display_name() -> None:
    payload = {
        "Roles": [
            {"id": "RO123", "primaryRole": "true", "displayName": "Test Role"},
            {"id": "RO456"},
        ]
    }
    result = extract_display_name(payload)
    assert result == {"displayName": "Test Role"}


def test_extract_contact() -> None:
    payload = {
        "Contacts": {
            "Contact": [
                {"type": "tel", "value": "123456789"},
                {"type": "email", "value": "test@example.com"},
            ],
        }
    }
    result = extract_contact(payload)
    assert result == {"type": "tel", "value": "123456789"}


def test_extract_ods_code() -> None:
    link = "https://example.com/organisations/ABC123"
    result = extract_ods_code(link)
    assert result == "ABC123"
