import pytest
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganization

from functions.ftrs_service.fhir_mapper.organization_mapper import OrganizationMapper


@pytest.fixture
def organization_mapper():
    return OrganizationMapper()


class TestOrganizationMapper:
    def test_map_to_organization_resource(self, organization_mapper, organisation):
        # Act
        org_resource = organization_mapper.map_to_fhir_organization(organisation)

        # Assert
        assert isinstance(org_resource, FhirOrganization)
        assert org_resource.id == str(organisation.id)
        assert org_resource.name == "Test Organisation"
        assert org_resource.active is True
        assert len(org_resource.identifier) == 1
        assert len(org_resource.telecom) == 1
        assert len(org_resource.address) == 1

    def test_create_identifier(self, organization_mapper, organisation):
        # Act
        identifiers = organization_mapper._create_identifier(organisation)

        # Assert
        assert len(identifiers) == 1
        assert isinstance(identifiers[0], Identifier)
        assert identifiers[0].use == "official"
        assert identifiers[0].system == "https://fhir.nhs.uk/Id/ods-organization-code"
        assert identifiers[0].value == "123456"

    def test_create_telecom(self, organization_mapper, organisation):
        # Act
        telecom = organization_mapper._create_telecom(organisation)

        # Assert
        assert len(telecom) == 1
        assert isinstance(telecom[0], ContactPoint)
        assert telecom[0].system == "phone"
        assert telecom[0].value == "123456789"

    def test_create_dummy_address(self, organization_mapper):
        # Act
        address = organization_mapper._create_dummy_address()

        # Assert
        assert len(address) == 1
        assert isinstance(address[0], Address)
        assert len(address[0].line) == 2
        assert address[0].line[0] == "Dummy Medical Practice"
        assert address[0].city == "Dummy City"
        assert address[0].postalCode == "DU00 0MY"
        assert address[0].country == "ENGLAND"

    @pytest.mark.parametrize(
        ("org_name", "telecom", "active"),
        [
            ("Test Org 1", "01234567890", True),
            ("Test Org 2", "09876543210", False),
            ("Default Name", "00000000000", True),
        ],
    )
    def test_map_to_organization_with_different_values(
        self, organization_mapper, create_organisation, org_name, telecom, active
    ):
        # Arrange
        updated_org_record = create_organisation(
            name=org_name, telecom=telecom, active=active
        )

        # Act
        org_resource = organization_mapper.map_to_fhir_organization(updated_org_record)

        # Assert
        assert org_resource.name == org_name
        assert org_resource.telecom[0].value == telecom
        assert org_resource.active == active
