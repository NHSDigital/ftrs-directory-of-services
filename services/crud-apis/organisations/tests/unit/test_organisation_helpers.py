from datetime import UTC, datetime
from http import HTTPStatus
from typing import NoReturn
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from organisations.app.services.organisation_helpers import (
    apply_updates,
    create_organisation,
    get_outdated_fields,
)


def test_get_outdated_fields_no_changes() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="GP Practice",
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
            "type": "GP Practice",
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
        type="GP Practice",
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
        type="GP Practice",
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
        type="GP Practice",
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
            "type": "GP Practice",
            "endpoints": [],
        }
    )

    result = get_outdated_fields(organisation, payload)

    assert result == {
        "modified_by": "UserB",
    }


def test_creates_organisation_when_valid_data_provided() -> NoReturn:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = None
    org_repository.create = MagicMock()

    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="GP Practice",
        endpoints=[],
    )
    result = create_organisation(organisation, org_repository)

    assert result == organisation
    org_repository.create.assert_called_once_with(organisation)
    assert result.createdBy == "SYSTEM"
    assert result.identifier_ODS_ODSCode == "ABC123"
    assert result.active is True
    assert result.name == "Test Organisation"


def test_raises_error_when_organisation_already_exists() -> NoReturn:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = Organisation(
        identifier_ODS_ODSCode="M81094",
        name="Existing Organisation",
        active=True,
        type="GP Practice",
        endpoints=[],
    )

    organisation = Organisation(
        identifier_ODS_ODSCode="M81094",
        name="Test Organisation",
        active=True,
        telecom="12345",
        type="GP Practice",
        endpoints=[],
    )

    with pytest.raises(HTTPException) as exc_info:
        create_organisation(organisation, org_repository)

    assert exc_info.value.status_code == HTTPStatus.CONFLICT
    assert exc_info.value.detail == "Organisation with this ODS code already exists"


def test_generates_new_id_when_id_already_exists() -> NoReturn:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = None
    org_repository.create = MagicMock()

    existing_id = uuid4()
    organisation = Organisation(
        id=existing_id,
        identifier_ODS_ODSCode="M81094",
        name="Test Organisation",
        active=True,
        type="GP Practice",
        endpoints=[],
    )

    result = create_organisation(organisation, org_repository)

    assert result.id != existing_id
    org_repository.create.assert_called_once_with(organisation)
