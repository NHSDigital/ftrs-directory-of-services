import logging
from unittest.mock import MagicMock, patch

import pytest

from pipeline.extract import (
    extract_contact,
    extract_display_name,
    extract_ods_code,
    extract_organisation_data,
    fetch_organisation_data,
    fetch_organisation_role,
    fetch_organisation_uuid,
    fetch_sync_data,
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

    with pytest.raises(ValueError, match="No primary role found in the roles list."):
        fetch_organisation_role(roles)


@patch("pipeline.extract.make_request")
@patch.dict(
    "os.environ",
    {"ENVIRONMENT": "local", "LOCAL_CRUD_API_URL": "https://localhost:8001"},
)
def test_fetch_organisation_uuid(mock_make_request: MagicMock) -> None:
    mock_make_request.return_value = {"id": "UUID123"}
    ods_code = "ABC123"
    result = fetch_organisation_uuid(ods_code)
    assert result == "UUID123"
    mock_make_request.assert_called_once_with(
        f"https://localhost:8001/organisation/ods_code/{ods_code}", sign=True
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
