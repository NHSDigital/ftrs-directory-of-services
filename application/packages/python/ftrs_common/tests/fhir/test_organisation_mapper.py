import uuid

import pytest
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
