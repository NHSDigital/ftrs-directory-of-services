import logging
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


@pytest.fixture(autouse=True)
def set_log_level(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)


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
    url = "https://"
    result = make_request(url)
    assert result == mock_response.json.return_value
    mock_get.assert_called_once_with(url, params=None, timeout=20)


@patch("pipeline.extract.requests.get")
def test_make_request_request_exception(
    mock_get: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    """Test make_request for a request exception."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        make_request("http://")

    assert "Request to http:// failed: Connection error" in caplog.text


@patch("pipeline.extract.requests.get")
@patch.dict("os.environ", {"ORGANISATION_API_URL": "https://localhost:8001"})
def test_make_request_organisation_api_404_error(
    mock_get: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Not Found"
    )
    mock_get.return_value = mock_response

    url = "https://localhost:8001/ods_code/ABC123"
    with pytest.raises(ValueError, match="Test"):
        make_request(url)

    mock_get.assert_called_once_with(url, params=None, timeout=20)


@patch("pipeline.extract.requests.get")
def test_make_request_HTTP_error(
    mock_get: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "400 Bad Request"
    )
    mock_get.return_value = mock_response

    url = "ANY"
    with pytest.raises(requests.exceptions.HTTPError):
        make_request(url)

    mock_get.assert_called_once_with(url, params=None, timeout=20)
    assert "HTTP error occurred: 400 Bad Request - Status Code: 400" in caplog.text


@patch("pipeline.extract.make_request")
def test_fetch_sync_data(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {
        "Organisations": [{"OrgLink": "https:///organisations/ABC123"}]
    }
    date = "2025-05-14"
    result = fetch_sync_data(date)
    assert result == [{"OrgLink": "https:///organisations/ABC123"}]
    mock_make_request.assert_called_once_with(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?",
        params={"LastChangeDate": date},
    )


@patch("pipeline.extract.make_request")
def test_fetch_organisation_data(
    mock_make_request: MagicMock,
) -> None:
    mock_make_request.return_value = {"Organisation": {"Name": "Test Organisation"}}
    ods_code = "ABC123"
    result = fetch_organisation_data(ods_code)
    mock_make_request.assert_called_once_with(
        f"https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{ods_code}"
    )
    assert result == {"Name": "Test Organisation"}


@patch("pipeline.extract.make_request")
def test_fetch_organisation_data_no_organisations(
    mock_make_request: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    mock_make_request.return_value = {}
    ods_code = "ABC123"
    result = fetch_organisation_data(ods_code)
    mock_make_request.assert_called_once_with(
        f"https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/{ods_code}"
    )
    assert result == []
    assert (
        "No organisation found in the response for the given ODS code ABC123"
        in caplog.text
    )


@patch("pipeline.extract.make_request")
def test_fetch_organisation_role(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {"displayName": "Test Role"}
    roles = [
        RoleItem(id="123", primaryRole=True),
    ]

    result = fetch_organisation_role(roles)
    mock_make_request.assert_called_once_with(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/123"
    )
    assert result == {"displayName": "Test Role"}


def test_fetch_organisation_role_no_primary_role() -> None:
    roles = [RoleItem(id="123", primaryRole=False)]

    with pytest.raises(ValueError, match="Test2"):
        fetch_organisation_role(roles)


@patch("pipeline.extract.make_request")
@patch.dict("os.environ", {"ORGANISATION_API_URL": "https://localhost:8001/"})
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
        "Contacts": {
            "Contact": [{"type": "tel", "value": "123456789"}],
        },
        "Other": "Data",
    }
    result = extract_organisation_data(payload)
    assert result == {
        "Name": "Test Organisation",
        "Status": "Active",
        "Roles": [{"id": "RO123"}],
        "Contact": {"type": "tel", "value": "123456789"},
    }


def test_extract_organisation_data_invalid_payload(
    caplog: pytest.LogCaptureFixture,
) -> None:
    payload = {
        "name": "Test Organisation",
        "Status": "Active",
        "Roles": [{"id": "RO123"}],
        "Contacts": {
            "Contact": [{"type": "tel", "value": "123456789"}],
        },
    }

    extract_organisation_data(payload)
    assert "Missing key in organisation payload: Name" in caplog.text


def test_extract_display_name() -> None:
    payload = {
        "Roles": [
            {"id": "RO123", "primaryRole": "true", "displayName": "Test Role"},
            {"id": "RP456", "primaryRole": "false", "displayName": "Other Role"},
        ]
    }
    result = extract_display_name(payload)
    assert result == {"displayName": "Test Role"}


def test_extract_display_name_without_primary_role() -> None:
    payload = {
        "Roles": [
            {"id": "RO123", "primaryRole": "false", "displayName": "Test Role"},
            {"id": "RO456", "primaryRole": "false", "displayName": "Other Role"},
        ]
    }

    result = extract_display_name(payload)
    assert result is None


def test_extract_display_name_empty_roles() -> None:
    payload = {"Roles": []}

    result = extract_display_name(payload)
    assert result is None


def test_extract_display_name_missing_roles_key() -> None:
    payload = {}

    with pytest.raises(
        TypeError, match="Roles payload extraction failed: role is not a list"
    ):
        extract_display_name(payload)


def test_extract_display_name_roles_is_none() -> None:
    """Test extract_display_name when Roles is None."""
    payload = {"Roles": None}

    with pytest.raises(
        TypeError, match="Roles payload extraction failed: role is not a list"
    ):
        extract_display_name(payload)


def test_extract_contact_with_other_type() -> None:
    payload = {
        "Contacts": {
            "Contact": [
                {"type": "tel", "value": "123456789"},
                {"type": "other", "value": "test@example.com"},
            ],
        }
    }
    result = extract_contact(payload)
    assert result == {"type": "tel", "value": "123456789"}


def test_extract_contact_no_tel() -> None:
    payload = {
        "Contacts": {
            "Contact": [
                {"type": "email", "value": "test@example.com"},
            ]
        }
    }

    result = extract_contact(payload)
    assert result is None


def test_extract_contact_invalid_format(caplog: pytest.LogCaptureFixture) -> None:
    payload = {"Contacts": {"Contact": [None]}}

    with pytest.raises(Exception):
        extract_contact(payload)
    assert "Invalid contact format: None" in caplog.text


def test_extract_contact_with_no_contacts() -> None:
    payload = {}
    result = extract_contact(payload)
    assert result is None


def test_extract_ods_code() -> None:
    link = "https:///organisations/ABC123"
    result = extract_ods_code(link)
    assert result == "ABC123"


def test_extract_ods_code_failure(caplog: pytest.LogCaptureFixture) -> None:
    link = None
    with pytest.raises(Exception):
        extract_ods_code(link)
    assert "ODS code extraction failed" in caplog.text
