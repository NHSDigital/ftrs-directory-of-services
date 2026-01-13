from builtins import str
from datetime import UTC, date, datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_data_layer.domain import Organisation, Telecom
from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from ftrs_data_layer.domain.enums import OrganisationTypeCode, TelecomType
from ftrs_data_layer.domain.organisation import LegalDates
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

from organisations.app.models.organisation import LegalDateField
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
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
        id="d5a852ef-12c7-4014-b398-661716a63027",
        primary_role_code=OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        non_primary_role_codes=[OrganisationTypeCode.GP_PRACTICE_ROLE_CODE],
        legalDates=LegalDates(start=date(2020, 1, 15), end=date(2025, 12, 31)),
    )
    payload = MagicMock(
        model_dump=lambda: {
            "identifier_ODS_ODSCode": "ABC123",
            "active": True,
            "name": "Test Organisation",
            "telecom": [
                {"type": TelecomType.PHONE, "value": "0300 311 22 33", "isPublic": True}
            ],
            "endpoints": [],
            "legalDates": {"start": date(2020, 1, 15), "end": date(2025, 12, 31)},
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
        telecom=[Telecom(type="phone", value="0300 311 22 33", isPublic=True)],
        endpoints=[],
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
        id="d5a852ef-12c7-4014-b398-661716a63027",
        legalDates={"start": "2020-01-15", "end": "2025-12-31"},
    )
    updates = {
        "name": "Updated Org Name",
        "telecom": [
            Telecom(type="phone", value="020 7972 3272", isPublic=True),
            Telecom(type="email", value="test@nhs.net", isPublic=True),
        ],
        "lastUpdatedBy": {
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        "legalDates": {
            "start": "2020-01-15",
        },
    }
    service = make_service()
    with patch(
        "organisations.app.services.organisation_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value = FIXED_MODIFIED_TIME
        service._apply_updates(organisation, updates)
    assert organisation.name == "Updated Org Name"
    assert organisation.telecom == [
        Telecom(type="phone", value="020 7972 3272", isPublic=True),
        Telecom(type="email", value="test@nhs.net", isPublic=True),
    ]
    assert organisation.lastUpdatedBy == {
        "type": "user",
        "value": "INGRESS_API_ID",
        "display": "FtRS Ingress API",
    }
    assert organisation.lastUpdated == FIXED_MODIFIED_TIME


@freeze_time(FIXED_MODIFIED_TIME)
def test_get_outdated_fields_with_changes(caplog: pytest.LogCaptureFixture) -> None:
    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
        id="d5a852ef-12c7-4014-b398-661716a63027",
        legalDates=LegalDates(start=date(2020, 1, 15), end=date(2025, 12, 31)),
    )
    payload = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=False,
        name="Updated Organisation",
        telecom=[Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True)],
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        primary_role_code=OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        non_primary_role_codes=[OrganisationTypeCode.GP_PRACTICE_ROLE_CODE],
        legalDates=LegalDates(start=date(2021, 1, 1), end=date(2026, 12, 31)),
    )
    service = make_service()
    with caplog.at_level("INFO"):
        result = service._get_outdated_fields(organisation, payload)

        # Extract legalDates from result for separate comparison
        result_legal_dates = result.pop("legalDates", None)
        expected_legal_dates = {"start": date(2021, 1, 1), "end": date(2026, 12, 31)}

        # Compare legalDates separately
        assert result_legal_dates == expected_legal_dates

        assert result == {
            "active": False,
            "name": "Updated Organisation",
            "telecom": [
                {"type": TelecomType.EMAIL, "value": "test@nhs.net", "isPublic": True}
            ],
            "lastUpdatedBy": AuditEvent(
                type=AuditEventType.user,
                value="INGRESS_API_ID",
                display="FtRS Ingress API",
            ),
            "lastUpdated": FIXED_MODIFIED_TIME,
            "primary_role_code": OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
            "non_primary_role_codes": [OrganisationTypeCode.GP_PRACTICE_ROLE_CODE],
        }
        assert (
            "Computed outdated fields: ['active', 'name', 'primary_role_code', 'non_primary_role_codes', 'telecom', 'legalDates'] for organisation d5a852ef-12c7-4014-b398-661716a63027"
            in caplog.text
        )


def test_creates_organisation_when_valid_data_provided() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = None
    org_repository.create = MagicMock()

    organisation = Organisation(
        identifier_ODS_ODSCode="ABC123",
        active=True,
        name="Test Organisation",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )

    service = make_service(org_repository=org_repository)
    result = service.create_organisation(organisation)

    assert result == organisation
    org_repository.create.assert_called_once_with(organisation)
    assert result.createdBy == AuditEvent(
        type=AuditEventType.user,
        value="INGRESS_API_ID",
        display="FtRS Ingress API",
    )
    assert result.identifier_ODS_ODSCode == "ABC123"
    assert result.telecom == [
        Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
    ]
    assert result.active is True
    assert result.name == "Test Organisation"


def test_raises_error_when_organisation_already_exists() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = Organisation(
        identifier_ODS_ODSCode="M81094",
        name="Existing Organisation",
        active=True,
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
    )

    organisation = Organisation(
        identifier_ODS_ODSCode="M81094",
        name="Test Organisation",
        active=True,
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
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
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
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
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Test Org",
        "telecom": [{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
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
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("INFO"):
        result = service.process_organisation_update(organisation_id, fhir_org)
        assert result is True
        org_repository.update.assert_called_once()
        assert f"Successfully updated organisation {organisation_id}" in caplog.text


def test_process_organisation_update_missing_required_field() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
    }
    with pytest.raises(OperationOutcomeException) as exc_info:
        service.process_organisation_update(organisation_id, fhir_org)

    assert exc_info.value.outcome["issue"][0]["code"] == "structure"
    assert exc_info.value.outcome["issue"][0]["severity"] == "error"
    assert (
        "Missing required field 'resourceType'"
        in exc_info.value.outcome["issue"][0]["diagnostics"]
    )


def test_process_organisation_update_invalid_fhir_structure() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    invalid_fhir = {
        "id": organisation_id,
        # Missing required resourceType field
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Test Org",
        "telecom": [{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
    }
    with pytest.raises(OperationOutcomeException) as exc_info:
        service.process_organisation_update(organisation_id, invalid_fhir)

    assert exc_info.value.outcome["issue"][0]["code"] == "structure"
    assert exc_info.value.outcome["issue"][0]["severity"] == "error"
    assert "resourceType" in exc_info.value.outcome["issue"][0]["diagnostics"]


def test_process_organisation_update_with_invalid_phone_number(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"system": "phone", "value": "0300", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("ERROR"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            service.process_organisation_update(organisation_id, fhir_org)
        assert (
            "Validation failed for the following resources: Telecom value field contains an invalid phone number: 0300"
            in str(exc_info.value)
        )


def test_process_organisation_update_with_invalid_email_number(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"system": "email", "value": "invalid-email", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("ERROR"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            service.process_organisation_update(organisation_id, fhir_org)
        assert (
            "Validation failed for the following resources: Telecom value field contains an invalid email address: invalid-email"
            in str(exc_info.value)
        )


def test_process_organisation_update_with_invalid_url(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"system": "url", "value": "nhs.net", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("ERROR"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            service.process_organisation_update(organisation_id, fhir_org)
        assert (
            "Validation failed for the following resources: Telecom value field contains an invalid url: nhs.net"
            in str(exc_info.value)
        )


def test_process_organisation_update_with_invalid_char_in_phone_number(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"system": "phone", "value": "@0300 311 22 33", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("ERROR"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            service.process_organisation_update(organisation_id, fhir_org)
        assert (
            "Validation failed for the following resources: Telecom value field contains an invalid phone number: @0300 311 22 33"
            in str(exc_info.value)
        )


def test_process_organisation_update_with_invalid_no_telecom_system(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"value": "0300", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("ERROR"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            service.process_organisation_update(organisation_id, fhir_org)

        assert (
            "Validation failed for the following resource: Telecom type (system) cannot be None or empty"
            in str(exc_info.value)
        )


def test_process_organisation_update_with_invalid_telecom_system_fax(
    caplog: pytest.LogCaptureFixture,
) -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    fhir_org = {
        "resourceType": "Organization",
        "id": organisation_id,
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {"system": "https://fhir.nhs.uk/Id/ods-organization-code", "value": "ODS1"}
        ],
        "active": True,
        "name": "Changed Name",
        "telecom": [{"system": "fax", "value": "020 7972 3272", "use": "work"}],
    }
    stored_organisation = Organisation(
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True)],
        endpoints=[],
        id=organisation_id,
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.get.return_value = stored_organisation
    with caplog.at_level("ERROR"):
        with pytest.raises(OperationOutcomeException) as exc_info:
            service.process_organisation_update(organisation_id, fhir_org)

        assert (
            "Validation failed for the following resource: invalid telecom type (system): fax"
            in str(exc_info.value)
        )


def test_get_by_ods_code_success() -> None:
    org = Organisation(
        identifier_ODS_ODSCode="ODS12345",
        active=True,
        name="Test Org",
        telecom=[Telecom(type="phone", value="0300 311 22 33", isPublic=True)],
        endpoints=[],
        id="00000000-0000-0000-0000-00000000000a",
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = org
    service = make_service(org_repository=org_repository)
    result = service.get_by_ods_code("ODS12345")
    assert result == org
    org_repository.get_by_ods_code.assert_called_once_with(ods_code="ODS12345")


def test_get_by_ods_code_not_found() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org_repository.get_by_ods_code.return_value = None
    service = make_service(org_repository=org_repository)
    with pytest.raises(OperationOutcomeException) as exc_info:
        service.get_by_ods_code("ODS99999")
    assert exc_info.value.outcome["issue"][0]["code"] == "not-found"
    assert "not found" in exc_info.value.outcome["issue"][0]["diagnostics"].lower()


def test_check_organisation_params_valid() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    service.check_organisation_params({"identifier": "ODS12345"})


def test_check_organisation_params_invalid() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    service = make_service(org_repository=org_repository)
    with pytest.raises(OperationOutcomeException) as exc_info:
        service.check_organisation_params({"identifier": "ODS12345", "foo": "bar"})
    assert exc_info.value.outcome["issue"][0]["code"] == "invalid"
    assert (
        "unexpected query parameter"
        in exc_info.value.outcome["issue"][0]["diagnostics"].lower()
    )


def test_get_all_organisations() -> None:
    org_repository = MagicMock(spec=AttributeLevelRepository)
    org1 = Organisation(
        identifier_ODS_ODSCode="ODS12345",
        active=True,
        name="Test Org",
        telecom=[Telecom(type="phone", value="0300 311 22 33", isPublic=True)],
        endpoints=[],
        id="00000000-0000-0000-0000-00000000000a",
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org2 = Organisation(
        identifier_ODS_ODSCode="ODS12345",
        active=True,
        name="Test Org",
        telecom=[Telecom(type="phone", value="020 7972 3272", isPublic=True)],
        endpoints=[],
        id="00000000-0000-0000-0000-00000000000a",
        createdBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        createdTime=FIXED_CREATED_TIME,
        lastUpdatedBy={
            "type": "user",
            "value": "INGRESS_API_ID",
            "display": "FtRS Ingress API",
        },
        lastUpdated=FIXED_MODIFIED_TIME,
    )
    org_repository.iter_records.return_value = [org1, org2]
    service = make_service(org_repository=org_repository)
    result = service.get_all_organisations()
    assert result == [org1, org2]
    org_repository.iter_records.assert_called_once()


def test_extract_date_field_from_enum() -> None:
    service = OrganisationService(org_repository=MagicMock())
    legal_dates = {"start": "2020-01-01", "end": "2025-12-31"}

    assert (
        service._extract_date_field(legal_dates, LegalDateField.START) == "2020-01-01"
    )
    assert service._extract_date_field(legal_dates, LegalDateField.END) == "2025-12-31"


def test_extract_date_field_not_in_enum() -> None:
    service = OrganisationService(org_repository=MagicMock())
    legal_dates = {"start": "2020-01-01", "end": "2025-12-31"}
    with pytest.raises(TypeError):
        service._extract_date_field(legal_dates, "foo")
