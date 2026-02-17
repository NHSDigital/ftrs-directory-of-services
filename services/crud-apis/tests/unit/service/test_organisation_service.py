from datetime import UTC, datetime
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from dos_ingest.service.organisation_service import OrganisationService
from fastapi import HTTPException
from freezegun import freeze_time
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from ftrs_data_layer.domain import Organisation, Telecom
from ftrs_data_layer.domain.auditevent import AuditEventType
from ftrs_data_layer.domain.enums import TelecomType
from tests.unit.fixtures.common import make_fhir_organisation_payload

TEST_PRODUCT_ID = "test-product-id"


def _stored_organisation(organisation_id: str) -> Organisation:
    return Organisation(
        id=organisation_id,
        identifier_ODS_ODSCode="ODS1",
        active=True,
        name="Test Org",
        telecom=[
            Telecom(type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True)
        ],
        endpoints=[],
        createdBy={"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
        lastUpdatedBy={"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
    )


@pytest.fixture
def organisation_service(
    org_repository_mock: MagicMock,
    logger_mock: MagicMock,
) -> OrganisationService:
    return OrganisationService(org_repository=org_repository_mock, logger=logger_mock)


def test_create_organisation_persists_new_record(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
    sample_organisation: Organisation,
) -> None:
    org_repository_mock.get_by_ods_code.return_value = None

    result = organisation_service.create_organisation(sample_organisation)

    assert result == sample_organisation
    org_repository_mock.create.assert_called_once_with(sample_organisation)


def test_create_organisation_raises_conflict_when_ods_code_exists(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
    sample_organisation: Organisation,
) -> None:
    org_repository_mock.get_by_ods_code.return_value = sample_organisation

    with pytest.raises(HTTPException) as exc_info:
        organisation_service.create_organisation(sample_organisation)

    assert exc_info.value.status_code == HTTPStatus.CONFLICT
    assert exc_info.value.detail == "Organisation with this ODS code already exists"


def test_process_update_requires_product_id(
    organisation_service: OrganisationService,
) -> None:
    payload = make_fhir_organisation_payload(
        organisation_id="00000000-0000-0000-0000-00000000000a"
    )

    with pytest.raises(OperationOutcomeException) as exc_info:
        organisation_service.process_organisation_update(
            organisation_id="00000000-0000-0000-0000-00000000000a",
            fhir_org=payload,
            nhse_product_id=None,
        )

    assert (
        exc_info.value.outcome["issue"][0]["diagnostics"]
        == "Product ID header is required for updating organisation"
    )


def test_process_update_raises_not_found_when_stored_record_is_missing(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
) -> None:
    org_repository_mock.get.return_value = None

    with pytest.raises(OperationOutcomeException) as exc_info:
        organisation_service.process_organisation_update(
            organisation_id="00000000-0000-0000-0000-00000000000a",
            fhir_org=make_fhir_organisation_payload(
                organisation_id="00000000-0000-0000-0000-00000000000a"
            ),
            nhse_product_id=TEST_PRODUCT_ID,
        )

    assert exc_info.value.outcome["issue"][0]["code"] == "not-found"


@freeze_time("2023-12-16T12:00:00Z")
def test_process_update_returns_false_when_no_fields_change(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
    sample_organisation: Organisation,
) -> None:
    org_repository_mock.get.return_value = sample_organisation

    result = organisation_service.process_organisation_update(
        organisation_id=str(sample_organisation.id),
        fhir_org=make_fhir_organisation_payload(
            organisation_id=str(sample_organisation.id)
        ),
        nhse_product_id=TEST_PRODUCT_ID,
    )

    assert result is False
    org_repository_mock.update.assert_not_called()


@freeze_time("2023-12-16T12:00:00Z")
def test_process_update_persists_supported_changes(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
    sample_organisation: Organisation,
) -> None:
    org_repository_mock.get.return_value = sample_organisation

    result = organisation_service.process_organisation_update(
        organisation_id=str(sample_organisation.id),
        fhir_org=make_fhir_organisation_payload(
            organisation_id=str(sample_organisation.id),
            name="Changed Name",
            telecom_value="020 7972 3272",
        ),
        nhse_product_id=TEST_PRODUCT_ID,
    )

    assert result is True
    org_repository_mock.update.assert_called_once()
    update_args = org_repository_mock.update.call_args.args
    assert update_args[0] == str(sample_organisation.id)

    saved = update_args[1]
    assert saved.name == "Changed Name"
    assert saved.telecom == [
        Telecom(type=TelecomType.PHONE, value="020 7972 3272", isPublic=True)
    ]
    assert saved.lastUpdatedBy.type == AuditEventType.app
    assert saved.lastUpdatedBy.value == TEST_PRODUCT_ID
    assert saved.lastUpdated == datetime(2023, 12, 16, 12, 0, 0, tzinfo=UTC)


def test_process_update_rejects_invalid_fhir_payload(
    organisation_service: OrganisationService,
) -> None:
    invalid_payload = {
        "id": "00000000-0000-0000-0000-00000000000a",
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ODS1",
            }
        ],
    }

    with pytest.raises(OperationOutcomeException) as exc_info:
        organisation_service.process_organisation_update(
            organisation_id="00000000-0000-0000-0000-00000000000a",
            fhir_org=invalid_payload,
            nhse_product_id=TEST_PRODUCT_ID,
        )

    assert exc_info.value.outcome["issue"][0]["code"] == "structure"


@pytest.mark.parametrize(
    ("telecom_system", "telecom_value", "expected_diagnostics"),
    [
        (
            "fax",
            "020 7972 3272",
            "invalid telecom type (system): fax",
        ),
        (
            "phone",
            "0300",
            "invalid phone number",
        ),
    ],
)
def test_process_update_rejects_invalid_telecom_values(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
    telecom_system: str,
    telecom_value: str,
    expected_diagnostics: str,
) -> None:
    organisation_id = "00000000-0000-0000-0000-00000000000a"
    org_repository_mock.get.return_value = _stored_organisation(organisation_id)

    with pytest.raises(OperationOutcomeException) as exc_info:
        organisation_service.process_organisation_update(
            organisation_id=organisation_id,
            fhir_org=make_fhir_organisation_payload(
                organisation_id=organisation_id,
                name="Changed Name",
                telecom_system=telecom_system,
                telecom_value=telecom_value,
            ),
            nhse_product_id=TEST_PRODUCT_ID,
        )

    assert expected_diagnostics in str(exc_info.value)


def test_get_by_ods_code_returns_record(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
    sample_organisation: Organisation,
) -> None:
    org_repository_mock.get_by_ods_code.return_value = sample_organisation

    result = organisation_service.get_by_ods_code("ODS1")

    assert result == sample_organisation
    org_repository_mock.get_by_ods_code.assert_called_once_with(ods_code="ODS1")


def test_get_by_ods_code_raises_not_found(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
) -> None:
    org_repository_mock.get_by_ods_code.return_value = None

    with pytest.raises(OperationOutcomeException) as exc_info:
        organisation_service.get_by_ods_code("UNKNOWN")

    assert exc_info.value.outcome["issue"][0]["code"] == "not-found"


def test_check_organisation_params_rejects_unexpected_keys(
    organisation_service: OrganisationService,
) -> None:
    with pytest.raises(OperationOutcomeException) as exc_info:
        organisation_service.check_organisation_params(
            {"identifier": "ODS1", "foo": "bar"}
        )

    assert exc_info.value.outcome["issue"][0]["code"] == "invalid"


def test_get_all_organisations_honours_limit_and_converts_dict_rows(
    organisation_service: OrganisationService,
    org_repository_mock: MagicMock,
) -> None:
    org_repository_mock.iter_records.return_value = [
        {
            "id": "00000000-0000-0000-0000-00000000000a",
            "identifier_ODS_ODSCode": "ODS1",
            "active": True,
            "name": "Test Org",
            "telecom": [{"type": "phone", "value": "0300 311 22 33", "isPublic": True}],
            "endpoints": [],
            "createdBy": {"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
            "lastUpdatedBy": {"type": "app", "value": "SYSTEM", "display": "SYSTEM"},
        }
    ]

    result = organisation_service.get_all_organisations(limit=25)

    org_repository_mock.iter_records.assert_called_once_with(max_results=25)
    assert len(result) == 1
    assert isinstance(result[0], Organisation)
