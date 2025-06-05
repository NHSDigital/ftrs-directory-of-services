from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from ftrs_data_layer.models import Organisation

from organisations.app.services.organisation_helpers import (
    apply_updates,
    get_outdated_fields,
)


def test_get_outdated_fields_no_changes() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="Test Type",
        endpoints=[],
        createdBy="ROBOT",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="ROBOT",
        modifiedDateTime="2023-11-01T00:00:00Z",
        id="d5a852ef-12c7-4014-b398-661716a63027",
    )
    payload = MagicMock(
        model_dump=lambda: {
            "identifier_ODS_ODSCode": "ABC123",
            "active": True,
            "name": "Test Organisation",
            "telecom": "12345",
            "type": "Test Type",
            "endpoints": [],
        }
    )

    result = get_outdated_fields(organisation, payload)

    assert result == {}


def test_apply_updates_with_modified_by_and_two_fields() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="Test Type",
        endpoints=[],
        createdBy="ROBOT",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="ROBOT",
        modifiedDateTime="2023-11-01T00:00:00Z",
        id="d5a852ef-12c7-4014-b398-661716a63027",
    )
    updates = {
        "name": "Updated Org Name",
        "telecom": "99999",
        "modified_by": "UserX",
    }

    with patch(
        "organisations.app.services.organisation_helpers.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)
        apply_updates(organisation, updates)

    assert organisation.name == "Updated Org Name"
    assert organisation.telecom == "99999"
    assert organisation.modifiedBy == "UserX"
    assert organisation.modifiedDateTime == datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)


def test_get_outdated_fields_with_changes() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="Test Type",
        endpoints=[],
        createdBy="ROBOT",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedBy="ROBOT",
        modifiedDateTime="2023-11-01T00:00:00Z",
        id="d5a852ef-12c7-4014-b398-661716a63027",
    )
    payload = MagicMock(
        model_dump=lambda: {
            "identifier_ODS_ODSCode": "DEF456",
            "active": False,
            "name": "Updated Organisation",
            "telecom": "67890",
            "type": "Updated Type",
        }
    )

    result = get_outdated_fields(organisation, payload)

    assert result == {
        "identifier_ODS_ODSCode": "DEF456",
        "active": False,
        "name": "Updated Organisation",
        "telecom": "67890",
        "type": "Updated Type",
    }


def test_get_outdated_fields_modified_by_field_only() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="Test Type",
        endpoints=[],
        createdBy="ROBOT",
        createdDateTime="2023-10-01T00:00:00Z",
        modifiedDateTime="2023-11-01T00:00:00Z",
        id="d5a852ef-12c7-4014-b398-661716a63027",
        modifiedBy="UserA",
    )
    payload = MagicMock(
        model_dump=lambda: {
            "modified_by": "UserB",
            "identifier_ODS_ODSCode": "ABC123",
            "active": True,
            "name": "Test Organisation",
            "telecom": "12345",
            "type": "Test Type",
            "endpoints": [],
        }
    )

    result = get_outdated_fields(organisation, payload)

    assert result == {
        "modified_by": "UserB",
    }
