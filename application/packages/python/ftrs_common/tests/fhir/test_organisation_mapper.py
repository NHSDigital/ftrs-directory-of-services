import uuid
from datetime import date

import pytest
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganisation
from ftrs_common.fhir.r4b.organisation_mapper import (
    ORGANISATION_ROLE_URL,
    TYPED_PERIOD_URL,
    OrganizationMapper,
)
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.organisation import LegalDates


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


def test__extract_ods_code_from_identifiers_success() -> None:
    """Test extracting ODS code from a valid identifier list."""
    mapper = OrganizationMapper()
    identifiers = [
        {
            "use": "official",
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "T6I4F",
        }
    ]
    result = mapper._extract_ods_code_from_identifiers(identifiers)
    assert result == "T6I4F"


def test__extract_ods_code_from_identifiers_multiple_identifiers() -> None:
    """Test extracting ODS code when there are multiple identifiers."""
    mapper = OrganizationMapper()
    identifiers = [
        {
            "use": "secondary",
            "system": "https://some.other.system/Id/other-code",
            "value": "OTHER123",
        },
        {
            "use": "official",
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "ABC123",
        },
    ]
    result = mapper._extract_ods_code_from_identifiers(identifiers)
    assert result == "ABC123"


def test__extract_ods_code_from_identifiers_no_matching_system() -> None:
    """Test that ValueError is raised when no ODS identifier is found."""
    mapper = OrganizationMapper()
    identifiers = [
        {
            "use": "official",
            "system": "https://some.other.system/Id/other-code",
            "value": "OTHER123",
        }
    ]
    with pytest.raises(
        ValueError, match="No ODS code identifier found in organization resource"
    ):
        mapper._extract_ods_code_from_identifiers(identifiers)


def test__extract_ods_code_from_identifiers_empty_list() -> None:
    """Test that ValueError is raised when identifier list is empty."""
    mapper = OrganizationMapper()
    identifiers = []
    with pytest.raises(
        ValueError, match="No ODS code identifier found in organization resource"
    ):
        mapper._extract_ods_code_from_identifiers(identifiers)


def test__extract_ods_code_from_identifiers_no_value() -> None:
    """Test that ValueError is raised when identifier has no value."""
    mapper = OrganizationMapper()
    identifiers = [
        {
            "use": "official",
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            # Missing value field
        }
    ]
    with pytest.raises(
        ValueError, match="No ODS code identifier found in organization resource"
    ):
        mapper._extract_ods_code_from_identifiers(identifiers)


def test__extract_ods_code_from_identifiers_non_dict_in_list() -> None:
    """Test that non-dict items in the list are skipped gracefully."""
    mapper = OrganizationMapper()
    identifiers = [
        "not a dict",
        None,
        {
            "use": "official",
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "XYZ789",
        },
    ]
    result = mapper._extract_ods_code_from_identifiers(identifiers)
    assert result == "XYZ789"


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


@pytest.mark.parametrize(
    "fhir_name,expected_name",
    [
        ("nhs trust hospital", "NHS Trust Hospital"),
        ("LONDON GP SURGERY", "London GP Surgery"),
        ("the icb board", "The ICB Board"),
        ("local pcn practice", "Local PCN Practice"),
        ("Mixed Case NHS GP", "Mixed Case NHS GP"),
    ],
)
def test_from_fhir_sanitizes_organization_name(
    fhir_name: str, expected_name: str
) -> None:
    """Test that organization names are sanitized with title case and acronym preservation."""
    mapper = OrganizationMapper()
    valid_uuid = str(uuid.uuid4())
    fhir_org = FhirOrganisation(
        id=valid_uuid,
        identifier=[
            Identifier(
                system="https://fhir.nhs.uk/Id/ods-organization-code",
                value=valid_uuid,
            )
        ],
        name=fhir_name,
        active=True,
        type=[CodeableConcept(text="Hospital")],
    )

    result = mapper.from_fhir(fhir_org)

    assert result.name == expected_name


@pytest.mark.parametrize(
    "fhir_type,expected_type",
    [
        ("nhs trust", "NHS Trust"),
        ("GP PRACTICE", "GP Practice"),
        ("icb organization", "ICB Organization"),
        ("pcn network", "PCN Network"),
    ],
)
def test_from_fhir_sanitizes_organization_type(
    fhir_type: str, expected_type: str
) -> None:
    """Test that organization types are sanitized with title case and acronym preservation."""
    mapper = OrganizationMapper()
    valid_uuid = str(uuid.uuid4())
    fhir_org = FhirOrganisation(
        id=valid_uuid,
        identifier=[
            Identifier(
                system="https://fhir.nhs.uk/Id/ods-organization-code",
                value=valid_uuid,
            )
        ],
        name="Test Organization",
        active=True,
        type=[CodeableConcept(text=fhir_type)],
    )

    result = mapper.from_fhir(fhir_org)

    assert result.type == expected_type


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
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "C88037",
            }
        ],
        "type": {
            "coding": {
                "system": "https://fhir.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRecordClass-1",
                "code": "1",
                "display": "HSCOrg",
            }
        },
    }
    result = mapper.from_ods_fhir_to_fhir(ods_fhir_organisation, "GP Practice")
    assert isinstance(result, FhirOrganisation)
    assert result.id == "C88037"
    assert result.name == "Test Org"
    assert result.active is True
    assert result.identifier[0].value == "C88037"
    assert result.telecom[0].system == "phone"
    assert result.telecom[0].value == "01234"
    assert result.type[0].coding[0].display == "GP Practice"


def test_to_fhir_bundle_single_org() -> None:
    mapper = OrganizationMapper()
    org1 = Organisation(
        id="00000000-0000-0000-0000-00000000000a",
        identifier_ODS_ODSCode="ODS1",
        name="Test Org 1",
        active=True,
        telecom="01234",
        type="GP Practice",
        modifiedBy="ODS_ETL_PIPELINE",
    )
    bundle_single = mapper.to_fhir_bundle([org1])
    assert bundle_single.__resource_type__ == "Bundle"
    assert bundle_single.type == "searchset"
    assert str(bundle_single.total) == "1"
    assert len(bundle_single.entry) == 1
    resource = bundle_single.entry[0].resource
    assert resource.id == "00000000-0000-0000-0000-00000000000a"
    assert resource.name == "Test Org 1"
    assert resource.active is True
    assert resource.identifier[0].value == "ODS1"
    assert (
        resource.identifier[0].system == "https://fhir.nhs.uk/Id/ods-organization-code"
    )
    assert resource.identifier[0].use == "official"
    assert resource.telecom[0].system == "phone"
    assert resource.telecom[0].value == "01234"
    assert resource.telecom[0].use == "work"
    assert resource.type[0].coding[0].display == "GP Practice"
    assert resource.type[0].coding[0].code == "GP Practice"
    assert resource.type[0].text == "GP Practice"
    assert (
        resource.meta.profile[0]
        == "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
    )


def test_to_fhir_bundle_multiple_orgs() -> None:
    mapper = OrganizationMapper()
    org1 = Organisation(
        id="00000000-0000-0000-0000-00000000000a",
        identifier_ODS_ODSCode="ODS1",
        name="Test Org 1",
        active=True,
        telecom="01234",
        type="GP Practice",
        modifiedBy="ODS_ETL_PIPELINE",
    )
    org2 = Organisation(
        id="00000000-0000-0000-0000-00000000000b",
        identifier_ODS_ODSCode="ODS2",
        name="Test Org 2",
        active=False,
        telecom=None,
        type="GP Practice",
        modifiedBy="ODS_ETL_PIPELINE",
    )
    bundle_multi = mapper.to_fhir_bundle([org1, org2])
    assert bundle_multi.__resource_type__ == "Bundle"
    assert bundle_multi.type == "searchset"
    assert str(bundle_multi.total) == "2"
    ids = {entry.resource.id for entry in bundle_multi.entry}
    assert ids == {
        "00000000-0000-0000-0000-00000000000a",
        "00000000-0000-0000-0000-00000000000b",
    }


def test__get_org_type() -> None:
    mapper = OrganizationMapper()
    org_type = [CodeableConcept(text="GP Practice")]
    org = make_fhir_org(
        id=str(uuid.uuid4()), name="Test Org", active=True, telecom=None, type=org_type
    )
    assert mapper._get_org_type(org) == "GP Practice"


def test__get_org_type_invalid_missing_type() -> None:
    mapper = OrganizationMapper()
    org = make_fhir_org(
        id=str(uuid.uuid4()), name="Test Org", active=True, telecom=None, type=None
    )
    assert mapper._get_org_type(org) is None


def test__get_org_type_with_coding_display() -> None:
    mapper = OrganizationMapper()
    org_type = [
        CodeableConcept(
            coding=[
                {
                    "system": "http://example.org/fhir/CodeSystem/org-type",
                    "code": "GP",
                    "display": "GP Practice",
                }
            ]
        )
    ]
    org = make_fhir_org(
        id=str(uuid.uuid4()), name="Test Org", active=True, telecom=None, type=org_type
    )
    assert mapper._get_org_type(org) == "GP Practice"


def test__get_org_type_with_no_display() -> None:
    mapper = OrganizationMapper()
    org_type = [CodeableConcept(id="abc")]
    org = make_fhir_org(
        id=str(uuid.uuid4()), name="Test Org", active=True, telecom=None, type=org_type
    )
    assert mapper._get_org_type(org) is None


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


def test__get_role_code_from_extension_england_structure() -> None:
    """Test extracting role code from England structure."""
    mapper = OrganizationMapper()
    ext = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {
                "url": "roleCode",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                            "code": "RO177",
                            "display": "PRESCRIBING COST CENTRE",
                        }
                    ]
                },
            }
        ],
    }
    result = mapper._get_role_code_from_extension(ext)
    assert result == "RO177"


def test__get_role_code_from_extension_returns_none_when_missing() -> None:
    """Test returns None when roleCode is missing."""
    mapper = OrganizationMapper()
    ext = {
        "extension": [
            {"url": "ABC", "valueInteger": 78491},
            {"url": "EFG", "valueBoolean": True},
        ]
    }
    result = mapper._get_role_code_from_extension(ext)
    assert result is None


def test__get_role_code_from_extension_returns_none_empty_coding() -> None:
    """Test returns None when coding array is empty."""
    mapper = OrganizationMapper()
    ext = {
        "extension": [
            {
                "url": "roleCode",
                "valueCodeableConcept": {"coding": []},
            }
        ]
    }
    result = mapper._get_role_code_from_extension(ext)
    assert result is None


def test__get_role_code_from_extension_returns_none_no_valuecodeableconcept() -> None:
    """Test returns None when valueCodeableConcept is missing."""
    mapper = OrganizationMapper()
    ext = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {
                "url": "roleCode",
            }
        ],
    }
    result = mapper._get_role_code_from_extension(ext)
    assert result is None


def test_get_all_role_codes_england_structure_multiple_roles() -> None:
    """Test extracting multiple role codes from England structure."""
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 78491,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 195368,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                ],
            },
        ]
    }
    result = mapper.get_all_role_codes(ods_org)
    assert result == ["RO177", "RO76"]


def test_get_all_role_codes_returns_empty_list_no_extensions() -> None:
    """Test returns empty list when no role extensions present."""
    mapper = OrganizationMapper()
    ods_org = {"identifier": [{"value": "TEST123"}]}
    result = mapper.get_all_role_codes(ods_org)
    assert result == []


def test_get_all_role_codes_skips_non_role_extensions() -> None:
    """Test skips extensions that are not role extensions."""
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [],
            }
        ]
    }
    result = mapper.get_all_role_codes(ods_org)
    assert result == []


def test_get_all_role_codes_correct_url_no_role_code() -> None:
    """Test get_all_role_codes with correct url but no role code present."""
    mapper = OrganizationMapper()
    ods_org = {
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    # No roleCode present
                ],
            }
        ]
    }
    result = mapper.get_all_role_codes(ods_org)
    assert result == []


def test_from_ods_fhir_to_fhir_with_dos_org_type() -> None:
    """Test from_ods_fhir_to_fhir with explicit org type."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "TEST123",
        "active": True,
        "name": "Test GP Practice",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ODS123",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {"url": "role", "valueCoding": {"code": "177"}},
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            },
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {"url": "role", "valueCoding": {"code": "76"}},
                    {"url": "primaryRole", "valueBoolean": False},
                ],
            },
        ],
    }
    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")
    assert result is not None
    assert result.identifier[0].value == "ODS123"
    assert result.type[0].text == "GP Practice"


def test__extract_legal_dates_with_valid_typed_period() -> None:
    """Test _extract_legal_dates extracts dates from valid TypedPeriod extension within OrganisationRole."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [{"code": "RO76", "display": "GP PRACTICE"}]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {"code": "Legal"},
                        },
                        {
                            "url": "period",
                            "valuePeriod": {
                                "start": "2020-01-15",
                                "end": "2025-12-31",
                            },
                        },
                    ],
                },
            ],
        }
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start == "2020-01-15"
    assert end == "2025-12-31"


def test__extract_legal_dates_no_extension_attribute() -> None:
    """Test _extract_legal_dates when fhir_resource has no extension attribute."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    if hasattr(fhir_org, "extension"):
        delattr(fhir_org, "extension")

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start is None
    assert end is None


def test__extract_legal_dates_extension_is_none() -> None:
    """Test _extract_legal_dates when extension attribute is None."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = None

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start is None
    assert end is None


def test__extract_legal_dates_extension_is_empty_list() -> None:
    """Test _extract_legal_dates when extension list is empty."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = []

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start is None
    assert end is None


def test__extract_legal_dates_multiple_extensions_typed_period_present() -> None:
    """Test _extract_legal_dates with multiple extensions including TypedPeriod within OrganisationRole."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = [
        {
            "url": "https://example.com/other-extension",
            "valueString": "test",
        },
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [{"code": "RO76", "display": "GP PRACTICE"}]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {"code": "Legal"},
                        },
                        {
                            "url": "period",
                            "valuePeriod": {
                                "start": "2020-01-15",
                                "end": "2025-12-31",
                            },
                        },
                    ],
                },
            ],
        },
        {
            "url": "https://example.com/another-extension",
            "valueBoolean": True,
        },
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start == "2020-01-15"
    assert end == "2025-12-31"


def test__extract_legal_dates_typed_period_no_sub_extensions() -> None:
    """Test _extract_legal_dates with TypedPeriod URL but no sub-extensions."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "valueString": "test",
        }
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start is None
    assert end is None


def test__extract_legal_dates_typed_period_empty_sub_extensions() -> None:
    """Test _extract_legal_dates with TypedPeriod but empty sub-extensions."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
            "extension": [],
        }
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start is None
    assert end is None


def test__extract_legal_dates_no_matching_url() -> None:
    """Test _extract_legal_dates when no extension has TypedPeriod URL."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = [
        {
            "url": "https://example.com/other-extension",
            "extension": [
                {
                    "url": "period",
                    "valuePeriod": {
                        "start": "2020-01-15",
                    },
                },
            ],
        },
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
                }
            ],
        },
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start is None
    assert end is None


def test__extract_legal_dates_ext_with_dict_method() -> None:
    """Test _extract_legal_dates handles extensions with .dict() method within OrganisationRole."""
    from fhir.resources.R4B.extension import Extension

    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()

    # Create a proper FHIR Extension object that has a .dict() method
    role_ext = Extension.model_validate(
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [{"code": "RO76", "display": "GP PRACTICE"}]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {"code": "Legal"},
                        },
                        {
                            "url": "period",
                            "valuePeriod": {
                                "start": "2020-01-15",
                                "end": "2025-12-31",
                            },
                        },
                    ],
                },
            ],
        }
    )

    fhir_org.extension = [role_ext]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start == "2020-01-15"
    assert end == "2025-12-31"


def test__extract_legal_dates_mixed_extension_types() -> None:
    """Test _extract_legal_dates with mixed dict and Extension object types within OrganisationRole."""
    from fhir.resources.R4B.extension import Extension

    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()

    # Create a proper FHIR Extension object
    other_ext = Extension.model_validate(
        {
            "url": "https://example.com/other-extension",
            "valueString": "test",
        }
    )

    # Mix of Extension object and dict
    fhir_org.extension = [
        other_ext,
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [{"code": "RO76", "display": "GP PRACTICE"}]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {"code": "Legal"},
                        },
                        {
                            "url": "period",
                            "valuePeriod": {
                                "start": "2020-01-15",
                            },
                        },
                    ],
                },
            ],
        },
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    assert start == "2020-01-15"
    assert end is None


def test__extract_legal_dates_first_matching_extension_wins() -> None:
    """Test _extract_legal_dates returns first matching TypedPeriod extension from first OrganisationRole."""
    mapper = OrganizationMapper()
    fhir_org = make_fhir_org()
    fhir_org.extension = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [
                            {"code": "RO177", "display": "PRESCRIBING COST CENTRE"}
                        ]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {"code": "Legal"},
                        },
                        {
                            "url": "period",
                            "valuePeriod": {
                                "start": "2020-01-15",
                                "end": "2025-12-31",
                            },
                        },
                    ],
                },
            ],
        },
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [
                {
                    "url": "roleCode",
                    "valueCodeableConcept": {
                        "coding": [{"code": "RO76", "display": "GP PRACTICE"}]
                    },
                },
                {
                    "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                    "extension": [
                        {
                            "url": "dateType",
                            "valueCoding": {"code": "Legal"},
                        },
                        {
                            "url": "period",
                            "valuePeriod": {
                                "start": "2021-01-01",
                                "end": "2026-12-31",
                            },
                        },
                    ],
                },
            ],
        },
    ]

    start, end = mapper._extract_legal_dates(fhir_org)
    # Should return dates from first OrganisationRole
    assert start == "2020-01-15"
    assert end == "2025-12-31"


def test_build_legal_date_extension_with_both_dates() -> None:
    """Test building legal date extension with both start and end dates."""
    mapper = OrganizationMapper()
    result = mapper._build_legal_date_extension("2020-01-15", "2025-12-31")

    assert result is not None
    result_dict = result.dict()
    assert (
        result_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    )
    assert str(len(result_dict["extension"])) == "2"

    # Check dateType sub-extension
    date_type = next(
        (e for e in result_dict["extension"] if e["url"] == "dateType"), None
    )
    assert date_type is not None
    assert date_type["valueCoding"]["code"] == "Legal"

    # Check period sub-extension
    period = next((e for e in result_dict["extension"] if e["url"] == "period"), None)
    assert period is not None
    assert period["valuePeriod"]["start"] == "2020-01-15"
    assert period["valuePeriod"]["end"] == "2025-12-31"


def test_to_fhir_with_legal_dates() -> None:
    """Test to_fhir includes legal date extension."""
    mapper = OrganizationMapper()
    org = Organisation(
        id="123e4567-e89b-12d3-a456-42661417400a",
        identifier_ODS_ODSCode="ODS1",
        name="Test Org",
        active=True,
        telecom="01234",
        type="GP Practice",
        legalDates=LegalDates(start=date(2020, 1, 15), end=date(2025, 12, 31)),
        modifiedBy="ODS_ETL_PIPELINE",
    )

    fhir_org = mapper.to_fhir(org)

    assert isinstance(fhir_org, FhirOrganisation)
    assert hasattr(fhir_org, "extension")
    assert fhir_org.extension is not None
    assert len(fhir_org.extension) == 1

    ext_dict = fhir_org.extension[0].dict()
    assert (
        ext_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    )

    period = next((e for e in ext_dict["extension"] if e["url"] == "period"), None)
    assert period["valuePeriod"]["start"] == "2020-01-15"
    assert period["valuePeriod"]["end"] == "2025-12-31"


@pytest.mark.parametrize(
    "start_date,end_date,expected_start,expected_end",
    [
        pytest.param(
            "2020-01-15",
            "2025-12-31",
            "2020-01-15",
            "2025-12-31",
            id="both_dates_present",
        ),
        pytest.param(
            "1974-04-01",
            None,
            "1974-04-01",
            None,
            id="only_start_date",
        ),
        pytest.param(
            None,
            "2025-12-31",
            None,
            "2025-12-31",
            id="only_end_date",
        ),
    ],
)
def test__build_legal_date_extension_with_dates(
    start_date: str | None,
    end_date: str | None,
    expected_start: str | None,
    expected_end: str | None,
) -> None:
    """Test building TypedPeriod extension with various date combinations."""
    mapper = OrganizationMapper()
    extension = mapper._build_legal_date_extension(start_date, end_date)

    assert extension is not None
    ext_dict = extension.dict()
    assert (
        ext_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    )
    assert str(len(ext_dict["extension"])) == "2"

    # Check dateType sub-extension
    date_type = next((e for e in ext_dict["extension"] if e["url"] == "dateType"), None)
    assert date_type is not None
    assert (
        date_type["valueCoding"]["system"]
        == "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType"
    )
    assert date_type["valueCoding"]["code"] == "Legal"
    assert date_type["valueCoding"]["display"] == "Legal"

    # Check period sub-extension
    period = next((e for e in ext_dict["extension"] if e["url"] == "period"), None)
    assert period is not None

    if expected_start is not None:
        assert period["valuePeriod"]["start"] == expected_start
    else:
        assert "start" not in period["valuePeriod"]

    if expected_end is not None:
        assert period["valuePeriod"]["end"] == expected_end
    else:
        assert "end" not in period["valuePeriod"]


def test__build_legal_date_extension_no_dates_returns_none() -> None:
    """Test building TypedPeriod extension with no dates returns None."""
    mapper = OrganizationMapper()
    extension = mapper._build_legal_date_extension(None, None)
    assert extension is None


@pytest.mark.parametrize(
    "typed_period_ext,expected_start,expected_end",
    [
        pytest.param(
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {
                            "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                            "code": "Legal",
                        },
                    },
                    {
                        "url": "period",
                        "valuePeriod": {
                            "start": "2020-01-15",
                            "end": "2025-12-31",
                        },
                    },
                ],
            },
            "2020-01-15",
            "2025-12-31",
            id="both_dates",
        ),
        pytest.param(
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {"code": "Legal"},
                    },
                    {
                        "url": "period",
                        "valuePeriod": {"start": "2020-01-15"},
                    },
                ],
            },
            "2020-01-15",
            None,
            id="start_only",
        ),
        pytest.param(
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {"code": "Legal"},
                    },
                    {
                        "url": "period",
                        "valuePeriod": {"end": "2025-12-31"},
                    },
                ],
            },
            None,
            "2025-12-31",
            id="end_only",
        ),
        pytest.param(
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {"code": "Operational"},
                    },
                    {
                        "url": "period",
                        "valuePeriod": {"start": "2020-01-15"},
                    },
                ],
            },
            "2020-01-15",
            None,
            id="non_legal_type_still_extracts_dates",
        ),
        pytest.param(
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {"code": "Legal"},
                    },
                ],
            },
            None,
            None,
            id="missing_period",
        ),
        pytest.param(
            None,
            None,
            None,
            id="none_extension",
        ),
    ],
)
def test__parse_legal_period(
    typed_period_ext: dict | None,
    expected_start: str | None,
    expected_end: str | None,
) -> None:
    """Test extracting dates from TypedPeriod Extension.

    Note: Validation of dateType='Legal' happens in Pydantic validator,
    so the mapper just extracts dates regardless of dateType value.
    """
    from fhir.resources.R4B.extension import Extension

    mapper = OrganizationMapper()
    ext_obj = Extension.model_validate(typed_period_ext) if typed_period_ext else None
    start, end = mapper._parse_legal_period(ext_obj)
    assert start == expected_start
    assert end == expected_end


def test_to_fhir_no_extension_when_no_legal_dates() -> None:
    """Test to_fhir does not include extension when no legal dates."""
    mapper = OrganizationMapper()
    org = Organisation(
        id="123e4567-e89b-12d3-a456-42661417400a",
        identifier_ODS_ODSCode="ODS1",
        name="Test Org",
        active=True,
        type="GP Practice",
        modifiedBy="ODS_ETL_PIPELINE",
    )

    fhir_org = mapper.to_fhir(org)

    # Extension should not be set or should be None/empty when no legal dates
    assert (
        not hasattr(fhir_org, "extension")
        or fhir_org.extension is None
        or len(fhir_org.extension) == 0
    )


def test_from_ods_fhir_to_fhir_no_legal_dates() -> None:
    """Test from_ods_fhir_to_fhir when no legal dates present in ODS FHIR OrganisationRole."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "C88037",
        "active": True,
        "name": "Test Org",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "C88037",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {"coding": [{"code": "RO76"}]},
                    }
                ],
            }
        ],
    }

    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")

    assert result is not None
    # Extension should be present (the OrganisationRole), even without legal dates
    assert result.extension is not None
    assert len(result.extension) == 1
    # Verify it's the OrganisationRole
    assert (
        result.extension[0].url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )


def test_from_fhir_no_legal_dates_when_no_extension() -> None:
    """Test from_fhir sets legal dates to None when no extension."""
    mapper = OrganizationMapper()
    fhir_org = FhirOrganisation(
        id="00000000-0000-0000-0000-00000000000a",
        identifier=[
            Identifier(
                use="official",
                system="https://fhir.nhs.uk/Id/ods-organization-code",
                value="ODS1",
            )
        ],
        name="Test Org",
        active=True,
        type=[CodeableConcept(text="GP Practice")],
    )

    org = mapper.from_fhir(fhir_org)

    assert org.legalDates is None


@pytest.mark.parametrize(
    "legal_start_date,legal_end_date,expected_start_in_period,expected_end_in_period",
    [
        pytest.param(
            date(2020, 1, 15),
            None,
            "2020-01-15",
            None,
            id="only_start_date_end_absent",
        ),
        pytest.param(
            None,
            date(2025, 12, 31),
            None,
            "2025-12-31",
            id="only_end_date_start_absent",
        ),
    ],
)
def test_to_fhir_partial_dates_absent_not_null(
    legal_start_date: date | None,
    legal_end_date: date | None,
    expected_start_in_period: str | None,
    expected_end_in_period: str | None,
) -> None:
    """Test to_fhir with partial dates - absent dates should not be in period dict, not null."""
    from ftrs_data_layer.domain.organisation import LegalDates

    mapper = OrganizationMapper()

    legal_dates = None
    if legal_start_date or legal_end_date:
        legal_dates = LegalDates(start=legal_start_date, end=legal_end_date)

    org = Organisation(
        id="123e4567-e89b-12d3-a456-42661417400a",
        identifier_ODS_ODSCode="ODS1",
        name="Test Org",
        active=True,
        type="GP Practice",
        legalDates=legal_dates,
        modifiedBy="ODS_ETL_PIPELINE",
    )

    fhir_org = mapper.to_fhir(org)

    assert fhir_org.extension is not None
    assert len(fhir_org.extension) == 1

    ext_dict = fhir_org.extension[0].dict()
    period = next((e for e in ext_dict["extension"] if e["url"] == "period"), None)

    if expected_start_in_period is not None:
        assert "start" in period["valuePeriod"]
        assert period["valuePeriod"]["start"] == expected_start_in_period
    else:
        assert "start" not in period["valuePeriod"]

    if expected_end_in_period is not None:
        assert "end" in period["valuePeriod"]
        assert period["valuePeriod"]["end"] == expected_end_in_period
    else:
        assert "end" not in period["valuePeriod"]


def test_from_ods_fhir_to_fhir_includes_legal_dates_typed_period() -> None:
    """Test from_ods_fhir_to_fhir extracts and includes OrganisationRole with legal dates as TypedPeriod."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "C88037",
        "active": True,
        "name": "Test Org",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "C88037",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "2015-06-01",
                                    "end": "2030-12-31",
                                },
                            },
                        ],
                    },
                ],
            }
        ],
    }

    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")

    assert result is not None
    assert result.extension is not None
    assert len(result.extension) == 1

    ext_dict = result.extension[0].dict()
    assert (
        ext_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Find the TypedPeriod within the OrganisationRole
    typed_period = next(
        (
            e
            for e in ext_dict["extension"]
            if e["url"]
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period is not None
    period = next((e for e in typed_period["extension"] if e["url"] == "period"), None)
    assert period["valuePeriod"]["start"] == "2015-06-01"
    assert period["valuePeriod"]["end"] == "2030-12-31"


def test_from_ods_fhir_to_fhir_extracts_first_organisation_role_with_legal_dates() -> (
    None
):
    """Test from_ods_fhir_to_fhir extracts first OrganisationRole with nested Legal TypedPeriod."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "K84605",
        "active": True,
        "name": "Test Practice",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "K84605",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 78491,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {"start": "1974-04-01"},
                            },
                        ],
                    },
                    {
                        "url": "active",
                        "valueBoolean": True,
                    },
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 195368,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {"start": "2014-04-15"},
                            },
                        ],
                    },
                    {
                        "url": "active",
                        "valueBoolean": True,
                    },
                ],
            },
        ],
    }

    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")

    assert result is not None
    assert result.extension is not None
    assert len(result.extension) == 1

    # Should extract the FIRST OrganisationRole
    ext_dict = result.extension[0].dict()
    assert (
        ext_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Verify it contains the first role code (RO177)
    role_code_ext = next(
        (e for e in ext_dict["extension"] if e["url"] == "roleCode"), None
    )
    assert role_code_ext is not None
    assert role_code_ext["valueCodeableConcept"]["coding"][0]["code"] == "RO177"

    # Verify it contains the Legal TypedPeriod with start date from first role
    typed_period = next(
        (
            e
            for e in ext_dict["extension"]
            if e["url"]
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period is not None
    period = next((e for e in typed_period["extension"] if e["url"] == "period"), None)
    assert period["valuePeriod"]["start"] == "1974-04-01"


def test_from_ods_fhir_to_fhir_no_organisation_role() -> None:
    """Test from_ods_fhir_to_fhir when no OrganisationRole extension is present."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "TEST123",
        "active": True,
        "name": "Test Org No Role",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "TEST123",
            }
        ],
        "extension": [],
    }

    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")

    assert result is not None
    # Should have no extensions when no OrganisationRole present
    assert (
        not hasattr(result, "extension")
        or result.extension is None
        or len(result.extension) == 0
    )


def test_from_ods_fhir_to_fhir_extracts_nested_legal_dates_from_role() -> None:
    """Test from_ods_fhir_to_fhir extracts OrganisationRole with nested Legal TypedPeriod."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "A12345",
        "active": True,
        "name": "Test GP Practice",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "A12345",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "instanceID",
                        "valueInteger": 183109,
                    },
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "2014-04-15",
                                },
                            },
                        ],
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Operational",
                                    "display": "Operational",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "2014-04-15",
                                },
                            },
                        ],
                    },
                    {
                        "url": "active",
                        "valueBoolean": True,
                    },
                ],
            }
        ],
    }

    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")

    # Verify the result has the entire OrganisationRole with nested TypedPeriod
    assert result is not None
    assert result.extension is not None
    assert len(result.extension) == 1

    ext_dict = result.extension[0].dict()
    assert (
        ext_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Verify the Legal TypedPeriod is nested within the OrganisationRole
    typed_periods = [
        e
        for e in ext_dict["extension"]
        if e["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    ]
    assert str(len(typed_periods)) == "2"

    # Find the Legal period
    legal_period = None
    for tp in typed_periods:
        date_type = next((e for e in tp["extension"] if e["url"] == "dateType"), None)
        if date_type and date_type["valueCoding"]["code"] == "Legal":
            legal_period = tp
            break

    assert legal_period is not None
    period = next((e for e in legal_period["extension"] if e["url"] == "period"), None)
    assert period is not None
    assert period["valuePeriod"]["start"] == "2014-04-15"


def test_from_ods_fhir_to_fhir_nested_legal_dates_with_multiple_roles() -> None:
    """Test from_ods_fhir_to_fhir extracts first OrganisationRole when multiple roles exist."""
    mapper = OrganizationMapper()
    ods_org = {
        "resourceType": "Organization",
        "id": "B98765",
        "active": True,
        "name": "Multi-Role Organization",
        "identifier": [
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "B98765",
            }
        ],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO177",
                                    "display": "PRESCRIBING COST CENTRE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "1974-04-01",
                                },
                            },
                        ],
                    },
                ],
            },
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
                "extension": [
                    {
                        "url": "roleCode",
                        "valueCodeableConcept": {
                            "coding": [
                                {
                                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                                    "code": "RO76",
                                    "display": "GP PRACTICE",
                                }
                            ]
                        },
                    },
                    {
                        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                        "extension": [
                            {
                                "url": "dateType",
                                "valueCoding": {
                                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                                    "code": "Legal",
                                    "display": "Legal",
                                },
                            },
                            {
                                "url": "period",
                                "valuePeriod": {
                                    "start": "2014-04-15",
                                    "end": "2025-12-31",
                                },
                            },
                        ],
                    },
                ],
            },
        ],
    }

    result = mapper.from_ods_fhir_to_fhir(ods_org, "GP Practice")

    assert result is not None
    assert result.extension is not None
    assert len(result.extension) == 1

    # Should extract the FIRST OrganisationRole (RO177)
    ext_dict = result.extension[0].dict()
    assert (
        ext_dict["url"]
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Verify it's the first role code
    role_code_ext = next(
        (e for e in ext_dict["extension"] if e["url"] == "roleCode"), None
    )
    assert role_code_ext is not None
    assert role_code_ext["valueCodeableConcept"]["coding"][0]["code"] == "RO177"

    # Verify the Legal TypedPeriod from the first role
    typed_period = next(
        (
            e
            for e in ext_dict["extension"]
            if e["url"]
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period is not None
    period = next((e for e in typed_period["extension"] if e["url"] == "period"), None)
    # First role's legal date should be extracted
    assert period["valuePeriod"]["start"] == "1974-04-01"


# --- Tests for refactored Extension-based legal period helpers ---


@pytest.fixture
def org_mapper() -> OrganizationMapper:
    return OrganizationMapper()


def make_typed_period_ext(
    date_type: str = "Legal", start: str = "2020-01-01", end: str = "2021-01-01"
) -> Extension:
    """Create a TypedPeriod Extension for testing."""
    return Extension.model_validate(
        {
            "url": TYPED_PERIOD_URL,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {
                        "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                        "code": date_type,
                        "display": date_type,
                    },
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": start, "end": end},
                },
            ],
        }
    )


def make_org_role_ext(typed_period: Extension) -> Extension:
    """Create an OrganisationRole Extension containing a TypedPeriod."""
    return Extension.model_validate(
        {
            "url": ORGANISATION_ROLE_URL,
            "extension": [typed_period.model_dump()],
        }
    )


def test_is_legal_typed_period_extension_legal(org_mapper: OrganizationMapper) -> None:
    """Test _is_legal_typed_period identifies Legal dateType correctly."""
    legal_ext = make_typed_period_ext("Legal")
    assert org_mapper._is_legal_typed_period(legal_ext) is True


def test_is_legal_typed_period_extension_non_legal(
    org_mapper: OrganizationMapper,
) -> None:
    """Test _is_legal_typed_period rejects non-Legal dateType."""
    operational_ext = make_typed_period_ext("Operational")
    assert org_mapper._is_legal_typed_period(operational_ext) is False


def test_find_legal_typed_period_extension_found(
    org_mapper: OrganizationMapper,
) -> None:
    """Test _find_legal_typed_period finds Legal TypedPeriod in OrganisationRole."""
    legal_period = make_typed_period_ext("Legal")
    org_role = make_org_role_ext(legal_period)
    found = org_mapper._find_legal_typed_period(org_role)
    assert found is not None
    assert found.url == TYPED_PERIOD_URL


def test_find_legal_typed_period_extension_not_found(
    org_mapper: OrganizationMapper,
) -> None:
    """Test _find_legal_typed_period returns None when no Legal TypedPeriod."""
    operational_period = make_typed_period_ext("Operational")
    org_role = make_org_role_ext(operational_period)
    found = org_mapper._find_legal_typed_period(org_role)
    assert found is None


def test_extract_first_organisation_role_with_legal_dates_extension_based(
    org_mapper: OrganizationMapper,
) -> None:
    """Test _extract_first_organisation_role extracts role with Legal TypedPeriod (Extension-based)."""
    legal_period = make_typed_period_ext("Legal", "2020-01-01", "2021-12-31")
    org_role = make_org_role_ext(legal_period)
    extensions = [org_role]

    result = org_mapper._extract_first_organisation_role(extensions)

    assert result is not None
    assert result["url"] == ORGANISATION_ROLE_URL
    assert len(result["extension"]) == 1
    typed_period = result["extension"][0]
    assert typed_period["url"] == TYPED_PERIOD_URL


def test_extract_first_organisation_role_no_legal_dates_extension_based(
    org_mapper: OrganizationMapper,
) -> None:
    """Test _extract_first_organisation_role returns OrganisationRole even when no Legal TypedPeriod (Extension-based)."""
    operational_period = make_typed_period_ext("Operational")
    org_role = make_org_role_ext(operational_period)
    extensions = [org_role]

    result = org_mapper._extract_first_organisation_role(extensions)
    assert result is not None
    assert result["url"] == ORGANISATION_ROLE_URL
    # Should contain the Operational TypedPeriod
    assert len(result["extension"]) == 1
    assert result["extension"][0]["url"] == TYPED_PERIOD_URL


def test_get_typed_period_extension_found(org_mapper: OrganizationMapper) -> None:
    """Test _get_typed_period_extension finds Legal TypedPeriod in OrganisationRole."""
    legal_period = make_typed_period_ext("Legal")
    org_role = make_org_role_ext(legal_period)
    extensions = [org_role]

    result = org_mapper._get_typed_period_extension(extensions)

    assert result is not None
    assert isinstance(result, Extension)
    assert result.url == TYPED_PERIOD_URL


def test_get_typed_period_extension_not_found(org_mapper: OrganizationMapper) -> None:
    """Test _get_typed_period_extension returns None when no Legal TypedPeriod."""
    operational_period = make_typed_period_ext("Operational")
    org_role = make_org_role_ext(operational_period)
    extensions = [org_role]

    result = org_mapper._get_typed_period_extension(extensions)
    assert result is None


def test_parse_legal_period_both_dates(org_mapper: OrganizationMapper) -> None:
    """Test _parse_legal_period extracts both start and end dates."""
    legal_ext = make_typed_period_ext("Legal", "2020-01-01", "2021-12-31")
    start, end = org_mapper._parse_legal_period(legal_ext)

    assert start == "2020-01-01"
    assert end == "2021-12-31"


def test_parse_legal_period_start_only(org_mapper: OrganizationMapper) -> None:
    """Test _parse_legal_period extracts start date when end is missing."""
    legal_ext = Extension.model_validate(
        {
            "url": TYPED_PERIOD_URL,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {"code": "Legal"},
                },
                {
                    "url": "period",
                    "valuePeriod": {"start": "2020-01-01"},
                },
            ],
        }
    )
    start, end = org_mapper._parse_legal_period(legal_ext)

    assert start == "2020-01-01"
    assert end is None


def test_parse_legal_period_no_period(org_mapper: OrganizationMapper) -> None:
    """Test _parse_legal_period returns None when no period sub-extension."""
    ext_no_period = Extension.model_validate(
        {
            "url": TYPED_PERIOD_URL,
            "extension": [
                {
                    "url": "dateType",
                    "valueCoding": {"code": "Legal"},
                },
            ],
        }
    )
    start, end = org_mapper._parse_legal_period(ext_no_period)

    assert start is None
    assert end is None


def test_parse_legal_period_none_extension(org_mapper: OrganizationMapper) -> None:
    """Test _parse_legal_period handles None input gracefully."""
    start, end = org_mapper._parse_legal_period(None)

    assert start is None
    assert end is None
