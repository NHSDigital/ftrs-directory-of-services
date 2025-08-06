from fhir.resources.R4B.address import Address
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization as FhirOrganization
from ftrs_data_layer.models import Organisation


class OrganizationMapper:
    def map_to_fhir_organization(self, organisation: Organisation) -> FhirOrganization:
        organization_id = str(organisation.id)
        name = organisation.name
        active = organisation.active
        identifier = self._create_identifier(organisation)
        telecom = self._create_telecom(organisation)
        address = self._create_dummy_address()

        fhir_organization = FhirOrganization.model_validate(
            {
                "id": organization_id,
                "identifier": identifier,
                "active": active,
                "name": name,
                "telecom": telecom,
                "address": address,
            }
        )

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

    def _create_telecom(self, organisation: Organisation) -> list[ContactPoint]:
        telecom = organisation.telecom

        if not telecom:
            return []

        telecom_entry = ContactPoint.model_validate(
            {
                "system": "phone",
                "value": telecom,
            }
        )

        return [telecom_entry]

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
