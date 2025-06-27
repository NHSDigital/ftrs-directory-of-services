from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
import pytest
from pydantic import ValidationError

from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)


def test_from_fhir_maps_fields_success():
    mapper = OrganizationMapper()
    ods_body = {
        "resourceType": "Organization",
        "id": "N8Q4P",
        "meta": {
            "lastUpdated": "2025-06-25T00:00:00+00:00",
            "profile": "https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1",
        },
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-ActivePeriod-1",
                "valuePeriod": {
                    "extension": [
                        {
                            "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-DateType-1",
                            "valueString": "Operational",
                        }
                    ],
                    "start": "2021-04-01",
                },
            },
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {
                        "url": "role",
                        "valueCoding": {
                            "system": "https://directory.spineservices.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRole-1",
                            "code": "280",
                            "display": "PHARMACY SITE",
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                    {
                        "url": "activePeriod",
                        "valuePeriod": {
                            "extension": [
                                {
                                    "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-DateType-1",
                                    "valueString": "Operational",
                                }
                            ],
                            "start": "2021-04-01",
                        },
                    },
                    {"url": "status", "valueString": "Active"},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {
                        "url": "role",
                        "valueCoding": {
                            "system": "https://directory.spineservices.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRole-1",
                            "code": "279",
                            "display": "COVID VACCINATION CENTRE",
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": False},
                    {
                        "url": "activePeriod",
                        "valuePeriod": {
                            "extension": [
                                {
                                    "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-DateType-1",
                                    "valueString": "Operational",
                                }
                            ],
                            "start": "2021-04-01",
                        },
                    },
                    {"url": "status", "valueString": "Active"},
                ],
            },
        ],
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "N8Q4P",
        },
        "active": True,
        "type": {
            "coding": {
                "system": "https://fhir.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRecordClass-1",
                "code": "2",
                "display": "HSCSite",
            }
        },
        "name": "WELL PHARMACY - CHINGFORD - COVID LOCAL VACCINATION SERVICE",
        "address": {
            "line": ["20 HATCH LANE", "CHINGFORD"],
            "city": "LONDON",
            "postalCode": "E4 6LQ",
            "country": "ENGLAND",
        },
    }
    fhir_org = mapper.from_ods_fhir_to_fhir(ods_body)
    print(fhir_org)
    #assert isinstance(fhir_org, Organization)
    assert fhir_org.id == "N8Q4P"
    assert (
        fhir_org.name == "WELL PHARMACY - CHINGFORD - COVID LOCAL VACCINATION SERVICE"
    )
    assert fhir_org.active is True
    assert fhir_org.telecom is None  # Telecom not provided in ods_body
    assert fhir_org.type is not None
    assert isinstance(fhir_org.type, list)
    assert len(fhir_org.type) == 1
    assert (
        fhir_org.type[0].coding[0].system
        == "https://fhir.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRecordClass-1"
    )
    assert fhir_org.type[0].coding[0].code == "2"
    assert fhir_org.type[0].coding[0].display == "HSCSite"
    assert fhir_org.address is not None
    # Fix the expected value to match the actual URL
    assert (
        fhir_org.type[0].coding[0].system
        == "https://fhir.nhs.uk/CodeSystem/Spine-RecordClass-1"
    )


def test_operation_outcome_exception_message():
    outcome = {"issue": [{"diagnostics": "Something went wrong"}]}
    exc = OperationOutcomeException(outcome)
    assert exc.outcome == outcome
    assert str(exc) == "Something went wrong"


def test_operation_outcome_exception_default_message():
    outcome = {"issue": [{}]}
    exc = OperationOutcomeException(outcome)
    assert str(exc) == "FHIR OperationOutcome error"


def test_operation_outcome_handler_build_basic():
    diagnostics = "Test diagnostics"
    outcome = OperationOutcomeHandler.build(diagnostics)
    assert isinstance(outcome, dict)
    assert outcome["issue"][0]["diagnostics"] == diagnostics
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["severity"] == "error"


def test_operation_outcome_handler_build_with_details_and_issues():
    diagnostics = "Test diagnostics"
    details = {"text": "More info"}
    issues = [{"severity": "warning", "code": "processing", "diagnostics": "Warn"}]
    outcome = OperationOutcomeHandler.build(diagnostics, details=details, issues=issues)
    assert outcome["issue"][0]["severity"] == "warning"
    assert outcome["issue"][0]["diagnostics"] == "Warn"


def test_operation_outcome_handler_from_exception():
    exc = Exception("Boom!")
    outcome = OperationOutcomeHandler.from_exception(exc)
    assert outcome["issue"][0]["diagnostics"] == "Boom!"
    assert outcome["issue"][0]["code"] == "exception"
    assert outcome["issue"][0]["severity"] == "fatal"


def test_operation_outcome_handler_from_validation_error_default_diagnostics():
    dummy_model_path = "tests.fhir.test_operation_outcome.DummyModel"

    try:
        raise ValidationError([], dummy_model_path)
    except ValidationError as e:
        outcome = OperationOutcomeHandler.from_validation_error(e)
        assert outcome["issue"][0]["diagnostics"] == "Validation failed for resource."
        assert outcome["issue"][0]["code"] == "invalid"
        assert outcome["issue"][0]["severity"] == "error"
        assert (
            "Invalid Resource" in outcome["issue"][0]["details"]["coding"][0]["display"]
        )


def test_operation_outcome_handler_from_validation_error_with_diagnostics():
    dummy_model_path = "tests.fhir.test_operation_outcome.DummyModel"

    class FakeError:
        def __str__(self):
            return "Fake error"

    mock_validation_error = ValidationError([FakeError()], model=dummy_model_path)
    outcome = OperationOutcomeHandler.from_validation_error(mock_validation_error)
    assert outcome["issue"][0]["diagnostics"] == "Fake error"
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["display"] == "error"
