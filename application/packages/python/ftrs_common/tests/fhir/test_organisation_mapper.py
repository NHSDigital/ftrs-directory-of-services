import uuid

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_data_layer.domain import Organisation


def make_fhir_org(
    id: str = str(uuid.uuid4()),
    name: str = "Test Org",
    active: bool = True,
    telecom: list | None = None,
    type: list | None = None,
) -> FhirOrganisation:
    kwargs = {
        "id": id,
        "identifier": [Identifier.model_construct(value=id)],
        "name": name,
        "active": active,
        "type": type,
    }
    if telecom is not None:
        if not isinstance(telecom, list):
            telecom = [telecom]
        kwargs["telecom"] = telecom

    return FhirOrganisation(**kwargs)


def test_to_fhir_maps_fields_correctly() -> None:
    mapper = OrganizationMapper()
    org = Organisation(
        id="123e4567-e89b-12d3-a456-42661417400a",
        identifier_ODS_ODSCode="ODS1",
        name="Test Org",
        active=True,
        telecom="01234",
        type="GP Practice",
        modifiedBy="ODS_ETL_PIPELINE",
    )
    fhir_org = mapper.to_fhir(org)
    assert isinstance(fhir_org, FhirOrganisation)
    assert fhir_org.id == "123e4567-e89b-12d3-a456-42661417400a"
    assert fhir_org.name == "Test Org"
    assert fhir_org.active is True
    assert fhir_org.identifier[0].value == "ODS1"
    assert fhir_org.telecom[0].system == "phone"
    assert fhir_org.telecom[0].value == "01234"
    assert fhir_org.telecom[0].use == "work"
    assert (
        fhir_org.meta.profile[0]
        == "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
    )
    assert fhir_org.type[0].coding[0].display == "GP Practice"


def test_to_fhir_handles_missing_telecom() -> None:
    mapper = OrganizationMapper()
    org = Organisation(
        id="123e4567-e89b-12d3-a456-42661417400a",
        identifier_ODS_ODSCode="ODS2",
        name="Test Org 2",
        active=False,
        telecom=None,
        type="GP Practice",
        modifiedBy="ODS_ETL_PIPELINE",
    )
    fhir_org = mapper.to_fhir(org)
    assert isinstance(fhir_org, FhirOrganisation)
    assert fhir_org.id == "123e4567-e89b-12d3-a456-42661417400a"
    assert fhir_org.name == "Test Org 2"
    assert fhir_org.active is False
    assert fhir_org.identifier[0].value == "ODS2"
    assert not hasattr(fhir_org, "contact") or fhir_org.telecom == []


def test__build_meta_profile() -> None:
    mapper = OrganizationMapper()
    meta = mapper._build_meta_profile()
    assert meta == {
        "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
    }


def test__build_identifier() -> None:
    mapper = OrganizationMapper()
    identifier = mapper._build_identifier("ODS1")
    assert isinstance(identifier, list)
    assert identifier[0].system == "https://fhir.nhs.uk/Id/ods-organization-code"
    assert identifier[0].value == "ODS1"
    assert identifier[0].use == "official"


def test__build_telecom() -> None:
    mapper = OrganizationMapper()
    telecom = mapper._build_telecom("01234")
    assert isinstance(telecom, list)
    assert telecom[0]["system"] == "phone"
    assert telecom[0]["value"] == "01234"
    assert telecom[0]["use"] == "work"
    telecom_none = mapper._build_telecom(None)
    assert telecom_none == []


def test__build_type() -> None:
    mapper = OrganizationMapper()
    type_list = mapper._build_type("GP Practice")
    assert isinstance(type_list, list)
    assert type_list[0].coding[0].display == "GP Practice"
    assert type_list[0].coding[0].code == "GP Practice"
    assert type_list[0].text == "GP Practice"
    # Test fallback
    type_list_default = mapper._build_type(None)
    assert type_list_default[0].coding[0].display == "GP Service"


def test_from_fhir_maps_fields_correctly() -> None:
    mapper = OrganizationMapper()
    org_type = [CodeableConcept(text="GP Practice")]
    valid_uuid = str(uuid.uuid4())
    org = FhirOrganisation(
        id=valid_uuid,
        identifier=[
            Identifier(
                system="https://fhir.nhs.uk/Id/ods-organization-code", value=valid_uuid
            )
        ],
        name="Test Org",
        active=True,
        type=org_type,
        telecom=[ContactPoint(system="phone", value="01234")],
    )
    internal_organisation = mapper.from_fhir(org)
    assert isinstance(internal_organisation, Organisation)
    assert internal_organisation.identifier_ODS_ODSCode == valid_uuid
    assert internal_organisation.name == "Test Org"
    assert internal_organisation.active is True
    assert internal_organisation.telecom == "01234"
    assert internal_organisation.type == "GP Practice"
    assert internal_organisation.modifiedBy == "ODS_ETL_PIPELINE"


def test_from_ods_fhir_to_fhir_validates_and_returns() -> None:
    mapper = OrganizationMapper()
    ods_fhir_organisation = {
        "resourceType": "Organization",
        "id": "C88037",
        "active": True,
        "name": "Test Org",
        "telecom": [{"system": "phone", "value": "01234"}],
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
                    "start": "1974-04-01",
                },
            },
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {
                        "url": "role",
                        "valueCoding": {
                            "system": "https://directory.spineservices.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRole-1",
                            "code": "177",
                            "display": "PRESCRIBING COST CENTRE",
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
                            "start": "1974-04-01",
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
                            "code": "76",
                            "display": "GP PRACTICE",
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
                            "start": "2014-04-15",
                        },
                    },
                    {"url": "status", "valueString": "Active"},
                ],
            },
        ],
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "C88037",
        },
        "type": {
            "coding": {
                "system": "https://fhir.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRecordClass-1",
                "code": "1",
                "display": "HSCOrg",
            }
        },
    }
    result = mapper.from_ods_fhir_to_fhir(ods_fhir_organisation)
    assert isinstance(result, FhirOrganisation)
    assert result.id == "C88037"
    assert result.name == "Test Org"
    assert result.active is True
    assert result.identifier[0].value == "C88037"
    assert result.telecom[0].system == "phone"
    assert result.telecom[0].value == "01234"
    assert result.type[0].coding[0].display == "PRESCRIBING COST CENTRE"


def test__get_org_type() -> None:
    mapper = OrganizationMapper()
    org_type = [CodeableConcept(text="GP Practice")]
    org = make_fhir_org(
        id=str(uuid.uuid4()), name="Test Org", active=True, telecom=None, type=org_type
    )
    assert mapper._get_org_type(org) == "GP Practice"


def test__get_org_telecom_with_phone() -> None:
    mapper = OrganizationMapper()
    org = make_fhir_org(
        telecom=[ContactPoint(system="phone", value="01234")],
    )
    assert mapper._get_org_telecom(org) == "01234"


def test__get_org_telecom_none() -> None:
    mapper = OrganizationMapper()
    org = make_fhir_org(
        telecom=[],
    )
    assert mapper._get_org_telecom(org) is None


def test__get_org_telecom_with_no_phone() -> None:
    mapper = OrganizationMapper()
    org = make_fhir_org(
        telecom=[
            ContactPoint(system="email", value="test@example.com"),
            ContactPoint(system="fax", value="12345"),
        ],
    )
    assert mapper._get_org_telecom(org) is None


def test__extract_role_from_extension_none_when_no_extension() -> None:
    mapper = OrganizationMapper()
    ods_org = {}
    assert mapper._extract_role_from_extension(ods_org) is None


def test__extract_role_from_extension_none_when_no_matching_role() -> None:
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "not-a-role-url",
                "extension": [
                    {"url": "role", "valueCoding": {"display": "GP PRACTICE"}},
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ]
    }
    assert mapper._extract_role_from_extension(ods_org) is None


def test__extract_role_from_extension_none_when_no_primary_role() -> None:
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {"url": "role", "valueCoding": {"display": "GP PRACTICE"}},
                    # missing primaryRole
                ],
            }
        ]
    }
    assert mapper._extract_role_from_extension(ods_org) is None


def test__extract_role_from_extension_success() -> None:
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {"url": "role", "valueCoding": {"display": "GP PRACTICE"}},
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ]
    }
    assert mapper._extract_role_from_extension(ods_org) == "GP PRACTICE"


def test__is_org_role_extension_true_and_false() -> None:
    mapper = OrganizationMapper()
    ext_true = {
        "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1"
    }
    ext_false = {"url": "not-a-role-url"}
    assert mapper._is_org_role_extension(ext_true) is True
    assert mapper._is_org_role_extension(ext_false) is False


def test__is_primary_role_true_and_false() -> None:
    mapper = OrganizationMapper()
    ext_true = {"extension": [{"url": "primaryRole", "valueBoolean": True}]}
    ext_false = {"extension": [{"url": "primaryRole", "valueBoolean": False}]}
    ext_none = {
        "extension": [{"url": "role", "valueCoding": {"display": "GP PRACTICE"}}]
    }
    assert mapper._is_primary_role(ext_true) is True
    assert mapper._is_primary_role(ext_false) is False
    assert mapper._is_primary_role(ext_none) is False


def test__get_role_display_from_extension_various() -> None:
    mapper = OrganizationMapper()
    ext_none = {"extension": []}
    assert mapper._get_role_display_from_extension(ext_none) is None
    ext_no_role = {
        "extension": [{"url": "notrole", "valueCoding": {"display": "GP PRACTICE"}}]
    }
    assert mapper._get_role_display_from_extension(ext_no_role) is None
    ext_no_value_coding = {"extension": [{"url": "role"}]}
    assert mapper._get_role_display_from_extension(ext_no_value_coding) is None
    ext_no_display = {"extension": [{"url": "role", "valueCoding": {}}]}
    assert mapper._get_role_display_from_extension(ext_no_display) is None
    ext_with_display = {
        "extension": [{"url": "role", "valueCoding": {"display": "Test Role"}}]
    }
    assert mapper._get_role_display_from_extension(ext_with_display) == "Test Role"
