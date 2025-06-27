import pytest
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_data_layer.models import Organisation
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding


def make_org(
    id="ODS1",
    name="Test Org",
    active=True,
    telecom=None,
    type_=None,
):
    kwargs = {
        "id": id,
        "name": name,
        "active": active,
    }
    if telecom is not None:
        kwargs["telecom"] = telecom
    if type_ is not None:
        kwargs["type"] = type_
    return Organization(**kwargs)

def test_from_fhir_maps_fields_correctly():
    mapper = OrganizationMapper()
    telecom = [ContactPoint(system="phone", value="01234").model_dump()]
    type_ = [CodeableConcept.model_dump(text="GP Practice")]
    org = make_org(
        id="ODS1", name="Test Org", active=True, telecom=telecom, type_=type_
    )
    result = mapper.from_fhir(org)
    assert isinstance(result, Organisation)
    assert result.identifier_ODS_ODSCode == "ODS1"
    assert result.name == "Test Org"
    assert result.active is True
    assert result.telecom == "01234"
    assert result.type == "GP Practice"
    assert result.modified_by == "ODS_ETL_PIPELINE"


def test_from_fhir_handles_missing_fields():
    mapper = OrganizationMapper()
    org = make_org(id="ODS2", name=None, active=None, telecom=None, type_=None)
    result = mapper.from_fhir(org)
    assert result.identifier_ODS_ODSCode == "ODS2"
    assert result.name is None
    assert result.active is False
    assert result.telecom is None
    assert result.type is None


def test_get_org_type_with_text():
    mapper = OrganizationMapper()
    type_ = [CodeableConcept(text="Hospital").model_dump()]
    org = make_org(type_=type_)
    assert mapper._get_org_type(org) == "Hospital"


def test_get_org_type_with_coding_display():
    mapper = OrganizationMapper()
    coding = [Coding(display="Clinic", code="CLINIC").model_dump()]
    type_ = [CodeableConcept(text=None, coding=coding).model_dump()]
    org = make_org(type_=type_)
    assert mapper._get_org_type(org) == "Clinic"


def test_get_org_type_with_coding_code():
    mapper = OrganizationMapper()
    coding = [Coding(display=None, code="CODEONLY").model_dump()]
    type_ = [CodeableConcept(text=None, coding=coding).model_dump()]
    org = make_org(type_=type_)
    assert mapper._get_org_type(org) == "CODEONLY"


def test_get_org_type_none():
    mapper = OrganizationMapper()
    org = make_org(type_=None)
    assert mapper._get_org_type(org) is None


def test_get_org_telecom_with_phone():
    mapper = OrganizationMapper()
    telecom = [ContactPoint(system="phone", value="01234").model_dump()]
    org = make_org(telecom=telecom)
    assert mapper._get_org_telecom(org) == "01234"


def test_get_org_telecom_none():
    mapper = OrganizationMapper()
    telecom = [ContactPoint(system="email", value="test@example.com").model_dump()]
    org = make_org(telecom=telecom)
    assert mapper._get_org_telecom(org) is None


def test_from_ods_fhir_to_fhir_validates_and_returns(mocker):
    mapper = OrganizationMapper()
    ods_organisation = {
        "resourceType": "Organization",
        "id": "C88037",
        "meta": {
            "lastUpdated": "2024-10-23T00:00:00+00:00",
            "profile": "https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1",
        },
        "active": True,
        "name": "Test Org",
        "telecom": [{"system": "phone", "value": "01234"}],
        "identifier": {"system": "test", "value": "ODS1"},
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {
                        "url": "role",
                        "valueCoding": {
                            "system": "https://directory.spineservices.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRole-1",
                            "display": "GP PRACTICE",
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            },
        ],
    }
    organisation = Organization(
        id=="C88037",
        name="Test Org",
        active=True,
        contact="01234",
        type="GP PRACTICE",
    )
    mock_validator = mocker.patch(
        "ftrs_common.fhir.r4b.organisation_mapper.FhirValidator.validate",
        return_value=organisation,
    )
    result = mapper.from_ods_fhir_to_fhir(ods_organisation)
    assert result is organisation
    mock_validator.assert_called_once()


def test_create_codable_concept_for_type_returns_list_of_dict():
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {
                        "url": "role",
                        "valueCoding": {"display": "Other"},
                    },
                    {"url": "primaryRole", "valueBoolean": False},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {"url": "role", "valueCoding": {"display": "GP PRACTICE"}},
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ]
    }
    result = mapper._create_codable_concept_for_type(ods_org)
    assert isinstance(result, list)
    assert isinstance(result[0], CodeableConcept)
    assert result[0].coding[0]["display"] == "GP PRACTICE"
    assert result[0].coding[0]["code"] == "76"


def test_create_contact_point_from_telecom_only_phone():
    mapper = OrganizationMapper()
    telecom = [
        {"system": "phone", "value": "01234"},
        {"system": "url", "value": "http://example.com"},
        {"system": "email", "value": "test@example.com"},
    ]
    result = mapper._create_contact_point_from_telecom(telecom)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["system"] == "phone"
    assert result[0]["value"] == "01234"
    assert result[0]["use"] == "work"
