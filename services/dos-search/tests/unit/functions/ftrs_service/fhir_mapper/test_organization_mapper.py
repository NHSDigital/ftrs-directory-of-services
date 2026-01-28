import pytest
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

    def test_create_identifier(self, organization_mapper, organisation):
        # Act
        identifiers = organization_mapper._create_identifier(organisation)

        # Assert
        assert len(identifiers) == 1
        assert isinstance(identifiers[0], Identifier)
        assert identifiers[0].use == "official"
        assert identifiers[0].system == "https://fhir.nhs.uk/Id/ods-organization-code"
        assert identifiers[0].value == "123456"

    @pytest.mark.parametrize(
        ("org_name", "active"),
        [
            ("Test Org 1", True),
            ("Test Org 2", False),
            ("Default Name", True),
        ],
    )
    def test_map_to_organization_with_different_values(
        self, organization_mapper, create_organisation, org_name, active
    ):
        # Arrange
        updated_org_record = create_organisation(name=org_name, active=active)

        # Act
        org_resource = organization_mapper.map_to_fhir_organization(updated_org_record)

        # Assert
        assert org_resource.name == org_name
        assert org_resource.active == active
