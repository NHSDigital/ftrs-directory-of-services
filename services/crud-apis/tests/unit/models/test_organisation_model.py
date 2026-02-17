import pytest
from dos_ingest.models.organisation import (
    OrganisationUpdatePayload,
    OrganizationQueryParams,
)
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import ValidationError


def _base_payload() -> dict:
    return {
        "id": "00000000-0000-0000-0000-00000000000a",
        "resourceType": "Organization",
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
    }


def test_organisation_update_payload_accepts_valid_payload() -> None:
    payload = OrganisationUpdatePayload(**_base_payload())

    assert payload.resourceType == "Organization"
    assert payload.identifier[0].value == "ABC123"


def test_organisation_update_payload_rejects_null_active() -> None:
    payload = _base_payload()
    payload["active"] = None

    with pytest.raises(ValidationError, match="Active field is required and cannot be null"):
        OrganisationUpdatePayload(**payload)


def test_organisation_update_payload_rejects_invalid_identifier_format() -> None:
    payload = _base_payload()
    payload["identifier"] = [
        {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "BAD!",
        }
    ]

    with pytest.raises(ValidationError, match="invalid ODS code format"):
        OrganisationUpdatePayload(**payload)


def test_organisation_update_payload_rejects_missing_ods_identifier() -> None:
    payload = _base_payload()
    payload["identifier"] = [{"system": "other-system", "value": "ABC123"}]

    with pytest.raises(ValidationError, match="at least one identifier must have system"):
        OrganisationUpdatePayload(**payload)


def test_organisation_update_payload_rejects_invalid_extension_url() -> None:
    payload = _base_payload()
    payload["extension"] = [
        {
            "url": "https://invalid.example/Extension",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                "code": "RO177",
                                "display": "RO177",
                            }
                        ]
                    },
                }
            ],
        }
    ]

    with pytest.raises(OperationOutcomeException, match="Invalid extension URL"):
        OrganisationUpdatePayload(**payload)


def test_organization_query_params_extracts_uppercase_ods_code() -> None:
    query = OrganizationQueryParams(identifier="odsOrganisationCode|abc123")

    assert query.ods_code == "ABC123"


def test_organization_query_params_rejects_bad_system() -> None:
    with pytest.raises(OperationOutcomeException, match="Invalid identifier system"):
        OrganizationQueryParams(identifier="wrongSystem|ABC123")
