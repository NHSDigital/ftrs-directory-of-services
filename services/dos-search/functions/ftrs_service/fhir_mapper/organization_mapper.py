from fhir.resources.R4B.address import Address
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganization
from ftrs_common.fhir.r4b.organisation_mapper import (
    OrganizationMapper as CommonOrganizationMapper,
)
from ftrs_data_layer.domain import Organisation


class OrganizationMapper:
    def map_to_fhir_organization(self, organisation: Organisation) -> FhirOrganization:
        fhir_organization = CommonOrganizationMapper().to_fhir(organisation)
        fhir_organization.address = self._create_dummy_address()
        return fhir_organization

    def _create_identifier(self, organisation: Organisation) -> list[Identifier]:
        identifier = Identifier.model_validate(
            {
                "use": "official",
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": organisation.identifier_ODS_ODSCode,
            }
        )

        return [identifier]

    def _create_dummy_address(self) -> list[Address]:
        address = Address.model_validate(
            {
                "line": ["Dummy Medical Practice", "Dummy Street"],
                "city": "Dummy City",
                "postalCode": "DU00 0MY",
                "country": "ENGLAND",
            }
        )

        return [address]
