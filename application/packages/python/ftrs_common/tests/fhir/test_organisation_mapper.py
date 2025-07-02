import uuid

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization, OrganizationContact
from ftrs_common.fhir.r4b.organisation_mapper import OrganizationMapper
from ftrs_data_layer.models import Organisation


def make_fhir_org(
    id: str = str(uuid.uuid4()),
    name: str = "Test Org",
    active: bool = True,
    contact: list | None = None,
    type: list | None = None,
) -> Organization:
    kwargs = {
        "id": id,
        "identifier": [Identifier.model_construct(value=id)],
        "name": name,
        "active": active,
        "type": type,
    }
    if contact is not None:
        if not isinstance(contact, list):
            contact = [contact]
        kwargs["contact"] = contact

    return Organization(**kwargs)


def test_from_fhir_maps_fields_correctly() -> None:
    mapper = OrganizationMapper()
    contact = OrganizationContact(telecom=[ContactPoint(system="phone", value="01234")])
    org_type = [CodeableConcept(text="GP Practice")]
    valid_uuid = str(uuid.uuid4())
    org = make_fhir_org(
        id=valid_uuid, name="Test Org", active=True, contact=contact, type=org_type
    )
    internal_organisation = mapper.from_fhir(org)
    assert isinstance(internal_organisation, Organisation)
    assert internal_organisation.identifier_ODS_ODSCode == valid_uuid
    assert internal_organisation.name == "Test Org"
    assert internal_organisation.active is True
    assert internal_organisation.telecom == "01234"
    assert internal_organisation.type == "GP Practice"
    assert internal_organisation.modifiedBy == "ODS_ETL_PIPELINE"


def test_from_fhir_handles_missing_contact() -> None:
    mapper = OrganizationMapper()
    org_type = [CodeableConcept(text="GP Practice")]
    org = make_fhir_org(
        id= str(uuid.uuid4()), name="Test Org", active=True, contact=None, type=org_type
    )
    internal_organisation = mapper.from_fhir(org)
    assert internal_organisation.telecom is None


def test_get_org_type() -> None:
    mapper = OrganizationMapper()
    org_type = [CodeableConcept(text="GP Practice")]
    org = make_fhir_org(
        id= str(uuid.uuid4()), name="Test Org", active=True, contact=None, type=org_type
    )
    assert mapper._get_org_type(org) == "GP Practice"


def test_get_org_type_type_no_text() -> None:
    mapper = OrganizationMapper()

    class DummyType:
        text = None

    class DummyOrg:
        type = [DummyType()]

    assert mapper._get_org_type(DummyOrg()) is None


def test_get_org_type_no_type() -> None:
    mapper = OrganizationMapper()
    org = make_fhir_org(
        id="ODS1", name="Test Org", active=True, contact=None, type=None
    )
    assert mapper._get_org_type(org) is None


def test_get_org_telecom_with_phone() -> None:
    mapper = OrganizationMapper()
    contact = OrganizationContact(telecom=[ContactPoint(system="phone", value="01234")])
    org = make_fhir_org(contact=contact)
    assert mapper._get_org_telecom(org) == "01234"


def test_get_org_telecom_none() -> None:
    mapper = OrganizationMapper()
    contact = []
    org = make_fhir_org(contact=contact)
    assert mapper._get_org_telecom(org) is None


def test_get_org_telecom_with_no_phone() -> None:
    mapper = OrganizationMapper()
    contact = OrganizationContact(
        telecom=[
            ContactPoint(system="email", value="test@example.com"),
            ContactPoint(system="fax", value="12345"),
        ]
    )
    org = make_fhir_org(contact=contact)
    assert mapper._get_org_telecom(org) is None


def test_get_role_display_from_extension_missing_role() -> None:
    mapper = OrganizationMapper()
    ext = {"extension": [{"url": "notrole", "valueCoding": {"display": "GP PRACTICE"}}]}
    assert mapper._get_role_display_from_extension(ext) is None


def test_get_role_display_from_extension_role_no_display() -> None:
    mapper = OrganizationMapper()
    ext = {"extension": [{"url": "role", "valueCoding": {}}]}
    assert mapper._get_role_display_from_extension(ext) is None


def test_get_role_display_from_extension_role_with_display() -> None:
    mapper = OrganizationMapper()
    ext = {"extension": [{"url": "role", "valueCoding": {"display": "Test Role"}}]}
    assert mapper._get_role_display_from_extension(ext) == "Test Role"


def test_get_role_display_from_extension_role_with_display_missing_value_coding() -> (
    None
):
    mapper = OrganizationMapper()
    ext = {"extension": [{"url": "role"}]}
    assert mapper._get_role_display_from_extension(ext) is None


def test_is_primary_role_false_when_no_primary_role() -> None:
    mapper = OrganizationMapper()
    ext = {"extension": [{"url": "role", "valueCoding": {"display": "GP PRACTICE"}}]}
    assert not mapper._is_primary_role(ext)


def test_is_primary_role_false_when_primary_role_false() -> None:
    mapper = OrganizationMapper()
    ext = {"extension": [{"url": "primaryRole", "valueBoolean": False}]}
    assert not mapper._is_primary_role(ext)


def test_extract_role_from_extension_no_matching_extension() -> None:
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


def test_extract_role_from_extension_no_primary_role() -> None:
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


def test_create_codable_concept_for_type_returns_list_of_dict() -> None:
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
            },
        ]
    }
    result = mapper._create_codable_concept_for_type(ods_org)
    assert isinstance(result, list)
    assert isinstance(result[0], CodeableConcept)
    assert result[0].coding[0].display == "GP PRACTICE"
    assert result[0].coding[0].code == "76"


def test_from_ods_fhir_to_fhir_validates_and_returns() -> None:
    mapper = OrganizationMapper()
    ods_fhir_organisation = {
        "resourceType": "Organization",
        "id": "C88037",
        "meta": {
            "lastUpdated": "2024-10-23T00:00:00+00:00",
            "profile": "https://fhir.nhs.uk/STU3/StructureDefinition/ODSAPI-Organization-1",
        },
        "active": True,
        "name": "Test Org",
        "telecom": [{"system": "phone", "value": "01234"}],
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "C88037",
        },
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
    expected_fhir_organisation = Organization(
        id="C88037",
        name="Test Org",
        active=True,
        contact=[OrganizationContact(
            telecom=[ContactPoint(system="phone", value="01234", use="work")]
        )],
        type=[
            CodeableConcept(
                coding=[
                    {
                        "system": "todo",
                        "code": "76",
                        "display": "GP PRACTICE",
                    }
                ]
            )
        ],
    )
    result = mapper.from_ods_fhir_to_fhir(ods_fhir_organisation)
    assert result.model_dump(
        exclude_none=True
    ) == expected_fhir_organisation.model_dump(exclude_none=True)


def test_find_phone_in_contact_returns_phone() -> None:
    mapper = OrganizationMapper()

    class DummyTelecom:
        system = "phone"
        value = "01234"

    class DummyContact:
        telecom = [DummyTelecom()]

    contact = DummyContact()
    assert mapper._find_phone_in_contact(contact) == "01234"


def test_find_phone_in_contact_returns_none_when_no_phone() -> None:
    mapper = OrganizationMapper()

    class DummyTelecom:
        system = "email"
        value = "test@example.com"

    class DummyContact:
        telecom = [DummyTelecom()]

    contact = DummyContact()
    assert mapper._find_phone_in_contact(contact) is None


def test_create_contact_point_from_internal() -> None:
    mapper = OrganizationMapper()
    cp = mapper._create_contact_point_from_internal("01234")
    assert isinstance(cp, ContactPoint)
    assert cp.system == "phone"
    assert cp.value == "01234"


def test_create_organization_contact_from_internal() -> None:
    mapper = OrganizationMapper()
    org_contact = mapper._create_organization_contact_from_internal("01234")
    assert isinstance(org_contact, OrganizationContact)
    assert org_contact.telecom[0].system == "phone"
    assert org_contact.telecom[0].value == "01234"


def test_create_identifier() -> None:
    mapper = OrganizationMapper()
    identifiers = mapper._create_identifier("ODS123")
    assert isinstance(identifiers, list)
    assert identifiers[0].system == "https://fhir.nhs.uk/Id/ods-organization-code"
    assert identifiers[0].value == "ODS123"


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
    assert isinstance(fhir_org, Organization)
    assert fhir_org.id == "123e4567-e89b-12d3-a456-42661417400a"
    assert fhir_org.name == "Test Org"
    assert fhir_org.active is True
    assert fhir_org.identifier[0].value == "ODS1"
    assert fhir_org.contact[0].telecom[0].system == "phone"
    assert fhir_org.contact[0].telecom[0].value == "01234"


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
    assert isinstance(fhir_org, Organization)
    assert fhir_org.id == "123e4567-e89b-12d3-a456-42661417400a"
    assert fhir_org.name == "Test Org 2"
    assert fhir_org.active is False
    assert fhir_org.identifier[0].value == "ODS2"
    assert fhir_org.contact is None


def test_create_organisation_contact_from_ods_only_phone() -> None:
    mapper = OrganizationMapper()
    telecom = [
        {"system": "phone", "value": "01234"},
        {"system": "email", "value": "test@example.com"},
    ]
    result = mapper._create_organisation_contact_from_ods(telecom)
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], OrganizationContact)
    assert result[0].telecom[0].system == "phone"
    assert result[0].telecom[0].value == "01234"
    assert result[0].telecom[0].use == "work"


def test_create_organisation_contact_from_ods_no_phone() -> None:
    mapper = OrganizationMapper()
    telecom = [
        {"system": "email", "value": "test@example.com"},
        {"system": "url", "value": "http://example.com"},
    ]
    result = mapper._create_organisation_contact_from_ods(telecom)
    assert result == []
