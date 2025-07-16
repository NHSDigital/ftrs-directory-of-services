from datetime import UTC, datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from ftrs_data_layer.models import Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from organisations.app.services.organisation_service import OrganisationService

FIXED_CREATED_TIME = datetime(2023, 12, 15, 12, 0, 0, tzinfo=UTC)
FIXED_MODIFIED_TIME = datetime(2023, 12, 16, 12, 0, 0, tzinfo=UTC)


def make_service(
    org_repository: AttributeLevelRepository | None = None,
    logger: object | None = None,
    mapper: object | None = None,
) -> OrganisationService:
    if org_repository is None:
        org_repository = MagicMock(spec=AttributeLevelRepository)
    return OrganisationService(
        org_repository=org_repository, logger=logger, mapper=mapper
    )


@freeze_time(FIXED_MODIFIED_TIME)
def test_get_outdated_fields_no_changes() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="GP Practice",
        endpoints=[],
        createdBy="ROBOT",
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="ROBOT",
        modifiedDateTime=FIXED_MODIFIED_TIME,
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
    service = make_service()
    result = service._get_outdated_fields(organisation, payload)
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
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="ROBOT",
        modifiedDateTime=FIXED_MODIFIED_TIME,
        id="d5a852ef-12c7-4014-b398-661716a63027",
    )
    updates = {
        "name": "Updated Org Name",
        "telecom": "99999",
        "modified_by": "UserX",
    }
    service = make_service()
    with patch(
        "organisations.app.services.organisation_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = FIXED_MODIFIED_TIME
        service._apply_updates(organisation, updates)
    assert organisation.name == "Updated Org Name"
    assert organisation.telecom == "99999"
    assert organisation.modifiedBy == "UserX"
    assert organisation.modifiedDateTime == FIXED_MODIFIED_TIME


@freeze_time(FIXED_MODIFIED_TIME)
def test_get_outdated_fields_with_changes() -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom="12345",
        type="GP Practice",
        endpoints=[],
        createdBy="ROBOT",
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="ROBOT",
        modifiedDateTime=FIXED_MODIFIED_TIME,
        id="d5a852ef-12c7-4014-b398-661716a63027",
    )
    payload = Organisation(
        identifier_ODS_ODSCode="DEF456",
        active=False,
        name="Updated Organisation",
        telecom="67890",
        type="Updated Type",
        modifiedBy="ETL_ODS_PIPELINE",
    )
    service = make_service()
    result = service._get_outdated_fields(organisation, payload)
    assert result == {
        "identifier_ODS_ODSCode": "DEF456",
        "active": False,
        "name": "Updated Organisation",
        "telecom": "67890",
        "type": "Updated Type",
        "modified_by": "ETL_ODS_PIPELINE",
        "modifiedDateTime": FIXED_MODIFIED_TIME,
    }


def test_creates_organisation_when_valid_data_provided() -> None:
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
        createdBy="ROBOT",
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="ROBOT",
        modifiedDateTime=FIXED_MODIFIED_TIME,
    )

    service = make_service(org_repository=org_repository)
    result = service.create_organisation(organisation)

    assert result == organisation
    org_repository.create.assert_called_once_with(organisation)
    assert result.createdBy == "ROBOT"
    assert result.identifier_ODS_ODSCode == "ABC123"
    assert result.active is True
    assert result.name == "Test Organisation"


def test_raises_error_when_organisation_already_exists() -> None:
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
    service = make_service(org_repository=org_repository)
    with pytest.raises(HTTPException) as exc_info:
        service.create_organisation(organisation)
    assert exc_info.value.status_code == HTTPStatus.CONFLICT
    assert exc_info.value.detail == "Organisation with this ODS code already exists"


def test_generates_new_id_when_id_already_exists() -> None:
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
        createdBy="ROBOT",
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="ROBOT",
        modifiedDateTime=FIXED_MODIFIED_TIME,
    )

    service = make_service(org_repository=org_repository)
    result = service.create_organisation(organisation)

    assert result.id != existing_id
    org_repository.create.assert_called_once_with(organisation)


def test_process_organisation_update_no_changes(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Test Org",
        "type": [
            {
                "coding": [
                    {"system": "TO-DO", "code": "GP Practice", "display": "GP Practice"}
                ],
                "text": "GP Practice",
            }
        ],
        "telecom": [{"system": "phone", "value": "12345", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom="12345",
        type="GP Practice",
        endpoints=[],
        id=organisation_id,
        createdBy="test",
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="ODS_ETL_PIPELINE",
        modifiedDateTime=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("INFO"):
        result = service.process_organisation_update(organisation_id, fhir_org)
        assert result is False
        assert f"No changes detected for organisation {organisation_id}" in caplog.text


def test_process_organisation_update_with_changes(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "type": [
            {
                "coding": [
                    {"system": "TO-DO", "code": "GP Practice", "display": "GP Practice"}
                ],
                "text": "GP Practice",
            }
        ],
        "telecom": [{"system": "phone", "value": "12345", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom="12345",
        type="GP Practice",
        endpoints=[],
        id=organisation_id,
        createdBy="test",
        createdDateTime=FIXED_CREATED_TIME,
        modifiedBy="test",
        modifiedDateTime=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("INFO"):
        result = service.process_organisation_update(organisation_id, fhir_org)
        assert result is True
        org_repository.update.assert_called_once()
        assert f"Successfully updated organisation {organisation_id}" in caplog.text
